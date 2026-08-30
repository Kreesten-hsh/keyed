from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, field
from typing import Literal

_KEY_PREFIX_PATTERN = re.compile(r"^key_(?:live|test)_[0-9a-f]{8,64}\.")


@dataclass(frozen=True, slots=True)
class GeneratedAPIKey:
    plaintext: str = field(repr=False)
    prefix: str
    salt: bytes
    key_hash: bytes


def generate_api_key(environment: Literal["live", "test"]) -> GeneratedAPIKey:
    public_id = secrets.token_hex(16)
    prefix = f"key_{environment}_{public_id}."
    plaintext = f"{prefix}{secrets.token_urlsafe(32)}"
    salt = secrets.token_bytes(32)
    return GeneratedAPIKey(
        plaintext=plaintext,
        prefix=prefix,
        salt=salt,
        key_hash=_hash_api_key(plaintext, salt=salt),
    )


def extract_key_prefix(plaintext: str) -> str | None:
    match = _KEY_PREFIX_PATTERN.match(plaintext)
    if match is None or len(plaintext) == match.end():
        return None
    return match.group(0)


def verify_api_key(plaintext: str, *, salt: bytes, expected_hash: bytes) -> bool:
    computed_hash = _hash_api_key(plaintext, salt=salt)
    return hmac.compare_digest(computed_hash, expected_hash)


def _hash_api_key(plaintext: str, *, salt: bytes) -> bytes:
    # Random API keys already have high entropy, so a fast cryptographic hash is
    # appropriate here. Password KDFs are designed for low-entropy human secrets.
    return hashlib.sha256(salt + plaintext.encode("utf-8")).digest()
