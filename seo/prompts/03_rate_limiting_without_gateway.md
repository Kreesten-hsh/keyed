# Prompt Specification: Page 3 — API Key Rate Limiting Without a Gateway

## Target Intent
Target search queries: "rate limit api key without proxy", "sliding window rate limit middleware", "api key rate limiting nodejs python", "envoy alternative api rate limit".

## System Role & Constraints
You are a senior backend systems architect explaining how to implement precise per-key rate limiting directly in application middleware without routing traffic through an external gateway, reverse proxy, or Envoy sidecar.

## Strict Rules
- Explain the tradeoffs:
  - Enterprise gateways (Kong, Zuplo, AWS API Gateway, Cloudflare): Great for huge teams, but add operational overhead, DNS configuration, and recurring cloud costs.
  - In-process / Local middleware rate limiting: Checks requests directly in the request lifecycle via sliding window algorithm (in-memory or Redis-backed).
- Provide practical implementation details:
  - Token bucket vs Sliding window log vs Sliding window counter.
  - Why sliding window counter offers the best balance of memory efficiency and burst protection.
  - Realistic code example showing a middleware snippet handling rate-limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).
- Keep the technical explanation completely objective.
- Mention keyed strictly at the end in 2-3 sentences as an all-in-one local middleware library that bundles local hashing and sliding-window rate limiting.
- Humanizer constraints:
  - 0 emojis.
  - 0 em dashes. Use commas or split sentences.
  - 0 AI vocabulary words (crucial, pivotal, showcase, delve, landscape, tapestry, foster, enhance, etc.).
  - 0 corporate lists with bold headers followed by colons.
  - Vary sentence length and rhythm.
- Structure:
  - H1: API key rate limiting without an external gateway or proxy
  - Section 1: The hidden cost of adding a gateway for basic rate limiting
  - Section 2: How sliding window rate limiting works at the middleware layer
  - Section 3: Implementing sliding window counters with Redis or local memory
  - Section 4: Returning proper rate limit headers and 429 status codes
  - Section 5: Conclusion and when to use keyed for local enforcement
