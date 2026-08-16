"""Master-key protection for the encrypted RE persistence adapter."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import secrets
import sys
from pathlib import Path
from typing import Protocol

MASTER_KEY_BYTES = 32
_KEY_FILE_MAGIC = b"CVREKEY1\x00"
CRYPTPROTECT_UI_FORBIDDEN = 0x1


class KeyProtectionError(RuntimeError):
    """Raised when protected master-key material cannot be handled safely."""


class KeyProtector(Protocol):
    def protect(self, plaintext: bytes) -> bytes: ...
    def unprotect(self, protected: bytes) -> bytes: ...


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _blob_from_bytes(value: bytes) -> tuple[_DATA_BLOB, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(value, len(value))
    blob = _DATA_BLOB(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    return blob, buffer


class WindowsDPAPIKeyProtector:
    """Protect keys with current-user Windows DPAPI (never machine scope)."""

    scope = "CURRENT_USER"

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise KeyProtectionError("Windows DPAPI is available only on Windows")
        self._crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._configure_signatures()

    def _configure_signatures(self) -> None:
        self._crypt32.CryptProtectData.argtypes = [
            ctypes.POINTER(_DATA_BLOB),
            wintypes.LPCWSTR,
            ctypes.POINTER(_DATA_BLOB),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DATA_BLOB),
        ]
        self._crypt32.CryptProtectData.restype = wintypes.BOOL
        self._crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(_DATA_BLOB),
            ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(_DATA_BLOB),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DATA_BLOB),
        ]
        self._crypt32.CryptUnprotectData.restype = wintypes.BOOL
        self._kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        self._kernel32.LocalFree.restype = ctypes.c_void_p

    def protect(self, plaintext: bytes) -> bytes:
        if not plaintext:
            raise KeyProtectionError("Refusing to protect empty key material")
        input_blob, keepalive = _blob_from_bytes(plaintext)
        _ = keepalive
        output_blob = _DATA_BLOB()
        ok = self._crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            "CenValue RE master key",
            None,
            None,
            None,
            CRYPTPROTECT_UI_FORBIDDEN,
            ctypes.byref(output_blob),
        )
        if not ok:
            raise KeyProtectionError(f"CryptProtectData failed: {ctypes.get_last_error()}")
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            self._kernel32.LocalFree(output_blob.pbData)

    def unprotect(self, protected: bytes) -> bytes:
        if not protected:
            raise KeyProtectionError("Protected key material is empty")
        input_blob, keepalive = _blob_from_bytes(protected)
        _ = keepalive
        output_blob = _DATA_BLOB()
        description = wintypes.LPWSTR()
        ok = self._crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            ctypes.byref(description),
            None,
            None,
            None,
            CRYPTPROTECT_UI_FORBIDDEN,
            ctypes.byref(output_blob),
        )
        if not ok:
            raise KeyProtectionError(f"CryptUnprotectData failed: {ctypes.get_last_error()}")
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            self._kernel32.LocalFree(output_blob.pbData)
            if description:
                self._kernel32.LocalFree(description)


def load_or_create_master_key(path: Path, protector: KeyProtector) -> bytes:
    """Load an existing wrapped key or create a new random 256-bit master key."""
    path = Path(path)
    if path.exists():
        raw = path.read_bytes()
        if not raw.startswith(_KEY_FILE_MAGIC):
            raise KeyProtectionError("Unrecognized protected-key file format")
        key = protector.unprotect(raw[len(_KEY_FILE_MAGIC) :])
        if len(key) != MASTER_KEY_BYTES:
            raise KeyProtectionError("Unprotected master key has invalid length")
        return key

    path.parent.mkdir(parents=True, exist_ok=True)
    master_key = secrets.token_bytes(MASTER_KEY_BYTES)
    protected = protector.protect(master_key)
    if not protected:
        raise KeyProtectionError("Key protector returned empty protected material")
    payload = _KEY_FILE_MAGIC + protected

    temp = path.with_name(path.name + ".tmp-" + secrets.token_hex(8))
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    finally:
        if temp.exists():
            temp.unlink()
    return master_key
