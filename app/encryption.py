"""Encryption helpers for protecting data at rest."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _normalize_key(raw_key: str) -> bytes:
    """Convert a passphrase or raw string into a valid Fernet key."""
    try:
        decoded = base64.urlsafe_b64decode(raw_key.encode("utf-8"))
        if len(decoded) == 32:
            return raw_key.encode("utf-8")
    except Exception:
        pass

    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class EncryptionManager:
    """Fernet wrapper used to encrypt and decrypt local records."""

    def __init__(self, key: str | None = None) -> None:
        settings = get_settings()
        self._fernet = Fernet(_normalize_key(key or settings.encryption_key))

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt stored data with the configured key.") from exc
