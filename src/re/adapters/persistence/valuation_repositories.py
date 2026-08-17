"""SQLCipher repositories for immutable E1-PR-003 indication evidence."""

from __future__ import annotations

from dataclasses import asdict

from ...ports.valuation_persistence import (
    HumanIndicationSnapshotRecord,
    HumanIndicationSourceRecord,
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


class SQLCipherHumanIndicationSnapshotRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: HumanIndicationSnapshotRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO human_indication_snapshot ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def get(self, record_id: str) -> HumanIndicationSnapshotRecord | None:
        row = self._connection.execute(
            "SELECT * FROM human_indication_snapshot WHERE id=?", (record_id,)
        ).fetchone()
        return HumanIndicationSnapshotRecord(**row) if row else None

    def list_for_case(self, case_id: str) -> tuple[HumanIndicationSnapshotRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM human_indication_snapshot
            WHERE case_id=? ORDER BY confirmed_at,id""",
            (case_id,),
        ).fetchall()
        return tuple(HumanIndicationSnapshotRecord(**row) for row in rows)


class SQLCipherHumanIndicationSourceRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: HumanIndicationSourceRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO human_indication_source ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def list_for_snapshot(
        self, indication_snapshot_id: str
    ) -> tuple[HumanIndicationSourceRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM human_indication_source
            WHERE indication_snapshot_id=? ORDER BY comparable_property_id""",
            (indication_snapshot_id,),
        ).fetchall()
        return tuple(HumanIndicationSourceRecord(**row) for row in rows)
