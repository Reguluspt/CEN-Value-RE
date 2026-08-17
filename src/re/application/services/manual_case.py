"""Application orchestration for manual Case / TSTD / TSSS data."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable, Iterable
from uuid import uuid4

from ..commands.manual_case import CreateManualCase, SaveComparable, SaveSubject
from ..queries.manual_case import ComparableBundle, ManualCaseSnapshot, SubjectBundle
from ...ports.persistence import (
    CaseRecord,
    ComparablePropertyRecord,
    EvidenceRecord,
    LandParcelRecord,
    LandValuationComponentRecord,
    MarketObservationRecord,
    PersistenceUnitOfWork,
    PropertyCharacteristicRecord,
    SubjectPropertyRecord,
)


class ManualCaseError(Exception):
    """Base application error for the bounded manual-data capability."""


class ManualCaseValidationError(ManualCaseError, ValueError):
    pass


class ManualCaseNotFoundError(ManualCaseError, LookupError):
    pass


class ManualCaseConflictError(ManualCaseError):
    pass


class ManualCasePersistenceError(ManualCaseError):
    pass


class UnsupportedProfileError(ManualCaseValidationError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id() -> str:
    return str(uuid4())


class ManualCaseService:
    """Create, update and resume canonical manual appraisal data."""

    def __init__(
        self,
        uow: PersistenceUnitOfWork,
        *,
        supported_profiles: Iterable[tuple[str, str]],
        now: Callable[[], str] = _utc_now,
        new_id: Callable[[], str] = _new_id,
    ) -> None:
        self._uow = uow
        self._supported_profiles = frozenset(
            (str(profile_id).strip(), str(profile_version).strip())
            for profile_id, profile_version in supported_profiles
        )
        self._now = now
        self._new_id = new_id

    def create_case(self, command: CreateManualCase) -> ManualCaseSnapshot:
        profile = (command.profile_id, command.profile_version)
        if profile not in self._supported_profiles:
            raise UnsupportedProfileError(
                f"Unsupported template profile: {command.profile_id}@{command.profile_version}"
            )
        timestamp = self._now()
        record = CaseRecord(
            id=self._new_id(),
            case_code=command.case_code,
            status="IN_PROGRESS",
            created_at=timestamp,
            updated_at=timestamp,
            appraisal_date=command.appraisal_date,
            client_name=command.client_name,
            valuation_purpose=command.valuation_purpose,
            template_profile_id=command.profile_id,
            template_profile_version=command.profile_version,
        )
        try:
            with self._uow.atomic():
                self._uow.cases.put(record)
        except Exception as exc:
            raise ManualCasePersistenceError("Case could not be persisted") from exc
        return self.resume_case(record.id)

    def save_subject(self, command: SaveSubject) -> ManualCaseSnapshot:
        case = self._require_case(command.case_id)
        existing = self._uow.subjects.get_for_case(case.id)
        property_id = self._resolve_property_identity(
            case_id=case.id,
            explicit_property_id=command.property_id,
            existing_property_id=existing.property_id if existing else None,
            role="subject",
        )
        timestamp = self._now()
        created_at = existing.created_at if existing else timestamp
        subject = SubjectPropertyRecord(
            property_id=property_id,
            case_id=case.id,
            legal_address=command.legal_address,
            current_address=command.current_address,
            legal_review_status=command.legal_review_status,
            created_at=created_at,
            updated_at=timestamp,
            source_certificate_id=command.source_certificate_id,
            display_name=command.display_name,
            latitude=command.latitude,
            longitude=command.longitude,
            planning_note=command.planning_note,
            environment_note=command.environment_note,
            version=(existing.version + 1) if existing else 1,
            archived_at=None,
        )

        existing_parcels = list(self._uow.land_parcels.list_for_property(property_id))
        existing_characteristics = {
            item.definition_key: item
            for item in self._uow.property_characteristics.list_for_property(property_id)
            if item.archived_at is None
        }

        parcel_records: list[LandParcelRecord] = []
        component_records: list[LandValuationComponentRecord] = []
        for index, parcel in enumerate(command.parcels):
            existing_parcel = None
            if parcel.parcel_id:
                existing_parcel = next((item for item in existing_parcels if item.id == parcel.parcel_id), None)
                if existing_parcel is None:
                    raise ManualCaseConflictError("parcel_id does not belong to the subject property")
            elif index < len(existing_parcels):
                existing_parcel = existing_parcels[index]
            parcel_id = existing_parcel.id if existing_parcel else self._new_id()
            parcel_records.append(
                LandParcelRecord(
                    id=parcel_id,
                    property_id=property_id,
                    created_at=existing_parcel.created_at if existing_parcel else timestamp,
                    updated_at=timestamp,
                    parcel_number=parcel.parcel_number,
                    map_sheet_number=parcel.map_sheet_number,
                    total_area_m2=parcel.total_area_m2,
                    legal_address=parcel.legal_address,
                    current_address=parcel.current_address,
                    notes=parcel.notes,
                    archived_at=None,
                )
            )
            existing_components = [
                item
                for item in self._uow.land_valuation_components.list_for_property(property_id)
                if item.parcel_id == parcel_id and item.archived_at is None
            ]
            for component_index, component in enumerate(parcel.valuation_components):
                existing_component = None
                if component.component_id:
                    existing_component = next(
                        (item for item in existing_components if item.id == component.component_id),
                        None,
                    )
                    if existing_component is None:
                        raise ManualCaseConflictError(
                            "component_id does not belong to the selected parcel/property"
                        )
                elif component_index < len(existing_components):
                    existing_component = existing_components[component_index]
                component_records.append(
                    LandValuationComponentRecord(
                        id=existing_component.id if existing_component else self._new_id(),
                        property_id=property_id,
                        parcel_id=parcel_id,
                        planning_status=component.planning_status,
                        area_m2=component.area_m2,
                        valuation_basis=component.valuation_basis,
                        include_in_final_value=component.include_in_final_value,
                        created_at=existing_component.created_at if existing_component else timestamp,
                        updated_at=timestamp,
                        unit_price_vnd_per_m2=component.unit_price_vnd_per_m2,
                        note=component.note,
                        policy_version=component.policy_version,
                        archived_at=None,
                    )
                )

        characteristic_records = self._characteristic_records(
            property_id=property_id,
            inputs=command.characteristics,
            existing=existing_characteristics,
            timestamp=timestamp,
        )

        updated_case = replace(
            case,
            active_subject_property_id=property_id,
            updated_at=timestamp,
            version=case.version + 1,
        )

        try:
            with self._uow.atomic():
                self._uow.subjects.put(subject)
                for record in parcel_records:
                    self._uow.land_parcels.put(record)
                for record in component_records:
                    self._uow.land_valuation_components.put(record)
                for record in characteristic_records:
                    self._uow.property_characteristics.put(record)
                self._uow.cases.put(updated_case)
        except Exception as exc:
            raise ManualCasePersistenceError("Subject data could not be saved atomically") from exc
        return self.resume_case(case.id)

    def save_comparable(self, command: SaveComparable) -> ManualCaseSnapshot:
        case = self._require_case(command.case_id)
        existing = self._uow.comparables.get_by_case_order(case.id, command.comparable_order)
        property_id = self._resolve_property_identity(
            case_id=case.id,
            explicit_property_id=command.property_id,
            existing_property_id=existing.property_id if existing else None,
            role=f"comparable slot {command.comparable_order}",
        )
        timestamp = self._now()
        created_at = existing.created_at if existing else timestamp

        existing_observation = self._uow.market_observations.get_by_comparable(property_id)
        if command.market_observation_id and (
            existing_observation is None or existing_observation.id != command.market_observation_id
        ):
            raise ManualCaseConflictError(
                "market_observation_id does not belong to this comparable"
            )
        observation_id = (
            command.market_observation_id
            or (existing_observation.id if existing_observation else None)
            or self._new_id()
        )

        comparable = ComparablePropertyRecord(
            property_id=property_id,
            case_id=case.id,
            legal_address=command.legal_address,
            current_address=command.current_address,
            comparable_order=command.comparable_order,
            completeness_status=command.completeness_status,
            created_at=created_at,
            updated_at=timestamp,
            market_observation_id=observation_id,
            display_name=command.display_name or f"TSSS{command.comparable_order:02d}",
            latitude=command.latitude,
            longitude=command.longitude,
            planning_note=command.planning_note,
            environment_note=command.environment_note,
            version=(existing.version + 1) if existing else 1,
            archived_at=None,
        )
        observation = MarketObservationRecord(
            id=observation_id,
            comparable_property_id=property_id,
            asking_or_sale_price_vnd=command.asking_or_sale_price_vnd,
            negotiated_price_vnd=command.negotiated_price_vnd,
            created_at=existing_observation.created_at if existing_observation else timestamp,
            updated_at=timestamp,
            negotiation_rate_pct=command.negotiation_rate_pct,
            observation_date=command.observation_date,
            note=command.observation_note,
            archived_at=None,
        )
        existing_characteristics = {
            item.definition_key: item
            for item in self._uow.property_characteristics.list_for_property(property_id)
            if item.archived_at is None
        }
        characteristic_records = self._characteristic_records(
            property_id=property_id,
            inputs=command.characteristics,
            existing=existing_characteristics,
            timestamp=timestamp,
        )
        existing_evidence = list(self._uow.evidence.list_for_property(property_id))
        evidence_records: list[EvidenceRecord] = []
        for index, item in enumerate(command.evidence):
            existing_item = None
            if item.evidence_id:
                existing_item = next((row for row in existing_evidence if row.id == item.evidence_id), None)
                if existing_item is None:
                    raise ManualCaseConflictError("evidence_id does not belong to this comparable")
            elif index < len(existing_evidence):
                existing_item = existing_evidence[index]
            evidence_records.append(
                EvidenceRecord(
                    id=existing_item.id if existing_item else self._new_id(),
                    property_id=property_id,
                    market_observation_id=observation_id,
                    created_at=existing_item.created_at if existing_item else timestamp,
                    updated_at=timestamp,
                    evidence_type=item.evidence_type,
                    source_url=item.source_url,
                    note=item.note,
                    archived_at=None,
                )
            )

        try:
            with self._uow.atomic():
                self._uow.comparables.put(comparable)
                self._uow.market_observations.put(observation)
                for record in characteristic_records:
                    self._uow.property_characteristics.put(record)
                for record in evidence_records:
                    self._uow.evidence.put(record)
        except Exception as exc:
            raise ManualCasePersistenceError("Comparable data could not be saved atomically") from exc
        return self.resume_case(case.id)

    def resume_case(self, case_id: str) -> ManualCaseSnapshot:
        case = self._require_case(case_id)
        subject_record = self._uow.subjects.get_for_case(case.id)
        subject = None
        if subject_record is not None:
            subject = SubjectBundle(
                property=subject_record,
                parcels=tuple(
                    item
                    for item in self._uow.land_parcels.list_for_property(subject_record.property_id)
                    if item.archived_at is None
                ),
                land_valuation_components=tuple(
                    item
                    for item in self._uow.land_valuation_components.list_for_property(subject_record.property_id)
                    if item.archived_at is None
                ),
                characteristics=tuple(
                    item
                    for item in self._uow.property_characteristics.list_for_property(subject_record.property_id)
                    if item.archived_at is None
                ),
            )
        comparables = []
        for record in self._uow.comparables.list_for_case(case.id):
            if record.archived_at is not None:
                continue
            comparables.append(
                ComparableBundle(
                    property=record,
                    market_observation=self._uow.market_observations.get_by_comparable(record.property_id),
                    characteristics=tuple(
                        item
                        for item in self._uow.property_characteristics.list_for_property(record.property_id)
                        if item.archived_at is None
                    ),
                    evidence=tuple(
                        item
                        for item in self._uow.evidence.list_for_property(record.property_id)
                        if item.archived_at is None
                    ),
                )
            )
        comparables.sort(key=lambda item: item.property.comparable_order)
        return ManualCaseSnapshot(case=case, subject=subject, comparables=tuple(comparables))

    def _require_case(self, case_id: str) -> CaseRecord:
        case = self._uow.cases.get(case_id)
        if case is None or case.archived_at is not None:
            raise ManualCaseNotFoundError(f"Manual case not found: {case_id}")
        return case

    def _resolve_property_identity(
        self,
        *,
        case_id: str,
        explicit_property_id: str | None,
        existing_property_id: str | None,
        role: str,
    ) -> str:
        if existing_property_id is not None:
            if explicit_property_id is not None and explicit_property_id != existing_property_id:
                raise ManualCaseConflictError(f"{role} identity cannot be replaced")
            return existing_property_id
        if explicit_property_id:
            subject = self._uow.subjects.get(explicit_property_id)
            comparable = self._uow.comparables.get(explicit_property_id)
            found = subject or comparable
            if found is not None:
                if found.case_id != case_id:
                    raise ManualCaseConflictError(f"{role} identity belongs to another case")
                raise ManualCaseConflictError(
                    f"{role} identity is already assigned to a different role or slot"
                )
            return explicit_property_id
        return self._new_id()

    def _characteristic_records(
        self,
        *,
        property_id: str,
        inputs,
        existing: dict[str, PropertyCharacteristicRecord],
        timestamp: str,
    ) -> tuple[PropertyCharacteristicRecord, ...]:
        output = []
        for item in inputs:
            previous = existing.get(item.definition_key)
            if item.characteristic_id and (
                previous is None or previous.id != item.characteristic_id
            ):
                raise ManualCaseConflictError(
                    f"characteristic_id does not match property definition {item.definition_key}"
                )
            output.append(
                PropertyCharacteristicRecord(
                    id=item.characteristic_id or (previous.id if previous else self._new_id()),
                    property_id=property_id,
                    definition_key=item.definition_key,
                    source_status=item.source_status,
                    verified_by_user=item.verified_by_user,
                    updated_at=timestamp,
                    decimal_value=item.decimal_value,
                    text_value=item.text_value,
                    code_value=item.code_value,
                    bool_value=item.bool_value,
                    date_value=item.date_value,
                    provenance_id=item.provenance_id,
                    archived_at=None,
                )
            )
        return tuple(output)
