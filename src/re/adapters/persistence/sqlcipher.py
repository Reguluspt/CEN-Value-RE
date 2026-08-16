"""Fail-closed SQLCipher connection handling for the canonical RE database."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class SQLCipherUnavailableError(RuntimeError):
    """Raised when no SQLCipher-capable DB-API binding is available."""


class SQLCipherSecurityError(RuntimeError):
    """Raised when a connection is not actually operating with SQLCipher."""


def _dict_factory(cursor, row):
    return {description[0]: row[index] for index, description in enumerate(cursor.description)}


def _load_sqlcipher_dbapi() -> Any:
    try:
        from sqlcipher3 import dbapi2 as dbapi
    except ImportError as exc:
        raise SQLCipherUnavailableError(
            "SQLCipher DB-API binding is required; plaintext sqlite3 fallback is forbidden"
        ) from exc
    return dbapi


def open_encrypted_connection(path: Path, key: bytes, *, dbapi: Any | None = None):
    if len(key) != 32:
        raise SQLCipherSecurityError("SQLCipher raw key must contain exactly 32 bytes")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    module = dbapi or _load_sqlcipher_dbapi()
    connection = module.connect(str(path))
    try:
        # SQLCipher raw-key syntax: 256-bit hex blob. This must be the first DB operation.
        connection.execute(f'PRAGMA key = "x\'{key.hex()}\'"')
        row = connection.execute("PRAGMA cipher_version").fetchone()
        version = row[0] if row else None
        if not isinstance(version, str) or not version.strip():
            raise SQLCipherSecurityError("Connected SQLite library is not SQLCipher")
        # Force first-page read so a wrong key fails immediately on an existing DB.
        connection.execute("SELECT count(*) FROM sqlite_master").fetchone()
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL").fetchone()
        connection.row_factory = _dict_factory
        return connection
    except Exception:
        connection.close()
        raise


def cipher_version(connection) -> str:
    row = connection.execute("PRAGMA cipher_version").fetchone()
    if isinstance(row, dict):
        value = next(iter(row.values()), None)
    else:
        value = row[0] if row else None
    if not value:
        raise SQLCipherSecurityError("SQLCipher version is unavailable")
    return str(value)
