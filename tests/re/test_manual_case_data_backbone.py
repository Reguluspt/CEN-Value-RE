"""E1-PR-001 acceptance tests for the manual Case / TSTĐ / TSSS data backbone."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from src.re.adapters.local_service import (
    AUTHORIZATION_HEADER,
    LAUNCH_ID_HEADER,
    LaunchSession,
    create_local_service_app,
)
from src.re.adapters.persistence import (
    EncryptedREPersistence,
    LATEST_SCHEMA_VERSION,
    PersistencePaths,
)
from src.re.adapters.persistence.migrations import MIGRATIONS, apply_migrations
from src.re.application.commands import (
    CharacteristicInput,
    CreateManualCase,
    EvidenceInput,
    LandParcelInput,
    LandValuationComponentInput,
    SaveComparable,
    SaveSubject,
)
from src.re.application.services import (
    ManualCaseConflictError,
    ManualCaseNotFoundError,
    ManualCasePersistenceError,
    ManualCaseService,
    UnsupportedProfileError,
)

SUPPORTED_PROFILE = ("cenvalue-re-n08-0038-v1", "1")


class MemoryKeyProtector:
    """Test protector that persists only opaque random wrapped blobs."""

    def __init__(self) -> None:
        self._values: dict[bytes, bytes] = {}

    def protect(self, plaintext: bytes) -> bytes:
        token = b"e1-wrapped:" + secrets.token_bytes(48)
        self._values[token] = bytes(plaintext)
        return token

    def unprotect(self, protected: bytes) -> bytes:
        return self._values[protected]


def _persistence(
    tmp_path: Path,
    *,
    legacy: Path | None = None,
) -> EncryptedREPersistence:
    return EncryptedREPersistence(
        PersistencePaths(tmp_path / "re-app-data"),
        MemoryKeyProtector(),
        legacy_cases_db=legacy,
    )


def _service(uow: object) -> ManualCaseService:
    return ManualCaseService(uow, supported_profiles={SUPPORTED_PROFILE})


def _create_case(service: ManualCaseService, code: str = "CV-E1-001"):
    return service.create_case(
        CreateManualCase(
            case_code=code,
            appraisal_date="2026-08-05",
            profile_id=SUPPORTED_PROFILE[0],
            profile_version=SUPPORTED_PROFILE[1],
            client_name="Manual Client",
            valuation_purpose="Collateral",
        )
    )


def _comparable(case_id: str, slot: int, *, property_id: str | None = None) -> SaveComparable:
    return SaveComparable(
        case_id=case_id,
        comparable_order=slot,
        property_id=property_id,
        legal_address=f"TSSS{slot} legal",
        current_address=f"TSSS{slot} current",
        completeness_status="COMPLETE",
        asking_or_sale_price_vnd=("21500000000.00", "88000000000", "38000000000")[slot - 1],
        negotiated_price_vnd=("18280000000.00", "74800000000", "32300000000")[slot - 1],
        negotiation_rate_pct="0.0000" if slot == 1 else None,
        characteristics=(
            CharacteristicInput(definition_key="area", decimal_value=f"{slot}.00"),
            CharacteristicInput(definition_key="frontage", decimal_value=f"{slot}.000"),
        ),
        evidence=(
            EvidenceInput(
                evidence_type="MANUAL_MARKET_NOTE",
                source_url=f"https://example.invalid/tsss-{slot}",
                note=f"manual evidence {slot}",
            ),
            EvidenceInput(
                evidence_type="MANUAL_MARKET_NOTE",
                source_url=f"https://example.invalid/tsss-{slot}-secondary",
                note=f"manual evidence {slot} secondary",
            ),
        ),
    )


def test_manual_case_subject_and_three_comparables_round_trip_exact_strings(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy" / "cases.db"
    legacy.parent.mkdir()
    legacy.write_bytes(b"legacy-sentinel-e1")
    legacy_before = hashlib.sha256(legacy.read_bytes()).hexdigest()

    persistence = _persistence(tmp_path, legacy=legacy)
    with persistence.open() as uow:
        assert uow.schema_version == LATEST_SCHEMA_VERSION
        assert LATEST_SCHEMA_VERSION >= 2
        service = _service(uow)
        created = _create_case(service)
        case_id = created.case.id
        assert created.case.appraisal_date == "2026-08-05"
        assert created.case.template_profile_id == SUPPORTED_PROFILE[0]
        assert created.case.template_profile_version == "1"

        subject = service.save_subject(
            SaveSubject(
                case_id=case_id,
                legal_address="Số 05 Nguyễn Văn Đậu",
                current_address="Số 05 Nguyễn Văn Đậu, phường Đức Nhuận",
                legal_review_status="MANUAL_REVIEWED",
                latitude="10.804423",
                longitude="106.686861",
                parcels=(
                    LandParcelInput(
                        parcel_number="24",
                        map_sheet_number="29/BĐĐC",
                        total_area_m2="103.20",
                        valuation_components=(
                            LandValuationComponentInput(
                                planning_status="COMPLIANT",
                                area_m2="82.9300",
                                valuation_basis="MARKET_INDICATED",
                                include_in_final_value=True,
                            ),
                            LandValuationComponentInput(
                                planning_status="NON_COMPLIANT",
                                area_m2="20.2700",
                                valuation_basis="OFFICIAL_LAND_PRICE",
                                include_in_final_value=True,
                                unit_price_vnd_per_m2="0.0000",
                            ),
                        ),
                    ),
                    LandParcelInput(
                        parcel_number="25",
                        map_sheet_number="29/BĐĐC",
                        total_area_m2="1.00",
                    ),
                ),
                characteristics=(
                    CharacteristicInput(definition_key="frontage", decimal_value="3.900"),
                    CharacteristicInput(definition_key="depth", decimal_value="27.3300"),
                    CharacteristicInput(definition_key="road_width", decimal_value="0.0000"),
                    CharacteristicInput(definition_key="shape", text_value="Tương đối vuông vức"),
                ),
            )
        )
        assert subject.subject is not None
        assert [item.parcel_number for item in subject.subject.parcels] == ["24", "25"]
        assert subject.subject.parcels[0].total_area_m2 == "103.20"
        assert [item.component_order for item in subject.subject.land_valuation_components] == [1, 2]
        assert subject.subject.land_valuation_components[0].area_m2 == "82.9300"
        assert subject.subject.land_valuation_components[1].unit_price_vnd_per_m2 == "0.0000"
        subject_chars = {
            item.definition_key: item for item in subject.subject.characteristics
        }
        assert subject_chars["frontage"].decimal_value == "3.900"
        assert subject_chars["road_width"].decimal_value == "0.0000"
        assert "location_quality" not in subject_chars

        for slot in (1, 2, 3):
            service.save_comparable(_comparable(case_id, slot))

        resumed = service.resume_case(case_id)
        assert [item.property.comparable_order for item in resumed.comparables] == [1, 2, 3]
        assert resumed.comparables[0].market_observation is not None
        assert resumed.comparables[0].market_observation.asking_or_sale_price_vnd == "21500000000.00"
        assert resumed.comparables[0].market_observation.negotiation_rate_pct == "0.0000"
        assert resumed.comparables[1].market_observation is not None
        assert resumed.comparables[1].market_observation.negotiation_rate_pct is None
        assert [item.evidence_order for item in resumed.comparables[0].evidence] == [1, 2]
        assert [item.note for item in resumed.comparables[0].evidence] == [
            "manual evidence 1",
            "manual evidence 1 secondary",
        ]
        before_close_json = resumed.to_json()

    assert hashlib.sha256(legacy.read_bytes()).hexdigest() == legacy_before

    with persistence.open() as reopened:
        resumed_again = _service(reopened).resume_case(case_id)
        assert resumed_again.to_json() == before_close_json


def test_required_date_supported_profile_and_binary_float_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="appraisal_date"):
        CreateManualCase(
            case_code="CV-INVALID",
            appraisal_date="",
            profile_id=SUPPORTED_PROFILE[0],
            profile_version="1",
        )
    with pytest.raises(TypeError, match="binary float"):
        CharacteristicInput(definition_key="area", decimal_value=1.25)
    with pytest.raises(TypeError, match="binary float"):
        SaveComparable(
            case_id="case",
            comparable_order=1,
            legal_address="A",
            current_address="B",
            completeness_status="COMPLETE",
            asking_or_sale_price_vnd=100.5,
            negotiated_price_vnd="100",
        )

    persistence = _persistence(tmp_path)
    with persistence.open() as uow:
        service = _service(uow)
        with pytest.raises(UnsupportedProfileError):
            service.create_case(
                CreateManualCase(
                    case_code="CV-UNSUPPORTED",
                    appraisal_date="2026-08-05",
                    profile_id="unknown-profile",
                    profile_version="1",
                )
            )


def test_comparable_identity_and_case_lineage_fail_closed(tmp_path: Path) -> None:
    persistence = _persistence(tmp_path)
    with persistence.open() as uow:
        service = _service(uow)
        case_one = _create_case(service, "CV-LINEAGE-1")
        case_two = _create_case(service, "CV-LINEAGE-2")
        saved = service.save_comparable(_comparable(case_one.case.id, 1))
        property_id = saved.comparables[0].property.property_id

        with pytest.raises(ManualCaseConflictError, match="another case"):
            service.save_comparable(_comparable(case_two.case.id, 1, property_id=property_id))

        with pytest.raises(ManualCaseConflictError, match="cannot be replaced"):
            service.save_comparable(
                _comparable(case_one.case.id, 1, property_id=str(uuid4()))
            )

        with pytest.raises(ValueError, match="UUID"):
            _comparable(case_one.case.id, 2, property_id="not-a-uuid")


def test_subject_bundle_write_is_atomic_on_nested_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    persistence = _persistence(tmp_path)
    with persistence.open() as uow:
        service = _service(uow)
        case = _create_case(service, "CV-ATOMIC")

        def fail_characteristic(_record) -> None:
            raise RuntimeError("deliberate nested write failure")

        monkeypatch.setattr(uow.property_characteristics, "put", fail_characteristic)
        with pytest.raises(ManualCasePersistenceError, match="atomically"):
            service.save_subject(
                SaveSubject(
                    case_id=case.case.id,
                    legal_address="Legal",
                    current_address="Current",
                    legal_review_status="REVIEWED",
                    characteristics=(
                        CharacteristicInput(
                            definition_key="area",
                            decimal_value="100.00",
                        ),
                    ),
                )
            )
        assert uow.subjects.get_for_case(case.case.id) is None
        assert uow.cases.get(case.case.id).active_subject_property_id is None


def test_archive_is_non_destructive_and_resume_hides_archived_case(tmp_path: Path) -> None:
    persistence = _persistence(tmp_path)
    with persistence.open() as uow:
        service = _service(uow)
        case = _create_case(service, "CV-ARCHIVE")
        archived_at = "2026-08-17T05:00:00Z"
        uow.cases.archive(case.case.id, archived_at)
        stored = uow.cases.get(case.case.id)
        assert stored is not None
        assert stored.archived_at == archived_at
        with pytest.raises(ManualCaseNotFoundError):
            service.resume_case(case.case.id)


def test_local_service_exercises_manual_use_case_without_direct_db_access(tmp_path: Path) -> None:
    persistence = _persistence(tmp_path)
    with persistence.open() as uow:
        service = _service(uow)
        session, credential = LaunchSession.issue()
        client = create_local_service_app(session, manual_cases=service).test_client()
        headers = {
            LAUNCH_ID_HEADER: credential.launch_id,
            AUTHORIZATION_HEADER: f"Bearer {credential.bearer_token}",
        }

        create_response = client.post(
            "/api/re/manual-cases",
            headers=headers,
            json={
                "case_code": "CV-HTTP",
                "appraisal_date": "2026-08-05",
                "profile_id": SUPPORTED_PROFILE[0],
                "profile_version": "1",
            },
        )
        assert create_response.status_code == 201
        case_id = create_response.get_json()["case"]["id"]

        subject_response = client.put(
            f"/api/re/manual-cases/{case_id}/subject",
            headers=headers,
            json={
                "legal_address": "Legal",
                "current_address": "Current",
                "legal_review_status": "REVIEWED",
                "characteristics": [
                    {"definition_key": "road_width", "decimal_value": "0.0000"}
                ],
            },
        )
        assert subject_response.status_code == 200

        for slot in (1, 2, 3):
            response = client.put(
                f"/api/re/manual-cases/{case_id}/comparables/{slot}",
                headers=headers,
                json={
                    "legal_address": f"L{slot}",
                    "current_address": f"C{slot}",
                    "completeness_status": "COMPLETE",
                    "asking_or_sale_price_vnd": "100.00",
                    "negotiated_price_vnd": "0.0000",
                },
            )
            assert response.status_code == 200

        resume = client.get(f"/api/re/manual-cases/{case_id}", headers=headers)
        assert resume.status_code == 200
        payload = resume.get_json()
        assert len(payload["comparables"]) == 3
        assert payload["subject"]["characteristics"][0]["decimal_value"] == "0.0000"

        anonymous = client.get(f"/api/re/manual-cases/{case_id}")
        assert anonymous.status_code == 401
        assert anonymous.get_json()["error"]["code"] == "RE_SESSION_REQUIRED"

        unsupported = client.post(
            "/api/re/manual-cases",
            headers=headers,
            json={
                "case_code": "CV-BAD-PROFILE",
                "appraisal_date": "2026-08-05",
                "profile_id": "unsupported",
                "profile_version": "1",
            },
        )
        assert unsupported.status_code == 400
        assert unsupported.get_json()["error"]["code"] == "RE_PROFILE_UNSUPPORTED"


def test_migration_v2_is_explicit_ordered_backbone_extension() -> None:
    assert [migration.version for migration in MIGRATIONS[:2]] == [1, 2]
    assert all(
        earlier.version < later.version
        for earlier, later in zip(MIGRATIONS, MIGRATIONS[1:])
    )
    assert LATEST_SCHEMA_VERSION >= 2
    migration = MIGRATIONS[1]
    assert migration.name == "epic1_manual_case_data_backbone"
    joined = "\n".join(migration.statements)
    for required in (
        "template_profile_id",
        "property_characteristic",
        "land_parcel",
        "parcel_order",
        "land_valuation_component",
        "component_order",
        "market_observation",
        "evidence",
        "evidence_order",
    ):
        assert required in joined


def test_migration_v2_rejects_comparable_case_lineage_mismatch() -> None:
    connection = sqlite3.connect(":memory:")
    apply_migrations(connection)
    connection.execute(
        "INSERT INTO appraisal_case(id,case_code,status,created_at,updated_at) VALUES (?,?,?,?,?)",
        ("case-a", "A", "IN_PROGRESS", "now", "now"),
    )
    connection.execute(
        "INSERT INTO appraisal_case(id,case_code,status,created_at,updated_at) VALUES (?,?,?,?,?)",
        ("case-b", "B", "IN_PROGRESS", "now", "now"),
    )
    connection.execute(
        """INSERT INTO property(id,case_id,role,legal_address,current_address,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?)""",
        ("comp-a", "case-a", "COMPARABLE", "L", "C", "now", "now"),
    )
    with pytest.raises(sqlite3.IntegrityError, match="lineage"):
        connection.execute(
            """INSERT INTO comparable_property(property_id,case_id,comparable_order,completeness_status)
            VALUES (?,?,?,?)""",
            ("comp-a", "case-b", 1, "COMPLETE"),
        )
