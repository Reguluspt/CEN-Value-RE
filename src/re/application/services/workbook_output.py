"""Application orchestration for supported-profile workbook generation."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, localcontext
from typing import Callable, Protocol

from ...ports.persistence import PropertyCharacteristicRecord
from ...ports.valuation_persistence import FinalValuationSnapshotRecord
from ...ports.workbook_output import (
    WorkbookGenerationArtifact,
    WorkbookGenerationSourceBinding,
    WorkbookOutputUnitOfWork,
    WorkbookOutputWriter,
)


class WorkbookOutputError(Exception):
    pass


class WorkbookOutputPrerequisiteError(WorkbookOutputError, ValueError):
    pass


class CurrentFinalValuationResolver(Protocol):
    def resolve_current(self, *, case_id: str) -> FinalValuationSnapshotRecord: ...


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _characteristic_value(record: PropertyCharacteristicRecord):
    supplied = [
        value
        for value in (
            record.decimal_value,
            record.text_value,
            record.code_value,
            record.bool_value,
            record.date_value,
        )
        if value is not None
    ]
    if len(supplied) != 1:
        raise WorkbookOutputPrerequisiteError(
            f"characteristic {record.definition_key} does not have exactly one value"
        )
    return supplied[0]


def _required_characteristic(records, key: str):
    matches = [
        item
        for item in records
        if item.archived_at is None and item.definition_key == key
    ]
    if len(matches) != 1:
        raise WorkbookOutputPrerequisiteError(
            f"required workbook characteristic {key!r} is missing or ambiguous"
        )
    return _characteristic_value(matches[0])


def _transaction_success_factor(asking: str, negotiated: str) -> str:
    asking_decimal = Decimal(asking)
    negotiated_decimal = Decimal(negotiated)
    if asking_decimal <= 0:
        raise WorkbookOutputPrerequisiteError(
            "comparable asking price must be positive for workbook normalization"
        )
    with localcontext() as context:
        context.prec = 50
        result = negotiated_decimal / asking_decimal
    if result <= 0:
        raise WorkbookOutputPrerequisiteError(
            "comparable transaction success factor must be positive"
        )
    return str(result.normalize())


class WorkbookOutputService:
    """Build a writer payload only from current accepted canonical evidence."""

    def __init__(
        self,
        uow: WorkbookOutputUnitOfWork,
        *,
        final_valuation: CurrentFinalValuationResolver,
        writer: WorkbookOutputWriter,
        now: Callable[[], str] = _utc_now,
    ) -> None:
        self._uow = uow
        self._final_valuation = final_valuation
        self._writer = writer
        self._now = now

    def generate(
        self,
        *,
        case_id: str,
        template_path: str,
        output_path: str,
    ) -> WorkbookGenerationArtifact:
        case = self._uow.cases.get(case_id)
        if case is None or case.archived_at is not None:
            raise WorkbookOutputPrerequisiteError("appraisal case is missing or archived")
        if not case.template_profile_id or not case.template_profile_version:
            raise WorkbookOutputPrerequisiteError(
                "case does not have a supported template profile binding"
            )

        try:
            final_snapshot = self._final_valuation.resolve_current(case_id=case_id)
        except Exception as exc:
            raise WorkbookOutputPrerequisiteError(
                "current final valuation evidence is required before workbook generation"
            ) from exc
        if final_snapshot.case_id != case_id:
            raise WorkbookOutputPrerequisiteError("final valuation case lineage mismatch")

        subject = self._uow.subjects.get_for_case(case_id)
        if subject is None or subject.archived_at is not None:
            raise WorkbookOutputPrerequisiteError("current subject property is required")
        if final_snapshot.subject_property_id != subject.property_id:
            raise WorkbookOutputPrerequisiteError(
                "final valuation does not bind the current subject property"
            )

        parcels = tuple(
            item
            for item in self._uow.land_parcels.list_for_property(subject.property_id)
            if item.archived_at is None
        )
        if len(parcels) != 1:
            raise WorkbookOutputPrerequisiteError(
                "N08 Walking Skeleton output requires exactly one current subject parcel"
            )
        parcel = parcels[0]

        components = tuple(
            item
            for item in self._uow.land_valuation_components.list_for_property(
                subject.property_id
            )
            if item.archived_at is None and item.include_in_final_value
        )
        compliant = [
            item
            for item in components
            if item.planning_status == "COMPLIANT"
            and item.valuation_basis == "MARKET_INDICATED"
        ]
        noncompliant = [
            item
            for item in components
            if item.planning_status == "NON_COMPLIANT"
            and item.valuation_basis in {"OFFICIAL_LAND_PRICE", "OTHER_MANUAL_BASIS"}
        ]
        if len(compliant) != 1 or len(noncompliant) != 1:
            raise WorkbookOutputPrerequisiteError(
                "N08 output requires one compliant and one noncompliant included land component"
            )
        if noncompliant[0].unit_price_vnd_per_m2 is None:
            raise WorkbookOutputPrerequisiteError(
                "noncompliant land unit price is required for workbook generation"
            )

        subject_characteristics = self._uow.property_characteristics.list_for_property(
            subject.property_id
        )
        values: dict[str, str | int | bool | None] = {
            "subject.current_address": subject.current_address,
            "subject.province": _required_characteristic(
                subject_characteristics, "address.current.province"
            ),
            "subject.latitude": subject.latitude,
            "subject.longitude": subject.longitude,
            "subject.parcel_number": parcel.parcel_number,
            "subject.map_sheet_number": parcel.map_sheet_number,
            "subject.noncompliant_unit_price": noncompliant[0].unit_price_vnd_per_m2,
            "subject.compliant_area_m2": compliant[0].area_m2,
            "subject.noncompliant_area_m2": noncompliant[0].area_m2,
            "subject.frontage": _required_characteristic(
                subject_characteristics, "frontage"
            ),
            "subject.depth": _required_characteristic(subject_characteristics, "depth"),
            "subject.shape": _required_characteristic(subject_characteristics, "shape"),
            "valuation.rounded_indicated_unit_price_vnd_per_m2": final_snapshot.rounded_indicated_unit_price_vnd_per_m2,
            "valuation.construction_value_total_vnd": final_snapshot.construction_value_total_vnd,
            "valuation.total_value_before_rounding_vnd": final_snapshot.total_value_before_rounding_vnd,
            "valuation.final_appraised_value_vnd": final_snapshot.final_appraised_value_vnd,
        }

        comparables = tuple(
            item
            for item in self._uow.comparables.list_for_case(case_id)
            if item.archived_at is None
        )
        comparables = tuple(sorted(comparables, key=lambda item: item.comparable_order))
        if tuple(item.comparable_order for item in comparables) != (1, 2, 3):
            raise WorkbookOutputPrerequisiteError(
                "workbook generation requires exactly current TSSS01, TSSS02 and TSSS03"
            )

        expected_factors = tuple(f"C{index}" for index in range(1, 12))
        for comparable in comparables:
            order = comparable.comparable_order
            observation = self._uow.market_observations.get_by_comparable(
                comparable.property_id
            )
            if observation is None or observation.archived_at is not None:
                raise WorkbookOutputPrerequisiteError(
                    f"TSSS{order:02d} current market observation is required"
                )
            characteristics = self._uow.property_characteristics.list_for_property(
                comparable.property_id
            )
            values.update(
                {
                    f"comparable.{order}.asking_price": observation.asking_or_sale_price_vnd,
                    f"comparable.{order}.negotiated_price": observation.negotiated_price_vnd,
                    f"comparable.{order}.transaction_success_factor": _transaction_success_factor(
                        observation.asking_or_sale_price_vnd,
                        observation.negotiated_price_vnd,
                    ),
                    f"comparable.{order}.area_m2": _required_characteristic(
                        characteristics, "area_m2"
                    ),
                    f"comparable.{order}.frontage": _required_characteristic(
                        characteristics, "frontage"
                    ),
                    f"comparable.{order}.depth": _required_characteristic(
                        characteristics, "depth"
                    ),
                    f"comparable.{order}.shape": _required_characteristic(
                        characteristics, "shape"
                    ),
                    f"comparable.{order}.building_area_m2": _required_characteristic(
                        characteristics, "building_area_m2"
                    ),
                    f"comparable.{order}.building_remaining_quality": _required_characteristic(
                        characteristics, "building_remaining_quality"
                    ),
                }
            )

            decisions = tuple(
                sorted(
                    self._uow.adjustment_decision_queries.list_for_comparable(
                        case_id, comparable.property_id
                    ),
                    key=lambda item: int(item.factor_key[1:]),
                )
            )
            if tuple(item.factor_key for item in decisions) != expected_factors:
                raise WorkbookOutputPrerequisiteError(
                    f"TSSS{order:02d} does not have a complete C1-C11 decision set"
                )
            for decision in decisions:
                if (
                    decision.archived_at is not None
                    or not decision.selected_explicitly
                    or decision.review_status != "CURRENT"
                    or decision.selected_rate_pct is None
                ):
                    raise WorkbookOutputPrerequisiteError(
                        f"{comparable.property_id}/{decision.factor_key} is not a current explicit human decision"
                    )
                values[
                    f"adjustment.{order}.{decision.factor_key}.selected_rate"
                ] = decision.selected_rate_pct

        return self._writer.generate(
            profile_id=case.template_profile_id,
            profile_version=case.template_profile_version,
            template_path=template_path,
            output_path=output_path,
            values=values,
            source_binding=WorkbookGenerationSourceBinding(
                case_id=case_id,
                final_valuation_snapshot_id=final_snapshot.id,
                final_valuation_semantic_sha256=final_snapshot.semantic_sha256,
            ),
            generated_at=self._now(),
        )
