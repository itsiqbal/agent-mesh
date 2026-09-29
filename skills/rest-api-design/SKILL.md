---
name: rest-api-design
description: REST API design conventions — resource naming, status codes, pagination, versioning, and error response shape. Use when designing or reviewing any HTTP API, regardless of backend language.
---
# REST API Design

## Resources & naming
- Plural nouns for collections (`/orders`, `/orders/{id}`), nested resources only one level deep where it reflects real ownership (`/orders/{id}/items`).
- Use HTTP methods correctly: GET (read, no side effects), POST (create), PUT (full replace), PATCH (partial update), DELETE (remove).

## Status codes
- 200/201/204 for success, 400 for validation errors, 401/403 for auth, 404 for missing resources, 409 for conflicts, 422 for semantically invalid input, 5xx only for genuine server-side failures.

## Pagination & filtering
- Cursor-based pagination for large/growing collections; offset/limit is fine for small, bounded ones. Document which one an endpoint uses.
- Filtering/sorting via query params with a documented, validated allowlist — never pass raw query params into a database query.

## Versioning
- Version in the URL path (`/v1/...`) or a header — pick one convention per project and stick to it; never make a breaking change to a live endpoint without bumping the version.

## Error shape
- One consistent error body across the whole API: `{"error": "string_code", "message": "human readable", "details": [...]}`. Every service should produce the same shape.

## Docs
- Keep an OpenAPI/Swagger spec in sync with the implementation (generate it from code annotations where the framework supports it, e.g. springdoc-openapi).
