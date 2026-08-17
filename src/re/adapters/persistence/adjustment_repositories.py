"""SQLCipher repositories for adjustment audit/query/calculation evidence."""

from __future__ import annotations

from dataclasses import asdict

from ...ports.adjustment_persistence import (
    AdjustmentCalculationSnapshotRecord,
    AdjustmentSelectionAuditRecord,
)
from ...ports.persistence import AdjustmentDecisionRecord


_FACTOR_ORDER_SQL = "CASE factor_key " + " ".join(
    f"WHEN 'C{index}' THEN {index}" for index in range(1, 12)
) + " ELSE 999 END"


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


class SQLCipherAdjustmentDecisionQueryRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def list_for_comparable(
        self, case_id: str, comparable_property_id: str
    ) -> tuple[AdjustmentDecisionRecord, ...]:
        rows = self._connection.execute(
            f"""SELECT * FROM adjustment_decision
            WHERE case_id=? AND comparable_property_id=? AND archived_at IS NULL
            ORDER BY {_FACTOR_ORDER_SQL}, id""",
            (case_id, comparable_property_id),
        ).fetchall()
        output = []
        for row in rows:
            row["selected_explicitly"] = bool(row["selected_explicitly"])
            output.append(AdjustmentDecisionRecord(**row))
        return tuple(output)


class SQLCipherAdjustmentSelectionAuditRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: AdjustmentSelectionAuditRecord) -> None:
        values = asdict(record)
        values["selected_explicitly"] = int(record.selected_explicitly)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO adjustment_selection_audit ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def list_for_decision(
        self, adjustment_decision_id: str
    ) -> tuple[AdjustmentSelectionAuditRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM adjustment_selection_audit
            WHERE adjustment_decision_id=? ORDER BY selected_at,id""",
            (adjustment_decision_id,),
        ).fetchall()
        output = []
        for row in rows:
            row["selected_explicitly"] = bool(row["selected_explicitly"])
            output.append(AdjustmentSelectionAuditRecord(**row))
        return tuple(output)


class SQLCipherAdjustmentCalculationSnapshotRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def add(self, record: AdjustmentCalculationSnapshotRecord) -> None:
        values = asdict(record)
        columns = tuple(values)
        _insert(
            self._connection,
            f"INSERT INTO adjustment_calculation_snapshot ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            tuple(values[name] for name in columns),
        )

    def get(self, record_id: str) -> AdjustmentCalculationSnapshotRecord | None:
        row = self._connection.execute(
            "SELECT * FROM adjustment_calculation_snapshot WHERE id=?", (record_id,)
        ).fetchone()
        return AdjustmentCalculationSnapshotRecord(**row) if row else None

    def list_for_comparable(
        self, case_id: str, comparable_property_id: str
    ) -> tuple[AdjustmentCalculationSnapshotRecord, ...]:
        rows = self._connection.execute(
            """SELECT * FROM adjustment_calculation_snapshot
            WHERE case_id=? AND comparable_property_id=?
            ORDER BY created_at,id""",
            (case_id, comparable_property_id),
        ).fetchall()
        return tuple(AdjustmentCalculationSnapshotRecord(**row) for row in rows)
