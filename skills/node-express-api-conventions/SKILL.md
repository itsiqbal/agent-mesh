---
name: node-express-api-conventions
description: Conventions for building Node.js/TypeScript backend services with Express or NestJS — project structure, validation, error handling, and testing. Use when creating or modifying a Node.js API service.
---
# Node.js/TypeScript API Conventions

## Structure
- Layer by responsibility: routes/controllers -> services -> data access. Keep controllers thin.
- TypeScript strict mode on; define request/response types explicitly, avoid `any`.

## Validation
- Validate all external input with zod (or `class-validator` in NestJS) at the boundary, before it reaches business logic.

## Errors
- Central error-handling middleware; throw typed errors (e.g. `class NotFoundError extends AppError`) and map them to HTTP status codes in one place.

## Data access
- Use a query builder or ORM appropriate to the datastore (Prisma/Knex/`pg` for Postgres/MySQL; the official MongoDB driver or Mongoose for MongoDB; `ioredis` for Redis).
- Never build SQL by string concatenation; always use parameterized queries.

## Testing
- Unit test services with Jest or Vitest.
- Integration test HTTP endpoints with `supertest` against a test database (docker-compose or Testcontainers), not mocks-all-the-way-down.

## Config
- Load config via environment variables validated at startup (fail fast if a required var is missing); never commit `.env` files.
