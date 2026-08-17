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
                parcel_number TEXT,
                map_sheet_number TEXT,
                total_area_m2 TEXT,
                legal_address TEXT,
                current_address TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT
            )""",
            """CREATE TABLE land_valuation_component (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL REFERENCES property(id),
                parcel_id TEXT REFERENCES land_parcel(id),
                planning_status TEXT NOT NULL CHECK (planning_status IN ('COMPLIANT','NON_COMPLIANT','UNKNOWN')),
                area_m2 TEXT NOT NULL,
                valuation_basis TEXT NOT NULL CHECK (valuation_basis IN ('MARKET_INDICATED','OFFICIAL_LAND_PRICE','OTHER_MANUAL_BASIS')),
                unit_price_vnd_per_m2 TEXT,
                include_in_final_value INTEGER NOT NULL CHECK (include_in_final_value IN (0,1)),
                note TEXT,
                policy_version TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT
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
                evidence_type TEXT,
                source_url TEXT,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                archived_at TEXT
            )""",
            "CREATE UNIQUE INDEX uq_property_case_role_subject ON property(case_id, role) WHERE role='SUBJECT' AND archived_at IS NULL",
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
    row = connection.execute("SELECT COALESCE(MAX(version), 0) AS version FROM re_schema_migration").fetchone()
    return _scalar(row)
