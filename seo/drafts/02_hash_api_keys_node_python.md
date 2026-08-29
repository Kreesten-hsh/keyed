# How to hash and verify API keys in Node.js and Python

Storing raw API keys in your database is a serious security flaw. If your database ever leaks through an SQL injection, an unencrypted backup, or an exposed snapshot, every user token is immediately compromised.

Just like user passwords, API keys must be hashed before storage. However, API keys have different performance and lookup requirements than user passwords. This guide explains how to generate, hash, index, and verify API keys securely in both Node.js and Python.

## The core security requirements of an API key system

A secure API key architecture requires four main mechanisms:

1. Cryptographic randomness: Keys must be generated using an entropy source provided by the operating system, never with standard pseudorandom generators like Math.random or Python's random module.
2. Structured prefixes: Splitting a key into a public prefix (such as `sk_live_`) and a secret suffix allows fast database lookups without scanning the entire table.
3. Cryptographic hashing: Storing only the cryptographic hash of the secret portion in your database.
4. Constant-time comparison: Comparing hashes using constant-time string equality functions to prevent side-channel timing attacks.

## Implementing API key hashing in Node.js

In Node.js, you can use the built-in `crypto` module to generate keys and compute fast, salted SHA-256 hashes.

Here is a complete implementation showing key generation and verification:

```javascript
import crypto from 'node:crypto';

// 1. Generate a new API key and its database record
export function generateApiKey(environment = 'live') {
  const prefix = `sk_${environment}_`;
  const secretBytes = crypto.randomBytes(24).toString('base64url');
  const fullKey = `${prefix}${secretBytes}`;

  // We hash the secret portion using SHA-256 with a salt
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto
    .createHash('sha256')
    .update(`${salt}:${secretBytes}`)
    .digest('hex');

  return {
    fullKey, // Return this ONCE to the user upon creation
    dbRecord: {
      prefix,
      salt,
      hash,
      createdAt: new Date().toISOString(),
      revoked: false
    }
  };
}

// 2. Verify an incoming API key against a stored database record
export function verifyApiKey(incomingKey, dbRecord) {
  if (!incomingKey || !dbRecord || dbRecord.revoked) {
    return false;
  }

  // Derive prefix length dynamically from the stored prefix
  const prefixLength = dbRecord.prefix.length;
  if (incomingKey.length <= prefixLength) {
    return false;
  }

  const incomingPrefix = incomingKey.slice(0, prefixLength);
  const incomingSecret = incomingKey.slice(prefixLength);

  if (incomingPrefix !== dbRecord.prefix) {
    return false;
  }

  const computedHash = crypto
    .createHash('sha256')
    .update(`${dbRecord.salt}:${incomingSecret}`)
    .digest('hex');

  const computedBuffer = Buffer.from(computedHash, 'hex');
  const storedBuffer = Buffer.from(dbRecord.hash, 'hex');

  if (computedBuffer.length !== storedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(computedBuffer, storedBuffer);
}
```

## Implementing API key hashing in Python with FastAPI

In Python, the standard library provides `secrets` for generation and `hashlib` for hashing.

Here is a clean implementation designed for FastAPI middleware or dependencies:

```python
import secrets
import hashlib
from typing import Optional, Dict

def generate_api_key(environment: str = "live") -> Dict[str, str]:
    prefix = f"sk_{environment}_"
    secret_bytes = secrets.token_urlsafe(24)
    full_key = f"{prefix}{secret_bytes}"
    
    salt = secrets.token_hex(16)
    hash_payload = f"{salt}:{secret_bytes}".encode("utf-8")
    key_hash = hashlib.sha256(hash_payload).hexdigest()
    
    return {
        "full_key": full_key,
        "prefix": prefix,
        "salt": salt,
        "hash": key_hash
    }

def verify_api_key(incoming_key: str, stored_prefix: str, stored_salt: str, stored_hash: str) -> bool:
    if not incoming_key or len(incoming_key) <= len(stored_prefix):
        return False
        
    prefix_len = len(stored_prefix)
    prefix = incoming_key[:prefix_len]
    if not secrets.compare_digest(prefix, stored_prefix):
        return False
        
    incoming_secret = incoming_key[prefix_len:]
    hash_payload = f"{stored_salt}:{incoming_secret}".encode("utf-8")
    computed_hash = hashlib.sha256(hash_payload).hexdigest()
    
    return secrets.compare_digest(computed_hash, stored_hash)
```

## Preventing timing attacks and indexing performance

When verifying API keys on high-throughput endpoints, you need to balance security with latency.

Standard string comparisons (`===` in JavaScript or `==` in Python) return `false` on the first mismatched character. Attackers can measure response times down to microseconds to guess the correct hash byte by byte. Always use `crypto.timingSafeEqual` or `secrets.compare_digest` to ensure verification takes identical time regardless of where a mismatch occurs.

For database performance, never query directly by full key hash if you use slow key derivation functions. Indexing by the public 8-character prefix allows your database to locate the single candidate row via B-Tree index in under 1 millisecond, after which your application code verifies the cryptographic hash in memory.

## Conclusion

Rolling your own API key hashing is straightforward once you handle prefixes, salts, and constant-time checks correctly.

If you prefer not to write and maintain this boilerplate across projects, keyed provides a lightweight local middleware for Node.js and Python that handles local hashing in under 3 milliseconds, sliding-window rate limiting, and instant revocation out of the box for a one-time payment.

Learn more and join the waitlist at https://kreesten-hsh.github.io/keyed/
