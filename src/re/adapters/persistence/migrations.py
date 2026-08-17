"""Explicit ordered schema migrations for the separate CenValue RE database."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]


MIGRATIONS = (
    Migration(
        1,
        "initial_re_persistence_foundation",
        (
            """CREATE TABLE appraisal_case (
                id TEXT PRIMARY KEY,
                case_code TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                appraisal_date TEXT,
                client_name TEXT,
                valuation_purpose TEXT,
                include_in_historical_learning INTEGER NOT NULL DEFAULT 0 CHECK (include_in_historical_learning IN (0, 1)),
                active_subject_property_id TEXT,
                current_approval_revision INTEGER,
                legacy_case_id TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                archived_at TEXT
            )""",
            """CREATE TABLE property (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                role TEXT NOT NULL CHECK (role IN ('SUBJECT', 'COMPARABLE')),
                display_name TEXT,
                legal_address TEXT NOT NULL,
                current_address TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                archived_at TEXT
            )""",
            """CREATE TABLE subject_property (
                property_id TEXT PRIMARY KEY REFERENCES property(id),
                legal_review_status TEXT NOT NULL,
                source_certificate_id TEXT
            )""",
            """CREATE TABLE comparable_property (
                property_id TEXT PRIMARY KEY REFERENCES property(id),
                comparable_order INTEGER NOT NULL,
                market_observation_id TEXT,
                completeness_status TEXT NOT NULL
            )""",
            """CREATE TABLE construction_asset (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                name TEXT NOT NULL,
                construction_type TEXT,
                construction_area_m2 TEXT,
                gross_floor_area_m2 TEXT,
                legal_registration_status TEXT NOT NULL,
                valuation_treatment TEXT NOT NULL,
                replacement_cost_vnd TEXT,
                remaining_quality_pct TEXT,
                remaining_value_vnd TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                archived_at TEXT
            )""",
            """CREATE TABLE adjustment_decision (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                comparable_property_id TEXT NOT NULL REFERENCES comparable_property(property_id),
                factor_key TEXT NOT NULL,
                suggested_rate_pct TEXT,
                selected_rate_pct TEXT,
                selected_explicitly INTEGER NOT NULL CHECK (selected_explicitly IN (0, 1)),
                selected_at TEXT,
                source_data_revision TEXT NOT NULL,
                review_status TEXT NOT NULL,
                approved_rate_pct TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                archived_at TEXT,
                UNIQUE(case_id, comparable_property_id, factor_key)
            )""",
            """CREATE TABLE approval_submission (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                revision_no INTEGER NOT NULL,
                exported_at TEXT NOT NULL,
                template_profile_id TEXT NOT NULL,
                workbook_hash TEXT NOT NULL,
                submitted_case_snapshot TEXT NOT NULL,
                submitted_result_snapshot TEXT NOT NULL,
                output_document_id TEXT NOT NULL,
                status TEXT NOT NULL,
                archived_at TEXT,
                UNIQUE(case_id, revision_no)
            )""",
        ),
    ),
    Migration(
        2,
        "epic1_manual_case_data_backbone",
        (
            "ALTER TABLE appraisal_case ADD COLUMN template_profile_id TEXT",
            "ALTER TABLE appraisal_case ADD COLUMN template_profile_version TEXT",
            "ALTER TABLE property ADD COLUMN latitude TEXT",
            "ALTER TABLE property ADD COLUMN longitude TEXT",
            "ALTER TABLE property ADD COLUMN planning_note TEXT",
            "ALTER TABLE property ADD COLUMN environment_note TEXT",
            "ALTER TABLE comparable_property ADD COLUMN case_id TEXT REFERENCES appraisal_case(id)",
            "UPDATE comparable_property SET case_id=(SELECT case_id FROM property WHERE property.id=comparable_property.property_id)",
            "CREATE UNIQUE INDEX uq_comparable_case_order ON comparable_property(case_id, comparable_order) WHERE case_id IS NOT NULL",
            """CREATE TRIGGER comparable_lineage_insert_guard
            BEFORE INSERT ON comparable_property
            WHEN NEW.case_id IS NULL
              OR NEW.comparable_order NOT IN (1,2,3)
              OR NEW.case_id != (SELECT case_id FROM property WHERE id=NEW.property_id)
            BEGIN
              SELECT RAISE(ABORT, 'comparable case lineage mismatch');
            END""",
            """CREATE TRIGGER comparable_lineage_update_guard
            BEFORE UPDATE OF case_id, comparable_order, property_id ON comparable_property
            WHEN NEW.case_id IS NULL
              OR NEW.comparable_order NOT IN (1,2,3)
              OR NEW.case_id != (SELECT case_id FROM property WHERE id=NEW.property_id)
            BEGIN
              SELECT RAISE(ABORT, 'comparable case lineage mismatch');
            END""",
            """CREATE TABLE land_parcel (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                parcel_order INTEGER NOT NULL CHECK (parcel_order > 0),
                parcel_number TEXT,
                map_sheet_number TEXT,
                total_area_m2 TEXT,
                legal_address TEXT,
                current_address TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT,
                UNIQUE(property_id, parcel_order)
            )""",
            """CREATE TABLE land_valuation_component (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                parcel_id TEXT REFERENCES land_parcel(id),
                component_order INTEGER NOT NULL CHECK (component_order > 0),
                planning_status TEXT NOT NULL CHECK (planning_status IN ('COMPLIANT','NON_COMPLIANT','UNKNOWN')),
                area_m2 TEXT NOT NULL,
                valuation_basis TEXT NOT NULL CHECK (valuation_basis IN ('MARKET_INDICATED','OFFICIAL_LAND_PRICE','OTHER_MANUAL_BASIS')),
                unit_price_vnd_per_m2 TEXT,
                include_in_final_value INTEGER NOT NULL CHECK (include_in_final_value IN (0,1)),
                note TEXT,
                policy_version TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT,
                UNIQUE(parcel_id, component_order)
            )""",
            """CREATE TABLE property_characteristic (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                definition_key TEXT NOT NULL,
                decimal_value TEXT,
                text_value TEXT,
                code_value TEXT,
                bool_value INTEGER CHECK (bool_value IN (0,1) OR bool_value IS NULL),
                date_value TEXT,
                source_status TEXT NOT NULL,
                provenance_id TEXT,
                verified_by_user INTEGER NOT NULL CHECK (verified_by_user IN (0,1)),
                updated_at TEXT NOT NULL,
                archived_at TEXT,
                UNIQUE(property_id, definition_key)
            )""",
            """CREATE TABLE market_observation (
                id TEXT PRIMARY KEY,
                comparable_property_id TEXT NOT NULL UNIQUE REFERENCES comparable_property(property_id),
                asking_or_sale_price_vnd TEXT NOT NULL,
                negotiation_rate_pct TEXT,
                negotiated_price_vnd TEXT NOT NULL,
                observation_date TEXT,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT
            )""",
            """CREATE TABLE evidence (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                market_observation_id TEXT REFERENCES market_observation(id),
                evidence_order INTEGER NOT NULL CHECK (evidence_order > 0),
                evidence_type TEXT,
                source_url TEXT,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT,
                UNIQUE(property_id, evidence_order)
            )""",
            "CREATE UNIQUE INDEX uq_property_case_role_subject ON property(case_id, role) WHERE role='SUBJECT' AND archived_at IS NULL",
        ),
    ),
    Migration(
        3,
        "epic1_market_adjustment_evidence",
        (
            """CREATE TRIGGER adjustment_decision_lineage_insert_guard
            BEFORE INSERT ON adjustment_decision
            WHEN NEW.case_id != (SELECT case_id FROM comparable_property WHERE property_id=NEW.comparable_property_id)
            BEGIN
              SELECT RAISE(ABORT, 'adjustment decision case lineage mismatch');
            END""",
            """CREATE TRIGGER adjustment_decision_lineage_update_guard
            BEFORE UPDATE OF case_id, comparable_property_id ON adjustment_decision
            WHEN NEW.case_id != (SELECT case_id FROM comparable_property WHERE property_id=NEW.comparable_property_id)
            BEGIN
              SELECT RAISE(ABORT, 'adjustment decision case lineage mismatch');
            END""",
            """CREATE TRIGGER adjustment_decision_identity_update_guard
            BEFORE UPDATE OF case_id, comparable_property_id, factor_key ON adjustment_decision
            WHEN NEW.case_id != OLD.case_id
              OR NEW.comparable_property_id != OLD.comparable_property_id
              OR NEW.factor_key != OLD.factor_key
            BEGIN
              SELECT RAISE(ABORT, 'adjustment decision identity is immutable');
            END""",
            """CREATE TABLE adjustment_selection_audit (
                id TEXT PRIMARY KEY,
                adjustment_decision_id TEXT NOT NULL REFERENCES adjustment_decision(id),
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                comparable_property_id TEXT NOT NULL REFERENCES comparable_property(property_id),
                factor_key TEXT NOT NULL,
                event_kind TEXT NOT NULL CHECK (event_kind IN ('SELECTED','SOURCE_DATA_CHANGED')),
                selected_rate_pct TEXT,
                selected_explicitly INTEGER NOT NULL CHECK (selected_explicitly IN (0,1)),
                selected_by TEXT NOT NULL CHECK (length(trim(selected_by)) > 0),
                selected_at TEXT NOT NULL,
                source_data_revision TEXT NOT NULL,
                review_status TEXT NOT NULL
            )""",
            """CREATE TRIGGER adjustment_selection_audit_lineage_guard
            BEFORE INSERT ON adjustment_selection_audit
            WHEN NEW.case_id != (SELECT case_id FROM comparable_property WHERE property_id=NEW.comparable_property_id)
              OR NEW.case_id != (SELECT case_id FROM adjustment_decision WHERE id=NEW.adjustment_decision_id)
              OR NEW.comparable_property_id != (SELECT comparable_property_id FROM adjustment_decision WHERE id=NEW.adjustment_decision_id)
              OR NEW.factor_key != (SELECT factor_key FROM adjustment_decision WHERE id=NEW.adjustment_decision_id)
            BEGIN
              SELECT RAISE(ABORT, 'adjustment selection audit lineage mismatch');
            END""",
            """CREATE TABLE adjustment_calculation_snapshot (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                comparable_property_id TEXT NOT NULL REFERENCES comparable_property(property_id),
                source_data_revision TEXT NOT NULL,
                normalized_base_price_vnd_per_m2 TEXT NOT NULL,
                normalized_base_evidence_ref TEXT NOT NULL,
                property_adjustment_base_vnd_per_m2 TEXT NOT NULL,
                indicated_unit_price_vnd_per_m2 TEXT NOT NULL,
                decision_set_sha256 TEXT NOT NULL,
                ordered_steps_json TEXT NOT NULL,
                semantic_sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""",
            """CREATE TRIGGER adjustment_snapshot_lineage_guard
            BEFORE INSERT ON adjustment_calculation_snapshot
            WHEN NEW.case_id != (SELECT case_id FROM comparable_property WHERE property_id=NEW.comparable_property_id)
            BEGIN
              SELECT RAISE(ABORT, 'adjustment calculation snapshot case lineage mismatch');
            END""",
            """CREATE TABLE adjustment_source_state (
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                comparable_property_id TEXT PRIMARY KEY REFERENCES comparable_property(property_id),
                source_revision INTEGER NOT NULL CHECK (source_revision > 0),
                normalized_base_price_vnd_per_m2 TEXT,
                normalized_base_bound_revision INTEGER,
                normalized_base_evidence_ref TEXT,
                updated_at TEXT NOT NULL,
                CHECK (
                    (normalized_base_price_vnd_per_m2 IS NULL AND normalized_base_bound_revision IS NULL AND normalized_base_evidence_ref IS NULL)
                    OR
                    (normalized_base_price_vnd_per_m2 IS NOT NULL AND normalized_base_bound_revision = source_revision AND length(trim(normalized_base_evidence_ref)) > 0)
                )
            )""",
            """CREATE TRIGGER adjustment_source_state_lineage_insert_guard
            BEFORE INSERT ON adjustment_source_state
            WHEN NEW.case_id != (SELECT case_id FROM comparable_property WHERE property_id=NEW.comparable_property_id)
            BEGIN
              SELECT RAISE(ABORT, 'adjustment source state lineage mismatch');
            END""",
            """CREATE TRIGGER adjustment_source_state_identity_update_guard
            BEFORE UPDATE OF case_id, comparable_property_id ON adjustment_source_state
            WHEN NEW.case_id != OLD.case_id OR NEW.comparable_property_id != OLD.comparable_property_id
            BEGIN
              SELECT RAISE(ABORT, 'adjustment source state identity is immutable');
            END""",
            """INSERT INTO adjustment_source_state(case_id,comparable_property_id,source_revision,updated_at)
            SELECT case_id,property_id,1,strftime('%Y-%m-%dT%H:%M:%fZ','now')
            FROM comparable_property WHERE case_id IS NOT NULL""",
            """CREATE TRIGGER adjustment_source_comparable_insert
            AFTER INSERT ON comparable_property
            WHEN NEW.case_id IS NOT NULL
            BEGIN
              INSERT OR IGNORE INTO adjustment_source_state(case_id,comparable_property_id,source_revision,updated_at)
              VALUES (NEW.case_id,NEW.property_id,1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));
            END""",
            """CREATE TRIGGER adjustment_source_property_update
            AFTER UPDATE OF legal_address,current_address,latitude,longitude,planning_note,environment_note,version,archived_at ON property
            WHEN NEW.role='COMPARABLE'
            BEGIN
              UPDATE adjustment_source_state SET source_revision=source_revision+1,
                  normalized_base_price_vnd_per_m2=NULL,normalized_base_bound_revision=NULL,
                  normalized_base_evidence_ref=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
              WHERE comparable_property_id=NEW.id;
              INSERT INTO adjustment_selection_audit(
                  id,adjustment_decision_id,case_id,comparable_property_id,factor_key,event_kind,
                  selected_rate_pct,selected_explicitly,selected_by,selected_at,source_data_revision,review_status)
              SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                  'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',
                  strftime('%Y-%m-%dT%H:%M:%fZ','now'),
                  CAST((SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id=NEW.id) AS TEXT),
                  'SOURCE_DATA_CHANGED'
              FROM adjustment_decision WHERE comparable_property_id=NEW.id AND review_status='CURRENT';
              UPDATE adjustment_decision SET review_status='SOURCE_DATA_CHANGED',version=version+1
              WHERE comparable_property_id=NEW.id AND review_status='CURRENT';
            END""",
            """CREATE TRIGGER adjustment_source_market_insert
            AFTER INSERT ON market_observation
            BEGIN
              UPDATE adjustment_source_state SET source_revision=source_revision+1,
                  normalized_base_price_vnd_per_m2=NULL,normalized_base_bound_revision=NULL,
                  normalized_base_evidence_ref=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
              WHERE comparable_property_id=NEW.comparable_property_id;
              INSERT INTO adjustment_selection_audit(
                  id,adjustment_decision_id,case_id,comparable_property_id,factor_key,event_kind,
                  selected_rate_pct,selected_explicitly,selected_by,selected_at,source_data_revision,review_status)
              SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                  'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',
                  strftime('%Y-%m-%dT%H:%M:%fZ','now'),
                  CAST((SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id=NEW.comparable_property_id) AS TEXT),
                  'SOURCE_DATA_CHANGED'
              FROM adjustment_decision WHERE comparable_property_id=NEW.comparable_property_id AND review_status='CURRENT';
              UPDATE adjustment_decision SET review_status='SOURCE_DATA_CHANGED',version=version+1
              WHERE comparable_property_id=NEW.comparable_property_id AND review_status='CURRENT';
            END""",
            """CREATE TRIGGER adjustment_source_market_update
            AFTER UPDATE ON market_observation
            BEGIN
              UPDATE adjustment_source_state SET source_revision=source_revision+1,
                  normalized_base_price_vnd_per_m2=NULL,normalized_base_bound_revision=NULL,
                  normalized_base_evidence_ref=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
              WHERE comparable_property_id=NEW.comparable_property_id;
              INSERT INTO adjustment_selection_audit(
                  id,adjustment_decision_id,case_id,comparable_property_id,factor_key,event_kind,
                  selected_rate_pct,selected_explicitly,selected_by,selected_at,source_data_revision,review_status)
              SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                  'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',
                  strftime('%Y-%m-%dT%H:%M:%fZ','now'),
                  CAST((SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id=NEW.comparable_property_id) AS TEXT),
                  'SOURCE_DATA_CHANGED'
              FROM adjustment_decision WHERE comparable_property_id=NEW.comparable_property_id AND review_status='CURRENT';
              UPDATE adjustment_decision SET review_status='SOURCE_DATA_CHANGED',version=version+1
              WHERE comparable_property_id=NEW.comparable_property_id AND review_status='CURRENT';
            END""",
            """CREATE TRIGGER adjustment_source_characteristic_insert
            AFTER INSERT ON property_characteristic
            WHEN EXISTS(SELECT 1 FROM property WHERE id=NEW.property_id AND role='COMPARABLE')
            BEGIN
              UPDATE adjustment_source_state SET source_revision=source_revision+1,
                  normalized_base_price_vnd_per_m2=NULL,normalized_base_bound_revision=NULL,
                  normalized_base_evidence_ref=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
              WHERE comparable_property_id=NEW.property_id;
              INSERT INTO adjustment_selection_audit(
                  id,adjustment_decision_id,case_id,comparable_property_id,factor_key,event_kind,
                  selected_rate_pct,selected_explicitly,selected_by,selected_at,source_data_revision,review_status)
              SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                  'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',
                  strftime('%Y-%m-%dT%H:%M:%fZ','now'),
                  CAST((SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id=NEW.property_id) AS TEXT),
                  'SOURCE_DATA_CHANGED'
              FROM adjustment_decision WHERE comparable_property_id=NEW.property_id AND review_status='CURRENT';
              UPDATE adjustment_decision SET review_status='SOURCE_DATA_CHANGED',version=version+1
              WHERE comparable_property_id=NEW.property_id AND review_status='CURRENT';
            END""",
            """CREATE TRIGGER adjustment_source_characteristic_update
            AFTER UPDATE ON property_characteristic
            WHEN EXISTS(SELECT 1 FROM property WHERE id=NEW.property_id AND role='COMPARABLE')
            BEGIN
              UPDATE adjustment_source_state SET source_revision=source_revision+1,
                  normalized_base_price_vnd_per_m2=NULL,normalized_base_bound_revision=NULL,
                  normalized_base_evidence_ref=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
              WHERE comparable_property_id=NEW.property_id;
              INSERT INTO adjustment_selection_audit(
                  id,adjustment_decision_id,case_id,comparable_property_id,factor_key,event_kind,
                  selected_rate_pct,selected_explicitly,selected_by,selected_at,source_data_revision,review_status)
              SELECT lower(hex(randomblob(16))),id,case_id,comparable_property_id,factor_key,
                  'SOURCE_DATA_CHANGED',selected_rate_pct,selected_explicitly,'SYSTEM_SOURCE_DRIFT',
                  strftime('%Y-%m-%dT%H:%M:%fZ','now'),
                  CAST((SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id=NEW.property_id) AS TEXT),
                  'SOURCE_DATA_CHANGED'
              FROM adjustment_decision WHERE comparable_property_id=NEW.property_id AND review_status='CURRENT';
              UPDATE adjustment_decision SET review_status='SOURCE_DATA_CHANGED',version=version+1
              WHERE comparable_property_id=NEW.property_id AND review_status='CURRENT';
            END""",
            "CREATE INDEX ix_adjustment_audit_decision ON adjustment_selection_audit(adjustment_decision_id, selected_at, id)",
            "CREATE INDEX ix_adjustment_snapshot_comparable ON adjustment_calculation_snapshot(case_id, comparable_property_id, created_at, id)",
        ),
    ),
    Migration(
        4,
        "epic1_comparable_quality_human_indication",
        (
            """CREATE TABLE human_indication_snapshot (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                selection_kind TEXT NOT NULL CHECK (selection_kind IN ('COMPARABLE','ZERO_GROSS_AVERAGE')),
                selected_comparable_property_id TEXT REFERENCES comparable_property(property_id),
                raw_indicated_unit_price_vnd_per_m2 TEXT NOT NULL,
                rounded_indicated_unit_price_vnd_per_m2 TEXT NOT NULL,
                rounding_target TEXT NOT NULL CHECK (rounding_target='UNIT_PRICE'),
                rounding_increment_vnd INTEGER CHECK (rounding_increment_vnd IS NULL OR rounding_increment_vnd > 0),
                rounding_source TEXT NOT NULL,
                rounding_profile_id TEXT,
                rounding_profile_version TEXT,
                confirmed_by TEXT NOT NULL CHECK (length(trim(confirmed_by)) > 0),
                confirmed_at TEXT NOT NULL,
                reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
                quality_snapshot_json TEXT NOT NULL,
                readiness_snapshot_json TEXT NOT NULL,
                guidance_snapshot_json TEXT NOT NULL,
                semantic_sha256 TEXT NOT NULL,
                CHECK (
                    (selection_kind='COMPARABLE' AND selected_comparable_property_id IS NOT NULL)
                    OR
                    (selection_kind='ZERO_GROSS_AVERAGE' AND selected_comparable_property_id IS NULL)
                )
            )""",
            """CREATE TRIGGER human_indication_snapshot_lineage_guard
            BEFORE INSERT ON human_indication_snapshot
            WHEN NEW.selected_comparable_property_id IS NOT NULL
              AND NEW.case_id != (
                  SELECT case_id FROM comparable_property
                  WHERE property_id=NEW.selected_comparable_property_id
              )
            BEGIN
              SELECT RAISE(ABORT, 'human indication selected comparable case lineage mismatch');
            END""",
            """CREATE TRIGGER human_indication_snapshot_update_guard
            BEFORE UPDATE ON human_indication_snapshot
            BEGIN
              SELECT RAISE(ABORT, 'human indication snapshot is immutable');
            END""",
            """CREATE TRIGGER human_indication_snapshot_delete_guard
            BEFORE DELETE ON human_indication_snapshot
            BEGIN
              SELECT RAISE(ABORT, 'human indication snapshot is append-only');
            END""",
            """CREATE TABLE human_indication_source (
                indication_snapshot_id TEXT NOT NULL REFERENCES human_indication_snapshot(id),
                case_id TEXT NOT NULL REFERENCES appraisal_case(id),
                comparable_property_id TEXT NOT NULL REFERENCES comparable_property(property_id),
                adjustment_snapshot_id TEXT NOT NULL REFERENCES adjustment_calculation_snapshot(id),
                adjustment_semantic_sha256 TEXT NOT NULL,
                PRIMARY KEY(indication_snapshot_id, comparable_property_id)
            )""",
            """CREATE TRIGGER human_indication_source_lineage_guard
            BEFORE INSERT ON human_indication_source
            WHEN NEW.case_id != (
                    SELECT case_id FROM human_indication_snapshot
                    WHERE id=NEW.indication_snapshot_id
                 )
              OR NEW.case_id != (
                    SELECT case_id FROM comparable_property
                    WHERE property_id=NEW.comparable_property_id
                 )
              OR NEW.case_id != (
                    SELECT case_id FROM adjustment_calculation_snapshot
                    WHERE id=NEW.adjustment_snapshot_id
                 )
              OR NEW.comparable_property_id != (
                    SELECT comparable_property_id FROM adjustment_calculation_snapshot
                    WHERE id=NEW.adjustment_snapshot_id
                 )
              OR NEW.adjustment_semantic_sha256 != (
                    SELECT semantic_sha256 FROM adjustment_calculation_snapshot
                    WHERE id=NEW.adjustment_snapshot_id
                 )
            BEGIN
              SELECT RAISE(ABORT, 'human indication source evidence lineage mismatch');
            END""",
            """CREATE TRIGGER human_indication_source_cardinality_guard
            BEFORE INSERT ON human_indication_source
            WHEN (SELECT COUNT(*) FROM human_indication_source
                  WHERE indication_snapshot_id=NEW.indication_snapshot_id) >= 3
            BEGIN
              SELECT RAISE(ABORT, 'human indication snapshot may bind exactly three comparable sources');
            END""",
            """CREATE TRIGGER human_indication_source_update_guard
            BEFORE UPDATE ON human_indication_source
            BEGIN
              SELECT RAISE(ABORT, 'human indication source evidence is immutable');
            END""",
            """CREATE TRIGGER human_indication_source_delete_guard
            BEFORE DELETE ON human_indication_source
            BEGIN
              SELECT RAISE(ABORT, 'human indication source evidence is append-only');
            END""",
            "CREATE INDEX ix_human_indication_case ON human_indication_snapshot(case_id, confirmed_at, id)",
            "CREATE INDEX ix_human_indication_source_adjustment ON human_indication_source(adjustment_snapshot_id)",
        ),
    ),
)

LATEST_SCHEMA_VERSION = MIGRATIONS[-1].version


def _scalar(row) -> int:
    if isinstance(row, dict):
        return int(next(iter(row.values())))
    return int(row[0])


def apply_migrations(connection) -> int:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS re_schema_migration (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )"""
    )
    connection.commit()
    applied = {
        int(row["version"] if isinstance(row, dict) else row[0])
        for row in connection.execute("SELECT version FROM re_schema_migration")
    }
    known = {migration.version for migration in MIGRATIONS}
    unknown = sorted(applied - known)
    if unknown:
        raise RuntimeError(f"Database contains unknown migration versions: {unknown}")

    for migration in MIGRATIONS:
        if migration.version in applied:
            continue
        connection.execute("BEGIN IMMEDIATE")
        try:
            for statement in migration.statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO re_schema_migration(version, name) VALUES (?, ?)",
                (migration.version, migration.name),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    row = connection.execute("SELECT MAX(version) FROM re_schema_migration").fetchone()
    if row is None:
        return 0
    if isinstance(row, dict):
        value = next(iter(row.values()), None)
    else:
        value = row[0]
    return int(value) if value is not None else 0