"""SQLCipher repository for authoritative adjustment source state."""

from __future__ import annotations

from ...ports.adjustment_source import AdjustmentSourceStateRecord


class SQLCipherAdjustmentSourceStateRepository:
    def __init__(self, connection) -> None:
        self._connection = connection

    def get(
        self, case_id: str, comparable_property_id: str
    ) -> AdjustmentSourceStateRecord | None:
        row = self._connection.execute(
            """SELECT case_id,comparable_property_id,source_revision,
            normalized_base_price_vnd_per_m2,normalized_base_bound_revision,
            normalized_base_evidence_ref,updated_at
            FROM adjustment_source_state
            WHERE case_id=? AND comparable_property_id=?""",
            (case_id, comparable_property_id),
        ).fetchone()
        return AdjustmentSourceStateRecord(**row) if row else None

    def ensure(
        self, case_id: str, comparable_property_id: str, updated_at: str
    ) -> AdjustmentSourceStateRecord:
        self._connection.execute(
            """INSERT INTO adjustment_source_state(
                case_id,comparable_property_id,source_revision,updated_at
            ) VALUES (?,?,1,?)
            ON CONFLICT(comparable_property_id) DO NOTHING""",
            (case_id, comparable_property_id, updated_at),
        )
        row = self.get(case_id, comparable_property_id)
        if row is None:
            raise RuntimeError("adjustment source state lineage mismatch")
        return row

    def bind_normalized_base(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        expected_source_revision: int,
        normalized_base_price_vnd_per_m2: str,
        evidence_ref: str,
        updated_at: str,
    ) -> AdjustmentSourceStateRecord:
        current = self.get(case_id, comparable_property_id)
        if current is None or current.source_revision != expected_source_revision:
            raise RuntimeError("adjustment source revision changed during base binding")

        same_binding = (
            current.normalized_base_price_vnd_per_m2 == normalized_base_price_vnd_per_m2
            and current.normalized_base_evidence_ref == evidence_ref
            and current.normalized_base_bound_revision == current.source_revision
        )
        if same_binding:
            return current

        has_prior_binding = (
            current.normalized_base_price_vnd_per_m2 is not None
            or current.normalized_base_evidence_ref is not None
        )
        target_revision = expected_source_revision + 1 if has_prior_binding else expected_source_revision

        if has_prior_binding:
            self._connection.execute(
                """INSERT INTO adjustment_selection_audit(
                    id,adjustment_decision_id,case_id,comparable_property_id,factor_key,
                    event_kind,selected_rate_pct,selected_explicitly,selected_by,selected_at,
                    source_data_revision,review_status
                )
                SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                    'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',?,
                    ?, 'SOURCE_DATA_CHANGED'
                FROM adjustment_decision
                WHERE case_id=? AND comparable_property_id=? AND review_status='CURRENT'""",
                (updated_at, str(target_revision), case_id, comparable_property_id),
            )
            self._connection.execute(
                """UPDATE adjustment_decision
                SET review_status='SOURCE_DATA_CHANGED',version=version+1
                WHERE case_id=? AND comparable_property_id=? AND review_status='CURRENT'""",
                (case_id, comparable_property_id),
            )

        cursor = self._connection.execute(
            """UPDATE adjustment_source_state
            SET source_revision=?,
                normalized_base_price_vnd_per_m2=?,
                normalized_base_bound_revision=?,
                normalized_base_evidence_ref=?,
                updated_at=?
            WHERE case_id=? AND comparable_property_id=? AND source_revision=?""",
            (
                target_revision,
                normalized_base_price_vnd_per_m2,
                target_revision,
                evidence_ref,
                updated_at,
                case_id,
                comparable_property_id,
                expected_source_revision,
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("adjustment source revision changed during base binding")
        row = self.get(case_id, comparable_property_id)
        if row is None:
            raise RuntimeError("adjustment source state disappeared during base binding")
        return row
