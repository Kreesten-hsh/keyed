# API key rate limiting without an external gateway or proxy

Most API architecture tutorials recommend placing an API gateway or reverse proxy in front of your service to enforce rate limits.

While gateways like Kong, Zuplo, or Envoy sidecars work well for enterprise infrastructure, they introduce operational complexity and recurring costs for solo developers and small teams. You need to configure DNS routing, maintain SSL certificates in multiple places, and pay monthly subscription fees for external proxy networks.

You can enforce robust, per-key rate limiting directly inside your application middleware using local memory or an existing Redis instance.

## The hidden cost of adding a gateway for basic rate limiting

Deploying an external gateway just to inspect an API key header creates several hidden problems:

First, it adds external network latency. Every request must pass through a third-party server before reaching your API, adding anywhere from 15 to 80 milliseconds of roundtrip time.

Second, it creates an external point of failure. If the gateway provider suffers a routing outage or DNS misconfiguration, your API becomes completely unreachable even if your backend servers are healthy.

Third, the pricing model is often misaligned with early-stage products. Most gateway providers charge monthly base fees plus overages per million requests. When you are running small side projects or bootstrapped micro-SaaS tools, these recurring subscriptions accumulate quickly.

## How sliding window rate limiting works at the middleware layer

Rate limiting algorithms generally fall into three categories: fixed window, token bucket, and sliding window counter.

Fixed window counters reset at fixed boundaries (such as the top of every minute). This creates a vulnerability where a client can send its entire quota at 11:59:59 and another full quota at 12:00:01, effectively doubling the allowed throughput across that boundary.

The sliding window counter algorithm fixes this without high memory overhead. It tracks the request count in the previous window and the current window, weighting them proportionally based on the current timestamp.

The formula is simple:

```text
weighted_requests = previous_window_count * (1 - time_into_current_window / window_size) + current_window_count
```

If the weighted request count is below your limit, the request is allowed and the current window counter increments.

## Implementing sliding window rate limiting in Express or Node.js

Here is a practical sliding window rate limiter implemented as a lightweight Express middleware using an in-memory Map or Redis:

```javascript
export function createRateLimiter({ limit = 60, windowMs = 60000 }) {
  const store = new Map();

  return function rateLimitMiddleware(req, res, next) {
    const key = req.headers['x-api-key'] || req.ip;
    const now = Date.now();
    const currentWindowStart = Math.floor(now / windowMs) * windowMs;

    let record = store.get(key);
    if (!record) {
      record = { currentStart: currentWindowStart, currentCount: 0, previousCount: 0 };
      store.set(key, record);
    }

    // Handle window rollover
    if (now - record.currentStart >= windowMs) {
      const isNextImmediateWindow = now - record.currentStart < windowMs * 2;
      record.previousCount = isNextImmediateWindow ? record.currentCount : 0;
      record.currentCount = 0;
      record.currentStart = currentWindowStart;
    }

    // Calculate sliding estimate
    const timeElapsedInCurrent = now - record.currentStart;
    const weight = 1 - (timeElapsedInCurrent / windowMs);
    const estimatedCount = Math.floor(record.previousCount * weight) + record.currentCount;

    const remaining = Math.max(0, limit - estimatedCount - 1);
    const resetTime = Math.ceil((record.currentStart + windowMs - now) / 1000);

    res.setHeader('X-RateLimit-Limit', limit);
    res.setHeader('X-RateLimit-Remaining', remaining);
    res.setHeader('X-RateLimit-Reset', resetTime);

    if (estimatedCount >= limit) {
      return res.status(429).json({
        error: 'Too Many Requests',
        message: `Rate limit exceeded. Try again in ${resetTime} seconds.`
      });
    }

    record.currentCount += 1;
    next();
  };
}
```

## Returning standard rate limit headers

RFC standards and developer expectations require consistent response headers so API clients can handle throttle limits gracefully:

1. `X-RateLimit-Limit`: The maximum number of requests allowed in the current window.
2. `X-RateLimit-Remaining`: The remaining number of requests allowed for the client in the active window.
3. `X-RateLimit-Reset`: The number of seconds remaining until the current rate limit window resets.

When a client breaches the limit, return HTTP status code `429 Too Many Requests` with a clear JSON error payload indicating when requests can safely resume.

## Conclusion

Enforcing API key rate limits at the middleware layer keeps your architecture simple, avoids third-party latency, and eliminates recurring proxy fees.

If you want a drop-in SDK that handles local key hashing, sliding-window rate limiting, and instant revocation in three lines of code, take a look at keyed. It runs entirely inside your application with zero proxy dependencies and is available as a one-time purchase.

Explore keyed and join the waitlist at https://kreesten-hsh.github.io/keyed/
