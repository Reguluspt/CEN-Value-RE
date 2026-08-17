"""SQLCipher repositories for E1-PR-004 final valuation evidence."""

from __future__ import annotations

from dataclasses import asdict

from ...ports.valuation_persistence import (
    ConstructionAggregateInputRecord,
    FinalValuationLandSourceRecord,
    FinalValuationSnapshotRecord,
)


def _insert(connection, sql: str, params: tuple[object, ...]) -> None:
    outer_transaction = bool(getattr(connection, "in_transaction", False))
    try:
        connection.execute(sql, params)
        if not outer_transaction:
            connection.commit()
    except Exception:
        if not outer_transaction:
            connection.rollback()
        raise


class SQLCipherConstructionAggregateInputRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: ConstructionAggregateInputRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO construction_aggregate_input ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def get(self, record_id: str) -> ConstructionAggregateInputRecord | None:
        row = self._connection.execute(
            "SELECT * FROM construction_aggregate_input WHERE id=?", (record_id,)
        ).fetchone()
        return ConstructionAggregateInputRecord(**row) if row else None

    def list_for_case(self, case_id: str) -> tuple[ConstructionAggregateInputRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM construction_aggregate_input
            WHERE case_id=? ORDER BY revision,id""",
            (case_id,),
        ).fetchall()
        return tuple(ConstructionAggregateInputRecord(**row) for row in rows)

    def latest_for_case(self, case_id: str) -> ConstructionAggregateInputRecord | None:
        row = self._connection.execute(
            """SELECT * FROM construction_aggregate_input
            WHERE case_id=? ORDER BY revision DESC,id DESC LIMIT 1""",
            (case_id,),
        ).fetchone()
        return ConstructionAggregateInputRecord(**row) if row else None


class SQLCipherFinalValuationSnapshotRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: FinalValuationSnapshotRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO final_valuation_snapshot ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def get(self, record_id: str) -> FinalValuationSnapshotRecord | None:
        row = self._connection.execute(
            "SELECT * FROM final_valuation_snapshot WHERE id=?", (record_id,)
        ).fetchone()
        return FinalValuationSnapshotRecord(**row) if row else None

    def list_for_case(self, case_id: str) -> tuple[FinalValuationSnapshotRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM final_valuation_snapshot
            WHERE case_id=? ORDER BY composed_at,id""",
            (case_id,),
        ).fetchall()
        return tuple(FinalValuationSnapshotRecord(**row) for row in rows)


class SQLCipherFinalValuationLandSourceRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: FinalValuationLandSourceRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO final_valuation_land_source ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def list_for_snapshot(
        self, valuation_snapshot_id: str
    ) -> tuple[FinalValuationLandSourceRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM final_valuation_land_source
            WHERE valuation_snapshot_id=? ORDER BY land_component_id""",
            (valuation_snapshot_id,),
        ).fetchall()
        return tuple(FinalValuationLandSourceRecord(**row) for row in rows)
