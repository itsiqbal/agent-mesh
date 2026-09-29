---
name: mongodb-schema-design
description: Document schema design patterns for MongoDB — embedding vs referencing, indexing, and schema validation. Use when designing MongoDB collections or reviewing document schema changes.
---
# MongoDB Schema Design

## When to reach for MongoDB
- Genuinely flexible/variable-shaped data, high write throughput of denormalized documents, or data that's always read/written as a whole aggregate. Don't default to it for data with clear relational structure and strong consistency needs — that's what MySQL/Postgres are for.

## Embedding vs referencing
- Embed data that's always accessed together and doesn't grow unboundedly (e.g. an order's line items).
- Reference (store an ID) when the related data is large, grows without bound, is shared across many parent documents, or is updated independently.

## Schema
- Define a JSON Schema validator on each collection even though Mongo is schemaless — it catches bugs early and documents the intended shape.
- Version documents when the shape changes (a `schemaVersion` field) so old and new documents can coexist during rollout.

## Indexing
- Index every field used in a query filter or sort; use compound indexes matching actual query patterns (equality fields first, then range/sort fields).
- Use the `explain()` output to confirm a query is using an index, not a collection scan.

## Testing
- Test against a real MongoDB instance (Testcontainers or docker-compose), not a hand-rolled in-memory mock.
