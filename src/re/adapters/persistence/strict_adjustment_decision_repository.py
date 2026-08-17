"""Strict persistence adapter for adjustment decisions.

Decision identity (id/case/comparable/factor) is immutable after insert. Mutable
selection state is updated with optimistic version comparison when requested.
"""

from __future__ import annotations

from dataclasses import asdict

from ...ports.persistence import AdjustmentDecisionRecord


_MUTABLE_COLUMNS = (
    "suggested_rate_pct",
    "selected_rate_pct",
    "selected_explicitly",
    "selected_at",
    "source_data_revision",
    "review_status",
    "approved_rate_pct",
    "version",
    "archived_at",
)


class StrictSQLCipherAdjustmentDecisionRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    @staticmethod
    def _params(record: AdjustmentDecisionRecord) -> dict[str, object]:
        values = asdict(record)
        values["selected_explicitly"] = int(record.selected_explicitly)
        return values

    def put(self, record: AdjustmentDecisionRecord) -> None:
        values = self._params(record)
        columns = tuple(values)
        self._connection.execute(
            f"""INSERT INTO adjustment_decision ({','.join(columns)})
            VALUES ({','.join('?' for _ in columns)})
            ON CONFLICT(id) DO UPDATE SET
            {','.join(f'{name}=excluded.{name}' for name in _MUTABLE_COLUMNS)}""",
            tuple(values[name] for name in columns),
        )

    def put_if_version(
        self, record: AdjustmentDecisionRecord, *, expected_version: int
    ) -> bool:
        values = self._params(record)
        assignments = ",".join(f"{name}=?" for name in _MUTABLE_COLUMNS)
        cursor = self._connection.execute(
            f"UPDATE adjustment_decision SET {assignments} WHERE id=? AND version=?",
            tuple(values[name] for name in _MUTABLE_COLUMNS)
            + (record.id, expected_version),
        )
        return cursor.rowcount == 1

    def get(self, record_id: str) -> AdjustmentDecisionRecord | None:
        row = self._connection.execute(
            "SELECT * FROM adjustment_decision WHERE id=?", (record_id,)
        ).fetchone()
        if row is None:
            return None
        row["selected_explicitly"] = bool(int(row["selected_explicitly"]))
        return AdjustmentDecisionRecord(**row)

    def archive(self, record_id: str, archived_at: str) -> None:
        self._connection.execute(
            "UPDATE adjustment_decision SET archived_at=? WHERE id=?",
            (archived_at, record_id),
        )
