"""SQLCipher repository implementations for the Epic 0 persistence foundation."""

from __future__ import annotations

from dataclasses import asdict

from ...ports.persistence import (
    AdjustmentDecisionRecord,
    ApprovalSubmissionRecord,
    CaseRecord,
    ComparablePropertyRecord,
    ConstructionAssetRecord,
    SubjectPropertyRecord,
)


def _commit(connection, statements: tuple[tuple[str, tuple[object, ...]], ...]) -> None:
    try:
        for sql, params in statements:
            connection.execute(sql, params)
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def _bool(value: object) -> bool:
    return bool(int(value))


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


class SQLCipherSubjectPropertyRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def put(self, record: SubjectPropertyRecord) -> None:
        property_params = (
            record.property_id,
            record.case_id,
            "SUBJECT",
            record.display_name,
            record.legal_address,
            record.current_address,
            record.created_at,
            record.updated_at,
            record.version,
            record.archived_at,
        )
        _commit(
            self._connection,
            (
                (
                    """INSERT INTO property(id,case_id,role,display_name,legal_address,current_address,created_at,updated_at,version,archived_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET case_id=excluded.case_id,role=excluded.role,display_name=excluded.display_name,
                    legal_address=excluded.legal_address,current_address=excluded.current_address,updated_at=excluded.updated_at,
                    version=excluded.version,archived_at=excluded.archived_at""",
                    property_params,
                ),
                (
                    """INSERT INTO subject_property(property_id,legal_review_status,source_certificate_id) VALUES (?,?,?)
                    ON CONFLICT(property_id) DO UPDATE SET legal_review_status=excluded.legal_review_status,
                    source_certificate_id=excluded.source_certificate_id""",
                    (record.property_id, record.legal_review_status, record.source_certificate_id),
                ),
            ),
        )

    def get(self, property_id: str) -> SubjectPropertyRecord | None:
        row = self._connection.execute(
            """SELECT p.id AS property_id,p.case_id,p.legal_address,p.current_address,s.legal_review_status,
            p.created_at,p.updated_at,s.source_certificate_id,p.display_name,p.version,p.archived_at
            FROM property p JOIN subject_property s ON s.property_id=p.id WHERE p.id=? AND p.role='SUBJECT'""",
            (property_id,),
        ).fetchone()
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
        property_params = (
            record.property_id,
            record.case_id,
            "COMPARABLE",
            record.display_name,
            record.legal_address,
            record.current_address,
            record.created_at,
            record.updated_at,
            record.version,
            record.archived_at,
        )
        _commit(
            self._connection,
            (
                (
                    """INSERT INTO property(id,case_id,role,display_name,legal_address,current_address,created_at,updated_at,version,archived_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET case_id=excluded.case_id,role=excluded.role,display_name=excluded.display_name,
                    legal_address=excluded.legal_address,current_address=excluded.current_address,updated_at=excluded.updated_at,
                    version=excluded.version,archived_at=excluded.archived_at""",
                    property_params,
                ),
                (
                    """INSERT INTO comparable_property(property_id,comparable_order,market_observation_id,completeness_status)
                    VALUES (?,?,?,?) ON CONFLICT(property_id) DO UPDATE SET comparable_order=excluded.comparable_order,
                    market_observation_id=excluded.market_observation_id,completeness_status=excluded.completeness_status""",
                    (
                        record.property_id,
                        record.comparable_order,
                        record.market_observation_id,
                        record.completeness_status,
                    ),
                ),
            ),
        )

    def get(self, property_id: str) -> ComparablePropertyRecord | None:
        row = self._connection.execute(
            """SELECT p.id AS property_id,p.case_id,p.legal_address,p.current_address,c.comparable_order,c.completeness_status,
            p.created_at,p.updated_at,c.market_observation_id,p.display_name,p.version,p.archived_at
            FROM property p JOIN comparable_property c ON c.property_id=p.id WHERE p.id=? AND p.role='COMPARABLE'""",
            (property_id,),
        ).fetchone()
        return ComparablePropertyRecord(**row) if row else None

    def archive(self, property_id: str, archived_at: str) -> None:
        _commit(
            self._connection,
            (("UPDATE property SET archived_at=?, updated_at=? WHERE id=? AND role='COMPARABLE'", (archived_at, archived_at, property_id)),),
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
