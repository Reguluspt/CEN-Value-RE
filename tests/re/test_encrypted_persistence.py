"""E0-PR-007 encrypted persistence foundation acceptance tests."""

from __future__ import annotations

import ctypes
import hashlib
import secrets
import sqlite3
import sys
from pathlib import Path

import pytest

from src.re.adapters.persistence import (
    EncryptedREPersistence,
    KeyProtectionError,
    LATEST_SCHEMA_VERSION,
    PersistencePaths,
    SQLCipherSecurityError,
    WindowsDPAPIKeyProtector,
)
from src.re.adapters.persistence import key_protection as key_protection_module
from src.re.adapters.persistence import migrations as migration_module
from src.re.adapters.persistence.key_protection import load_or_create_master_key
from src.re.adapters.persistence.migrations import Migration, apply_migrations
from src.re.adapters.persistence.sqlcipher import open_encrypted_connection
from src.re.ports.persistence import (
    AdjustmentDecisionRecord,
    ApprovalSubmissionRecord,
    CaseRecord,
    ComparablePropertyRecord,
    ConstructionAssetRecord,
    SubjectPropertyRecord,
)


class MemoryKeyProtector:
    """In-memory test double; protected blobs contain no plaintext master key."""

    def __init__(self) -> None:
        self._values: dict[bytes, bytes] = {}
        self.protect_calls = 0
        self.unprotect_calls = 0
        self.last_plaintext: bytes | None = None

    def protect(self, plaintext: bytes) -> bytes:
        self.protect_calls += 1
        self.last_plaintext = bytes(plaintext)
        token = b"test-wrapped:" + secrets.token_bytes(48)
        self._values[token] = bytes(plaintext)
        return token

    def unprotect(self, protected: bytes) -> bytes:
        self.unprotect_calls += 1
        try:
            return self._values[protected]
        except KeyError as exc:
            raise KeyProtectionError("test protector cannot unwrap this blob") from exc


def _persistence(tmp_path: Path, protector: MemoryKeyProtector, legacy: Path | None = None):
    return EncryptedREPersistence(
        PersistencePaths(tmp_path / "re-app-data"),
        protector,
        legacy_cases_db=legacy,
    )


def test_master_key_is_random_wrapped_and_reused(tmp_path: Path) -> None:
    protector = MemoryKeyProtector()
    path = tmp_path / "cenvalue-re.masterkey"
    first = load_or_create_master_key(path, protector)
    assert len(first) == 32
    assert protector.protect_calls == 1
    assert first not in path.read_bytes()

    second = load_or_create_master_key(path, protector)
    assert second == first
    assert protector.protect_calls == 1
    assert protector.unprotect_calls == 1


def test_protected_key_file_rejects_unknown_format(tmp_path: Path) -> None:
    path = tmp_path / "cenvalue-re.masterkey"
    path.write_bytes(b"plaintext-key-material")
    with pytest.raises(KeyProtectionError, match="Unrecognized"):
        load_or_create_master_key(path, MemoryKeyProtector())


def test_dpapi_baseline_is_current_user_scope() -> None:
    assert WindowsDPAPIKeyProtector.scope == "CURRENT_USER"
    if sys.platform != "win32":
        with pytest.raises(KeyProtectionError, match="only on Windows"):
            WindowsDPAPIKeyProtector()


def test_dpapi_wrap_unwrap_uses_noninteractive_current_user_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    buffers: list[object] = []
    flags: list[int] = []
    local_free_calls: list[object] = []

    class FakeFunction:
        def __init__(self, implementation):
            self.implementation = implementation
            self.argtypes = None
            self.restype = None

        def __call__(self, *args):
            return self.implementation(*args)

    def write_blob(output_arg, value: bytes) -> None:
        buffer = ctypes.create_string_buffer(value, len(value))
        buffers.append(buffer)
        output = output_arg._obj
        output.cbData = len(value)
        output.pbData = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))

    def protect(input_arg, description, entropy, reserved, prompt, dw_flags, output_arg):
        del description, entropy, reserved, prompt
        flags.append(dw_flags)
        source = input_arg._obj
        plaintext = ctypes.string_at(source.pbData, source.cbData)
        write_blob(output_arg, b"wrapped:" + plaintext)
        return 1

    def unprotect(input_arg, description_arg, entropy, reserved, prompt, dw_flags, output_arg):
        del entropy, reserved, prompt
        flags.append(dw_flags)
        source = input_arg._obj
        protected = ctypes.string_at(source.pbData, source.cbData)
        assert protected.startswith(b"wrapped:")
        write_blob(output_arg, protected[len(b"wrapped:") :])
        description_arg._obj.value = "CenValue RE master key"
        return 1

    def local_free(pointer):
        local_free_calls.append(pointer)
        return None

    crypt32 = type("FakeCrypt32", (), {})()
    crypt32.CryptProtectData = FakeFunction(protect)
    crypt32.CryptUnprotectData = FakeFunction(unprotect)
    kernel32 = type("FakeKernel32", (), {})()
    kernel32.LocalFree = FakeFunction(local_free)

    monkeypatch.setattr(key_protection_module.sys, "platform", "win32")
    monkeypatch.setattr(
        key_protection_module.ctypes,
        "WinDLL",
        lambda name, use_last_error=True: crypt32 if name == "crypt32" else kernel32,
        raising=False,
    )

    protector = WindowsDPAPIKeyProtector()
    plaintext = b"k" * 32
    protected = protector.protect(plaintext)
    assert protected != plaintext
    assert protector.unprotect(protected) == plaintext
    assert flags == [key_protection_module.CRYPTPROTECT_UI_FORBIDDEN] * 2
    assert len(local_free_calls) == 3


def test_plain_sqlite_binding_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SQLCipherSecurityError, match="not SQLCipher"):
        open_encrypted_connection(tmp_path / "must-not-be-plain.db", b"k" * 32, dbapi=sqlite3)


def test_sqlcipher_db_is_encrypted_at_rest_and_wrong_key_fails(tmp_path: Path) -> None:
    protector = MemoryKeyProtector()
    persistence = _persistence(tmp_path, protector)
    with persistence.open() as uow:
        assert uow.schema_version == LATEST_SCHEMA_VERSION
        assert uow.sqlcipher_version
        uow.cases.put(
            CaseRecord(
                id="case-1",
                case_code="CV-001",
                status="DRAFT",
                created_at="2026-08-16T00:00:00Z",
                updated_at="2026-08-16T00:00:00Z",
                client_name="Sensitive Client",
            )
        )

    raw = persistence.paths.database.read_bytes()
    assert raw[:16] != b"SQLite format 3\x00"
    assert b"Sensitive Client" not in raw
    assert protector.last_plaintext is not None
    assert protector.last_plaintext not in persistence.paths.protected_master_key.read_bytes()

    with persistence.open() as reopened:
        assert reopened.cases.get("case-1") is not None

    with pytest.raises(Exception):
        bad = open_encrypted_connection(persistence.paths.database, secrets.token_bytes(32))
        bad.close()

    plain = sqlite3.connect(persistence.paths.database)
    try:
        with pytest.raises(sqlite3.DatabaseError):
            plain.execute("SELECT count(*) FROM sqlite_master").fetchone()
    finally:
        plain.close()


def test_all_six_repository_contracts_round_trip_exact_strings(tmp_path: Path) -> None:
    persistence = _persistence(tmp_path, MemoryKeyProtector())
    with persistence.open() as uow:
        case = CaseRecord(
            id="case-1",
            case_code="CV-001",
            status="IN_PROGRESS",
            created_at="2026-08-16T00:00:00Z",
            updated_at="2026-08-16T00:00:00Z",
            appraisal_date="2026-08-16",
            include_in_historical_learning=True,
        )
        subject = SubjectPropertyRecord(
            property_id="subject-1",
            case_id=case.id,
            legal_address="Legal A",
            current_address="Current A",
            legal_review_status="REVIEWED",
            created_at=case.created_at,
            updated_at=case.updated_at,
        )
        comparable = ComparablePropertyRecord(
            property_id="comp-1",
            case_id=case.id,
            legal_address="Legal B",
            current_address="Current B",
            comparable_order=1,
            completeness_status="COMPLETE",
            created_at=case.created_at,
            updated_at=case.updated_at,
        )
        asset = ConstructionAssetRecord(
            id="asset-1",
            property_id=subject.property_id,
            name="House",
            legal_registration_status="REGISTERED",
            valuation_treatment="VALUE",
            created_at=case.created_at,
            updated_at=case.updated_at,
            construction_area_m2="300.125",
            replacement_cost_vnd="6500000.00",
            remaining_quality_pct="0.8750",
            remaining_value_vnd="1706250000.000000",
        )
        adjustment = AdjustmentDecisionRecord(
            id="adj-1",
            case_id=case.id,
            comparable_property_id=comparable.property_id,
            factor_key="area",
            selected_explicitly=True,
            source_data_revision="rev-1",
            review_status="CURRENT",
            suggested_rate_pct="0.0500",
            selected_rate_pct="0.0000",
        )
        approval = ApprovalSubmissionRecord(
            id="approval-1",
            case_id=case.id,
            revision_no=1,
            exported_at="2026-08-16T01:00:00Z",
            template_profile_id="N08-0038",
            workbook_hash="abc123",
            submitted_case_snapshot='{"case":"CV-001"}',
            submitted_result_snapshot='{"value":"19581000000"}',
            output_document_id="doc-1",
            status="EXPORTED",
        )

        uow.cases.put(case)
        uow.subjects.put(subject)
        uow.comparables.put(comparable)
        uow.construction_assets.put(asset)
        uow.adjustment_decisions.put(adjustment)
        uow.approval_submissions.put(approval)

        assert uow.cases.get(case.id) == case
        assert uow.subjects.get(subject.property_id) == subject
        assert uow.comparables.get(comparable.property_id) == comparable
        assert uow.construction_assets.get(asset.id) == asset
        assert uow.adjustment_decisions.get(adjustment.id) == adjustment
        assert uow.approval_submissions.get(approval.id) == approval

        archived_at = "2026-08-16T02:00:00Z"
        uow.cases.archive(case.id, archived_at)
        uow.subjects.archive(subject.property_id, archived_at)
        uow.comparables.archive(comparable.property_id, archived_at)
        uow.construction_assets.archive(asset.id, archived_at)
        uow.adjustment_decisions.archive(adjustment.id, archived_at)
        uow.approval_submissions.archive(approval.id, archived_at)
        assert uow.cases.get(case.id).archived_at == archived_at
        assert uow.subjects.get(subject.property_id).archived_at == archived_at
        assert uow.comparables.get(comparable.property_id).archived_at == archived_at
        assert uow.construction_assets.get(asset.id).archived_at == archived_at
        assert uow.adjustment_decisions.get(adjustment.id).archived_at == archived_at
        assert uow.approval_submissions.get(approval.id).archived_at == archived_at


def test_legacy_cases_database_is_untouched(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy" / "cases.db"
    legacy.parent.mkdir()
    legacy.write_bytes(b"legacy-cases-db-sentinel\x00\x01")
    before = hashlib.sha256(legacy.read_bytes()).hexdigest()

    persistence = _persistence(tmp_path, MemoryKeyProtector(), legacy)
    with persistence.open() as uow:
        assert uow.schema_version == 1

    after = hashlib.sha256(legacy.read_bytes()).hexdigest()
    assert before == after
    assert persistence.paths.database != legacy


def test_same_path_as_legacy_database_is_rejected(tmp_path: Path) -> None:
    paths = PersistencePaths(tmp_path)
    with pytest.raises(ValueError, match="separate"):
        EncryptedREPersistence(paths, MemoryKeyProtector(), legacy_cases_db=paths.database)


def test_unknown_schema_version_fails_closed() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE re_schema_migration(version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )
    connection.execute(
        "INSERT INTO re_schema_migration(version,name,applied_at) VALUES (99,'future','now')"
    )
    connection.commit()
    with pytest.raises(RuntimeError, match="unknown migration"):
        apply_migrations(connection)


def test_failed_migration_is_transactional(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = sqlite3.connect(":memory:")
    bad = Migration(
        2,
        "deliberate_failure",
        (
            "CREATE TABLE should_rollback(id TEXT PRIMARY KEY)",
            "THIS IS NOT SQL",
        ),
    )
    monkeypatch.setattr(migration_module, "MIGRATIONS", (migration_module.MIGRATIONS[0], bad))
    with pytest.raises(sqlite3.DatabaseError):
        migration_module.apply_migrations(connection)
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert "should_rollback" not in tables
    versions = [row[0] for row in connection.execute("SELECT version FROM re_schema_migration")]
    assert versions == [1]
