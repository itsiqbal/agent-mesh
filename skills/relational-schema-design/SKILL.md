---
name: relational-schema-design
description: Schema design, indexing, and migration practices for MySQL and PostgreSQL. Use when designing tables, writing migrations, or reviewing SQL schema changes.
---
# Relational Schema Design (MySQL & PostgreSQL)

## Design
- Normalize by default (3NF); denormalize deliberately and document why, not as a first draft.
- Every table gets a primary key (prefer a surrogate key: `bigint`/`uuid`), `created_at`/`updated_at` timestamps, and a soft-delete flag only if the domain actually needs undelete/audit history.
- Foreign keys are enforced at the database level, not just in application code.

## Indexing
- Index every foreign key and every column used in a `WHERE`/`JOIN`/`ORDER BY` for a query you're introducing.
- Prefer a composite index matching the query's actual filter order over several single-column indexes.
- Don't over-index write-heavy tables; check existing indexes before adding one that overlaps.

## Migrations
- Every schema change is a versioned, reversible migration (Flyway/Liquibase for Java, Prisma Migrate/node-pg-migrate/knex for Node) — never a manual `ALTER` against a shared environment.
- For a table with production data: additive changes first (add a nullable column, backfill, then add `NOT NULL`/constraint in a follow-up migration) to avoid locking or downtime.

## MySQL vs PostgreSQL specifics
- MySQL: prefer InnoDB, be explicit about collation (`utf8mb4`), watch for implicit type coercion in `WHERE` clauses.
- PostgreSQL: use native types (`jsonb` for semi-structured columns, arrays/enums where they genuinely fit), leverage partial and expression indexes when useful, use `EXPLAIN ANALYZE` before assuming a query is slow.
