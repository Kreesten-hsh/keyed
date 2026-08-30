from __future__ import annotations

import hmac

import pytest

from keyed.core import hashing


def test_generated_key_verifies_and_plaintext_is_hidden_from_repr() -> None:
    generated = hashing.generate_api_key("live")

    assert generated.plaintext.startswith(generated.prefix)
    assert hashing.verify_api_key(
        generated.plaintext,
        salt=generated.salt,
        expected_hash=generated.key_hash,
    )
    assert generated.plaintext not in repr(generated)


def test_invalid_key_fails_verification() -> None:
    generated = hashing.generate_api_key("test")

    assert not hashing.verify_api_key(
        "key_test_invalid.invalid",
        salt=generated.salt,
        expected_hash=generated.key_hash,
    )


def test_two_generated_keys_do_not_collide() -> None:
    first = hashing.generate_api_key("live")
    second = hashing.generate_api_key("live")

    assert first.plaintext != second.plaintext
    assert first.prefix != second.prefix
    assert first.key_hash != second.key_hash


def test_prefix_is_extracted_without_a_fixed_slice() -> None:
    generated = hashing.generate_api_key("live")

    assert hashing.extract_key_prefix(generated.plaintext) == generated.prefix
    assert hashing.extract_key_prefix("key_live_deadbeef.secret") == "key_live_deadbeef."
    assert hashing.extract_key_prefix("not-a-key") is None


def test_verification_uses_constant_time_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated = hashing.generate_api_key("live")
    calls: list[tuple[bytes, bytes]] = []
    original_compare_digest = hmac.compare_digest

    def compare_digest(left: bytes, right: bytes) -> bool:
        calls.append((left, right))
        return original_compare_digest(left, right)

    monkeypatch.setattr(hashing.hmac, "compare_digest", compare_digest)

    assert hashing.verify_api_key(
        generated.plaintext,
        salt=generated.salt,
        expected_hash=generated.key_hash,
    )
    assert calls == [(generated.key_hash, generated.key_hash)]
