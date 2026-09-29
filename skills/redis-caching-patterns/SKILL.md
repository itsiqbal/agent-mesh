---
name: redis-caching-patterns
description: Caching, session storage, and rate-limiting patterns using Redis. Use when adding a cache layer, storing sessions, or implementing rate limiting.
---
# Redis Patterns

## Caching
- Cache-aside (lazy loading) is the default: read from cache, on miss read from the source of truth and populate the cache with a TTL.
- Always set a TTL — never cache without an expiry unless there's an explicit invalidation path.
- Key naming: `service:entity:id` (e.g. `orders:order:123`) so keys are greppable and namespaced per service.
- Invalidate/update the cache key on write (or use a short TTL and accept eventual consistency) — decide explicitly, don't leave it undefined.

## Sessions & rate limiting
- Store sessions with a TTL matching your session policy; never store sensitive data unencrypted in a session value.
- Implement rate limiting with a fixed-window or sliding-window counter (`INCR` + `EXPIRE`, or a Lua script for atomicity) rather than reading-then-writing non-atomically.

## Reliability
- Treat Redis as a cache, not a system of record, unless a feature explicitly requires Redis persistence (RDB/AOF) and that's been confirmed with the database-engineer/devops-gcp agent.
- Handle Redis being unavailable gracefully (fail open to the source of truth for caches; fail closed for rate limits/locks where correctness matters).
