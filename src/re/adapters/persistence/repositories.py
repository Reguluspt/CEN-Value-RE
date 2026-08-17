"""SQLCipher repository implementations for CenValue RE."""

from __future__ import annotations

from dataclasses import asdict

from ...ports.persistence import (
    AdjustmentDecisionRecord,
    ApprovalSubmissionRecord,
    CaseRecord,
    ComparablePropertyRecord,
    ConstructionAssetRecord,
    EvidenceRecord,
    LandParcelRecord,
    LandValuationComponentRecord,
    MarketObservationRecord,
    PropertyCharacteristicRecord,
    SubjectPropertyRecord,
)


def _commit(connection, statements: tuple[tuple[str, tuple[object, ...]], ...]) -> None:
    outer_transaction = bool(getattr(connection, "in_transaction", False))
    try:
        for sql, params in statements:
            connection.execute(sql, params)
        if not outer_transaction:
            connection.commit()
    except Exception:
        if not outer_transaction:
            connection.rollback()
        raise


def _bool(value: object) -> bool:
    return bool(int(value))


def _optional_bool(value: object | None) -> bool | None:
    if value is None:
        return None
    return _bool(value)


class SQLCipherCaseRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: CaseRecord) -> None:
        values = asdict(record)
        values["include_in_historical_learning"] = int(record.include_in_historical_learning)
        columns = tuple(values)
        sql = (
            f"INSERT INTO appraisal_case ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get(self, record_id: str) -> CaseRecord | None:
        row = self._connection.execute(
            "SELECT * FROM appraisal_case WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            return None
        row["include_in_historical_learning"] = _bool(row["include_in_historical_learning"])
        return CaseRecord(**row)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE appraisal_case SET archived_at = ?, updated_at = ? WHERE id = ?", (archived_at, archived_at, record_id)),),
        )


_PROPERTY_COLUMNS = (
    "id",
    "case_id",
    "role",
    "display_name",
    "legal_address",
    "current_address",
    "latitude",
    "longitude",
    "planning_note",
    "environment_note",
    "created_at",
    "updated_at",
    "version",
    "archived_at",
)


def _property_params(record, role: str) -> tuple[object, ...]:
    return (
        record.property_id,
        record.case_id,
        role,
        record.display_name,
        record.legal_address,
        record.current_address,
        record.latitude,
        record.longitude,
        record.planning_note,
        record.environment_note,
        record.created_at,
        record.updated_at,
        record.version,
        record.archived_at,
    )


_PROPERTY_UPSERT = f"""INSERT INTO property({','.join(_PROPERTY_COLUMNS)})
VALUES ({','.join('?' for _ in _PROPERTY_COLUMNS)})
ON CONFLICT(id) DO UPDATE SET
case_id=excluded.case_id,role=excluded.role,display_name=excluded.display_name,
legal_address=excluded.legal_address,current_address=excluded.current_address,
latitude=excluded.latitude,longitude=excluded.longitude,
planning_note=excluded.planning_note,environment_note=excluded.environment_note,
updated_at=excluded.updated_at,version=excluded.version,archived_at=excluded.archived_at"""


class SQLCipherSubjectPropertyRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: SubjectPropertyRecord) -> None:
        _commit(
            self._connection,
            (
                (_PROPERTY_UPSERT, _property_params(record, "SUBJECT")),
                (
                    """INSERT INTO subject_property(property_id,legal_review_status,source_certificate_id) VALUES (?,?,?)
                    ON CONFLICT(property_id) DO UPDATE SET legal_review_status=excluded.legal_review_status,
                    source_certificate_id=excluded.source_certificate_id""",
                    (record.property_id, record.legal_review_status, record.source_certificate_id),
                ),
            ),
        )

    def _select(self, where: str, params: tuple[object, ...]):
        return self._connection.execute(
            f"""SELECT p.id AS property_id,p.case_id,p.legal_address,p.current_address,s.legal_review_status,
            p.created_at,p.updated_at,s.source_certificate_id,p.display_name,p.latitude,p.longitude,
            p.planning_note,p.environment_note,p.version,p.archived_at
            FROM property p JOIN subject_property s ON s.property_id=p.id
            WHERE p.role='SUBJECT' AND {where}""",
            params,
        ).fetchone()

    def get(self, property_id: str) -> SubjectPropertyRecord | None:
        row = self._select("p.id=?", (property_id,))
        return SubjectPropertyRecord(**row) if row else None

    def get_for_case(self, case_id: str) -> SubjectPropertyRecord | None:
        row = self._select("p.case_id=? AND p.archived_at IS NULL ORDER BY p.created_at LIMIT 1", (case_id,))
        return SubjectPropertyRecord(**row) if row else None

    def archive(self, property_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE property SET archived_at=?, updated_at=? WHERE id=? AND role='SUBJECT'", (archived_at, archived_at, property_id)),),
        )


class SQLCipherComparablePropertyRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: ComparablePropertyRecord) -> None:
        _commit(
            self._connection,
            (
                (_PROPERTY_UPSERT, _property_params(record, "COMPARABLE")),
                (
                    """INSERT INTO comparable_property(property_id,case_id,comparable_order,market_observation_id,completeness_status)
                    VALUES (?,?,?,?,?) ON CONFLICT(property_id) DO UPDATE SET case_id=excluded.case_id,
                    comparable_order=excluded.comparable_order,market_observation_id=excluded.market_observation_id,
                    completeness_status=excluded.completeness_status""",
                    (
                        record.property_id,
                        record.case_id,
                        record.comparable_order,
                        record.market_observation_id,
                        record.completeness_status,
                    ),
                ),
            ),
        )

    def _select(self, where: str, params: tuple[object, ...]):
        return self._connection.execute(
            f"""SELECT p.id AS property_id,p.case_id,p.legal_address,p.current_address,c.comparable_order,c.completeness_status,
            p.created_at,p.updated_at,c.market_observation_id,p.display_name,p.latitude,p.longitude,
            p.planning_note,p.environment_note,p.version,p.archived_at
            FROM property p JOIN comparable_property c ON c.property_id=p.id
            WHERE p.role='COMPARABLE' AND {where}""",
            params,
        )

    def get(self, property_id: str) -> ComparablePropertyRecord | None:
        row = self._select("p.id=?", (property_id,)).fetchone()
        return ComparablePropertyRecord(**row) if row else None

    def get_by_case_order(self, case_id: str, comparable_order: int) -> ComparablePropertyRecord | None:
        row = self._select(
            "p.case_id=? AND c.comparable_order=? AND p.archived_at IS NULL",
            (case_id, comparable_order),
        ).fetchone()
        return ComparablePropertyRecord(**row) if row else None

    def list_for_case(self, case_id: str) -> tuple[ComparablePropertyRecord, ...]:
        rows = self._select("p.case_id=? ORDER BY c.comparable_order,p.id", (case_id,)).fetchall()
        return tuple(ComparablePropertyRecord(**row) for row in rows)

    def archive(self, property_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE property SET archived_at=?, updated_at=? WHERE id=? AND role='COMPARABLE'", (archived_at, archived_at, property_id)),),
        )


class SQLCipherLandParcelRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: LandParcelRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        sql = (
            f"INSERT INTO land_parcel ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            "ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get(self, record_id: str) -> LandParcelRecord | None:
        row = self._connection.execute("SELECT * FROM land_parcel WHERE id=?", (record_id,)).fetchone()
        return LandParcelRecord(**row) if row else None

    def list_for_property(self, property_id: str) -> tuple[LandParcelRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM land_parcel WHERE property_id=? ORDER BY created_at,id", (property_id,)
        ).fetchall()
        return tuple(LandParcelRecord(**row) for row in rows)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE land_parcel SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherLandValuationComponentRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: LandValuationComponentRecord) -> None:
        values = asdict(record)
        values["include_in_final_value"] = int(record.include_in_final_value)
        columns = tuple(values)
        sql = (
            f"INSERT INTO land_valuation_component ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            "ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def list_for_property(self, property_id: str) -> tuple[LandValuationComponentRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM land_valuation_component WHERE property_id=? ORDER BY created_at,id", (property_id,)
        ).fetchall()
        output = []
        for row in rows:
            row["include_in_final_value"] = _bool(row["include_in_final_value"])
            output.append(LandValuationComponentRecord(**row))
        return tuple(output)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE land_valuation_component SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherPropertyCharacteristicRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: PropertyCharacteristicRecord) -> None:
        values = asdict(record)
        values["verified_by_user"] = int(record.verified_by_user)
        values["bool_value"] = None if record.bool_value is None else int(record.bool_value)
        columns = tuple(values)
        sql = (
            f"INSERT INTO property_characteristic ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            "ON CONFLICT(property_id,definition_key) DO UPDATE SET "
            + ",".join(
                f"{name}=excluded.{name}"
                for name in columns
                if name not in {"id", "property_id", "definition_key"}
            )
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def list_for_property(self, property_id: str) -> tuple[PropertyCharacteristicRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM property_characteristic WHERE property_id=? ORDER BY definition_key,id",
            (property_id,),
        ).fetchall()
        output = []
        for row in rows:
            row["verified_by_user"] = _bool(row["verified_by_user"])
            row["bool_value"] = _optional_bool(row["bool_value"])
            output.append(PropertyCharacteristicRecord(**row))
        return tuple(output)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE property_characteristic SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherMarketObservationRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: MarketObservationRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        sql = (
            f"INSERT INTO market_observation ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            "ON CONFLICT(comparable_property_id) DO UPDATE SET "
            + ",".join(
                f"{name}=excluded.{name}" for name in columns if name not in {"id", "comparable_property_id"}
            )
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get_by_comparable(self, comparable_property_id: str) -> MarketObservationRecord | None:
        row = self._connection.execute(
            "SELECT * FROM market_observation WHERE comparable_property_id=?",
            (comparable_property_id,),
        ).fetchone()
        return MarketObservationRecord(**row) if row else None

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE market_observation SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherEvidenceRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: EvidenceRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        sql = (
            f"INSERT INTO evidence ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            "ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def list_for_property(self, property_id: str) -> tuple[EvidenceRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM evidence WHERE property_id=? ORDER BY created_at,id", (property_id,)
        ).fetchall()
        return tuple(EvidenceRecord(**row) for row in rows)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE evidence SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherConstructionAssetRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: ConstructionAssetRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        sql = (
            f"INSERT INTO construction_asset ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get(self, record_id: str) -> ConstructionAssetRecord | None:
        row = self._connection.execute("SELECT * FROM construction_asset WHERE id=?", (record_id,)).fetchone()
        return ConstructionAssetRecord(**row) if row else None

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE construction_asset SET archived_at=?, updated_at=? WHERE id=?", (archived_at, archived_at, record_id)),),
        )


class SQLCipherAdjustmentDecisionRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: AdjustmentDecisionRecord) -> None:
        values = asdict(record)
        values["selected_explicitly"] = int(record.selected_explicitly)
        columns = tuple(values)
        sql = (
            f"INSERT INTO adjustment_decision ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get(self, record_id: str) -> AdjustmentDecisionRecord | None:
        row = self._connection.execute("SELECT * FROM adjustment_decision WHERE id=?", (record_id,)).fetchone()
        if row is None:
            return None
        row["selected_explicitly"] = _bool(row["selected_explicitly"])
        return AdjustmentDecisionRecord(**row)

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE adjustment_decision SET archived_at=? WHERE id=?", (archived_at, record_id)),),
        )


class SQLCipherApprovalSubmissionRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: ApprovalSubmissionRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        sql = (
            f"INSERT INTO approval_submission ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
            f"ON CONFLICT(id) DO UPDATE SET "
            + ",".join(f"{name}=excluded.{name}" for name in columns if name != "id")
        )
        _commit(self._connection, ((sql, tuple(values[name] for name in columns)),))

    def get(self, record_id: str) -> ApprovalSubmissionRecord | None:
        row = self._connection.execute("SELECT * FROM approval_submission WHERE id=?", (record_id,)).fetchone()
        return ApprovalSubmissionRecord(**row) if row else None

    def archive(self, record_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE approval_submission SET archived_at=? WHERE id=?", (archived_at, record_id)),),
        )
