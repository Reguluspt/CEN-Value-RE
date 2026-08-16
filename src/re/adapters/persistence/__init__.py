"""Encrypted persistence adapters for CenValue RE."""

from .key_protection import (
    KeyProtectionError,
    KeyProtector,
    WindowsDPAPIKeyProtector,
    load_or_create_master_key,
)
from .migrations import LATEST_SCHEMA_VERSION, MIGRATIONS, apply_migrations
from .sqlcipher import SQLCipherSecurityError, SQLCipherUnavailableError
from .store import EncryptedREPersistence, PersistencePaths, SQLCipherUnitOfWork

__all__ = [
    "EncryptedREPersistence",
    "KeyProtectionError",
    "KeyProtector",
    "LATEST_SCHEMA_VERSION",
    "MIGRATIONS",
    "PersistencePaths",
    "SQLCipherSecurityError",
    "SQLCipherUnavailableError",
    "SQLCipherUnitOfWork",
    "WindowsDPAPIKeyProtector",
    "apply_migrations",
    "load_or_create_master_key",
]
