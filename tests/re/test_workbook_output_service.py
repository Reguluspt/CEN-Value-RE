from dataclasses import replace

import pytest

from src.re.application.services.workbook_output import (
    WorkbookOutputPrerequisiteError,
    WorkbookOutputService,
)
from src.re.ports.persistence import (
    AdjustmentDecisionRecord,
    CaseRecord,
    ComparablePropertyRecord,
    LandParcelRecord,
    LandValuationComponentRecord,
    MarketObservationRecord,
    PropertyCharacteristicRecord,
    SubjectPropertyRecord,
)
from src.re.ports.valuation_persistence import FinalValuationSnapshotRecord
from src.re.ports.workbook_output import WorkbookGenerationArtifact


class _ById:
    def __init__(self, records):
        self.records = {item.id: item for item in records}

    def get(self, record_id):
        return self.records.get(record_id)


class _Subjects:
    def __init__(self, record):
        self.record = record

    def get_for_case(self, case_id):
        return self.record if self.record.case_id == case_id else None


class _Comparables:
    def __init__(self, records):
        self.records = tuple(records)

    def list_for_case(self, case_id):
        return tuple(item for item in self.records if item.case_id == case_id)


class _Parcels:
    def __init__(self, records):
        self.records = tuple(records)

    def list_for_property(self, property_id):
        return tuple(item for item in self.records if item.property_id == property_id)


class _Components(_Parcels):
    pass


class _Characteristics:
    def __init__(self, records):
        self.records = list(records)

    def list_for_property(self, property_id):
        return tuple(item for item in self.records if item.property_id == property_id)


class _Observations:
    def __init__(self, records):
        self.records = {item.comparable_property_id: item for item in records}

    def get_by_comparable(self, comparable_property_id):
        return self.records.get(comparable_property_id)


class _DecisionQueries:
    def __init__(self, records):
        self.records = list(records)

    def list_for_comparable(self, case_id, comparable_property_id):
        return tuple(
            item
            for item in self.records
            if item.case_id == case_id
            and item.comparable_property_id == comparable_property_id
        )


class _FinalResolver:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def resolve_current(self, *, case_id):
        assert case_id == self.snapshot.case_id
        return self.snapshot


class _Writer:
    def __init__(self):
        self.call = None

    def generate(self, **kwargs):
        self.call = kwargs
        return WorkbookGenerationArtifact(
            profile_id=kwargs["profile_id"],
            profile_version=kwargs["profile_version"],
            template_path=kwargs["template_path"],
            output_path=kwargs["output_path"],
            source_sha256="1" * 64,
            output_sha256="2" * 64,
            source_binding=kwargs["source_binding"],
            generated_at=kwargs["generated_at"],
            changed_cells=("Nhập liệu!F7",),
            applied_transformations=("localize-stale-phieu-tttt-e5",),
        )


class _Uow:
    pass


def _char(record_id, property_id, key, *, decimal=None, text=None):
    return PropertyCharacteristicRecord(
        id=record_id,
        property_id=property_id,
        definition_key=key,
        source_status="MANUAL",
        verified_by_user=True,
        updated_at="t",
        decimal_value=decimal,
        text_value=text,
    )


def _fixture():
    case = CaseRecord(
        id="case-1",
        case_code="CV-E1-005",
        status="IN_PROGRESS",
        created_at="t",
        updated_at="t",
        appraisal_date="2026-08-05",
        template_profile_id="cenvalue-re-n08-0038-v1",
        template_profile_version="1",
    )
    subject = SubjectPropertyRecord(
        property_id="subject-1",
        case_id="case-1",
        legal_address="legal",
        current_address="Số 05 Nguyễn Văn Đậu",
        legal_review_status="REVIEWED",
        created_at="t",
        updated_at="t",
        latitude="10.804423",
        longitude="106.686861",
    )
    parcel = LandParcelRecord(
        id="parcel-1",
        property_id="subject-1",
        parcel_order=1,
        created_at="t",
        updated_at="t",
        parcel_number="24",
        map_sheet_number="29/BĐĐC",
        total_area_m2="103.2",
    )
    components = (
        LandValuationComponentRecord(
            id="land-1",
            property_id="subject-1",
            component_order=1,
            planning_status="COMPLIANT",
            area_m2="82.93",
            valuation_basis="MARKET_INDICATED",
            include_in_final_value=True,
            created_at="t",
            updated_at="t",
        ),
        LandValuationComponentRecord(
            id="land-2",
            property_id="subject-1",
            component_order=2,
            planning_status="NON_COMPLIANT",
            area_m2="20.27",
            valuation_basis="OFFICIAL_LAND_PRICE",
            include_in_final_value=True,
            created_at="t",
            updated_at="t",
            unit_price_vnd_per_m2="106000000",
            policy_version="N08:I31",
        ),
    )
    comparables = tuple(
        ComparablePropertyRecord(
            property_id=f"comp-{index}",
            case_id="case-1",
            legal_address=f"comp-{index}",
            current_address=f"comp-{index}",
            comparable_order=index,
            completeness_status="COMPLETE",
            created_at="t",
            updated_at="t",
        )
        for index in range(1, 4)
    )
    asking = ("21500000000", "88000000000", "38000000000")
    negotiated = ("18275000000", "74800000000", "32300000000")
    observations = tuple(
        MarketObservationRecord(
            id=f"obs-{index}",
            comparable_property_id=f"comp-{index}",
            asking_or_sale_price_vnd=asking[index - 1],
            negotiated_price_vnd=negotiated[index - 1],
            created_at="t",
            updated_at="t",
        )
        for index in range(1, 4)
    )
    characteristics = [
        _char("s-province", "subject-1", "address.current.province", text="Tp. HCM"),
        _char("s-frontage", "subject-1", "frontage", decimal="3.9"),
        _char("s-depth", "subject-1", "depth", decimal="27.33"),
        _char("s-shape", "subject-1", "shape", text="Tương đối vuông vức"),
    ]
    comparable_data = (
        ("68.3", "3.55", "19.35", "Tương đối vuông vức", "327.59", "0.75"),
        ("299", "15", "20", "Không vuông vức", "569", "0.8"),
        ("149", "6.1", "25.5", "Không vuông vức", "420", "0.75"),
    )
    for index, data in enumerate(comparable_data, 1):
        property_id = f"comp-{index}"
        for suffix, key, value, is_text in (
            ("area", "area_m2", data[0], False),
            ("frontage", "frontage", data[1], False),
            ("depth", "depth", data[2], False),
            ("shape", "shape", data[3], True),
            ("building-area", "building_area_m2", data[4], False),
            ("quality", "building_remaining_quality", data[5], False),
        ):
            characteristics.append(
                _char(
                    f"{property_id}-{suffix}",
                    property_id,
                    key,
                    text=value if is_text else None,
                    decimal=None if is_text else value,
                )
            )

    decisions = []
    for order in range(1, 4):
        for factor in range(1, 12):
            decisions.append(
                AdjustmentDecisionRecord(
                    id=f"d-{order}-{factor}",
                    case_id="case-1",
                    comparable_property_id=f"comp-{order}",
                    factor_key=f"C{factor}",
                    selected_explicitly=True,
                    source_data_revision="rev-1",
                    review_status="CURRENT",
                    selected_rate_pct="0" if factor != 4 else "-0.10",
                    selected_at="t",
                )
            )

    final = FinalValuationSnapshotRecord(
        id="final-1",
        case_id="case-1",
        subject_property_id="subject-1",
        appraisal_date="2026-08-05",
        human_indication_snapshot_id="human-1",
        human_indication_semantic_sha256="b" * 64,
        rounded_indicated_unit_price_vnd_per_m2="196308000",
        land_components_json="[]",
        land_components_sha256="c" * 64,
        compliant_residential_land_value_vnd="16279822440",
        other_recognized_land_value_vnd="2148620000",
        recognized_land_value_vnd="18428442440",
        construction_aggregate_input_id="construction-1",
        construction_aggregate_semantic_sha256="d" * 64,
        construction_value_total_vnd="1152970000",
        total_value_before_rounding_vnd="19581412440",
        final_appraised_value_vnd="19581000000",
        rounding_target="TOTAL_VALUE",
        rounding_mode="NEAREST",
        rounding_increment_vnd=1_000_000,
        rounding_source="TEMPLATE_DEFAULT",
        rounding_profile_id="cenvalue-re-n08-0038-v1",
        rounding_profile_version="1",
        rounding_selected_by=None,
        rounding_selected_at=None,
        composed_at="t",
        semantic_sha256="e" * 64,
    )

    uow = _Uow()
    uow.cases = _ById((case,))
    uow.subjects = _Subjects(subject)
    uow.comparables = _Comparables(comparables)
    uow.land_parcels = _Parcels((parcel,))
    uow.land_valuation_components = _Components(components)
    uow.property_characteristics = _Characteristics(characteristics)
    uow.market_observations = _Observations(observations)
    uow.adjustment_decision_queries = _DecisionQueries(decisions)
    return uow, final


def test_service_builds_writer_payload_only_from_current_canonical_state():
    uow, final = _fixture()
    writer = _Writer()
    service = WorkbookOutputService(
        uow,
        final_valuation=_FinalResolver(final),
        writer=writer,
        now=lambda: "2026-08-18T08:00:00Z",
    )
    artifact = service.generate(
        case_id="case-1",
        template_path="C:/external/n08.xlsx",
        output_path="C:/output/generated.xlsx",
    )

    values = writer.call["values"]
    assert writer.call["profile_id"] == "cenvalue-re-n08-0038-v1"
    assert writer.call["profile_version"] == "1"
    assert writer.call["source_binding"].final_valuation_snapshot_id == "final-1"
    assert writer.call["source_binding"].final_valuation_semantic_sha256 == "e" * 64
    assert values["subject.compliant_area_m2"] == "82.93"
    assert values["subject.noncompliant_area_m2"] == "20.27"
    assert values["subject.noncompliant_unit_price"] == "106000000"
    assert values["comparable.1.transaction_success_factor"] == "0.85"
    assert values["adjustment.1.C1.selected_rate"] == "0"
    assert values["adjustment.1.C4.selected_rate"] == "-0.10"
    assert values["valuation.total_value_before_rounding_vnd"] == "19581412440"
    assert values["valuation.final_appraised_value_vnd"] == "19581000000"
    assert artifact.excel_qualification_status == "NOT_RUN"


def test_service_fails_closed_for_missing_required_canonical_mapping():
    uow, final = _fixture()
    uow.property_characteristics.records = [
        item
        for item in uow.property_characteristics.records
        if not (item.property_id == "subject-1" and item.definition_key == "frontage")
    ]
    service = WorkbookOutputService(
        uow,
        final_valuation=_FinalResolver(final),
        writer=_Writer(),
    )
    with pytest.raises(WorkbookOutputPrerequisiteError, match="frontage"):
        service.generate(
            case_id="case-1",
            template_path="template.xlsx",
            output_path="output.xlsx",
        )


def test_service_fails_closed_when_any_adjustment_decision_is_stale():
    uow, final = _fixture()
    original = uow.adjustment_decision_queries.records[0]
    uow.adjustment_decision_queries.records[0] = replace(
        original, review_status="SOURCE_DATA_CHANGED"
    )
    service = WorkbookOutputService(
        uow,
        final_valuation=_FinalResolver(final),
        writer=_Writer(),
    )
    with pytest.raises(WorkbookOutputPrerequisiteError, match="not a current explicit human decision"):
        service.generate(
            case_id="case-1",
            template_path="template.xlsx",
            output_path="output.xlsx",
        )
