"""Encrypted persistence composition root for CenValue RE."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .adjustment_repositories import (
    SQLCipherAdjustmentCalculationSnapshotRepository,
    SQLCipherAdjustmentDecisionQueryRepository,
    SQLCipherAdjustmentSelectionAuditRepository,
)
from .adjustment_source_repository import SQLCipherAdjustmentSourceStateRepository
from .key_protection import KeyProtector, load_or_create_master_key
from .migrations import apply_migrations
from .repositories import (
    SQLCipherApprovalSubmissionRepository,
    SQLCipherCaseRepository,
    SQLCipherComparablePropertyRepository,
    SQLCipherConstructionAssetRepository,
    SQLCipherEvidenceRepository,
    SQLCipherLandParcelRepository,
    SQLCipherLandValuationComponentRepository,
    SQLCipherMarketObservationRepository,
    SQLCipherPropertyCharacteristicRepository,
    SQLCipherSubjectPropertyRepository,
)
from .strict_adjustment_decision_repository import StrictSQLCipherAdjustmentDecisionRepository
from .sqlcipher import cipher_version, open_encrypted_connection


@dataclass(frozen=True, slots=True)
class PersistencePaths:
    app_data_dir: Path

    @property
    def database(self) -> Path:
        return self.app_data_dir / "cenvalue-re.db"

    @property
    def protected_master_key(self) -> Path:
        return self.app_data_dir / "cenvalue-re.masterkey"


class SQLCipherUnitOfWork:
    def __init__(self, connection, schema_version: int) -> None:
        self._connection = connection
        self._schema_version = schema_version
        self.cases = SQLCipherCaseRepository(connection)
        self.subjects = SQLCipherSubjectPropertyRepository(connection)
        self.comparables = SQLCipherComparablePropertyRepository(connection)
        self.land_parcels = SQLCipherLandParcelRepository(connection)
        self.land_valuation_components = SQLCipherLandValuationComponentRepository(connection)
        self.property_characteristics = SQLCipherPropertyCharacteristicRepository(connection)
        self.market_observations = SQLCipherMarketObservationRepository(connection)
        self.evidence = SQLCipherEvidenceRepository(connection)
        self.construction_assets = SQLCipherConstructionAssetRepository(connection)
        self.adjustment_decisions = StrictSQLCipherAdjustmentDecisionRepository(connection)
        self.adjustment_decision_queries = SQLCipherAdjustmentDecisionQueryRepository(connection)
        self.adjustment_selection_audit = SQLCipherAdjustmentSelectionAuditRepository(connection)
        self.adjustment_calculation_snapshots = SQLCipherAdjustmentCalculationSnapshotRepository(connection)
        self.adjustment_source_states = SQLCipherAdjustmentSourceStateRepository(connection)
        self.approval_submissions = SQLCipherApprovalSubmissionRepository(connection)

    @property
    def schema_version(self) -> int:
        return self._schema_version

    @property
    def sqlcipher_version(self) -> str:
        return cipher_version(self._connection)

    @contextmanager
    def atomic(self) -> Iterator[None]:
        if bool(getattr(self._connection, "in_transaction", False)):
            raise RuntimeError("Nested persistence transactions are not supported")
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLCipherUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class EncryptedREPersistence:
    """Open the separate canonical RE database using wrapped key material."""

    def __init__(
        self,
        paths: PersistencePaths,
        key_protector: KeyProtector,
        *,
        legacy_cases_db: Path | None = None,
        dbapi: Any | None = None,
    ) -> None:
        self.paths = PersistencePaths(Path(paths.app_data_dir))
        self._key_protector = key_protector
        self._legacy_cases_db = Path(legacy_cases_db) if legacy_cases_db is not None else None
        self._dbapi = dbapi
        if self._legacy_cases_db is not None:
            if self.paths.database.resolve() == self._legacy_cases_db.resolve():
                raise ValueError("CenValue RE database must be separate from legacy cases.db")

    def open(self) -> SQLCipherUnitOfWork:
        master_key = load_or_create_master_key(
            self.paths.protected_master_key, self._key_protector
        )
        connection = open_encrypted_connection(
            self.paths.database, master_key, dbapi=self._dbapi
        )
        try:
            schema_version = apply_migrations(connection)
            return SQLCipherUnitOfWork(connection, schema_version)
        except Exception:
            connection.close()
            raise
