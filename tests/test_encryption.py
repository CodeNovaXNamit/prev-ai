"""Tests for encryption utilities."""

from app.encryption import EncryptionManager


def test_encrypt_and_decrypt_roundtrip() -> None:
    manager = EncryptionManager(key="test-key")
    secret = "Highly sensitive note contents"

    encrypted = manager.encrypt(secret)

    assert encrypted != secret
    assert manager.decrypt(encrypted) == secret


def test_invalid_key_cannot_decrypt() -> None:
    manager = EncryptionManager(key="test-key")
    other_manager = EncryptionManager(key="another-key")
    encrypted = manager.encrypt("private")

    try:
        other_manager.decrypt(encrypted)
        assert False, "Expected a ValueError for an invalid key."
    except ValueError:
        assert True
