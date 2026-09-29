---
name: testing-strategy
description: Test strategy and coverage expectations across the stack — unit, integration, and end-to-end tests for Java, Node, and React/Next.js code. Use when writing tests or deciding what level of testing a change needs.
---
# Testing Strategy

## Test pyramid
- Many fast unit tests (pure logic, no I/O), fewer integration tests (real DB/cache via Testcontainers or docker-compose), a handful of end-to-end tests for critical user journeys (Playwright/Cypress).

## What needs a test
- Every new business-logic function or bug fix (write a regression test first for bug fixes).
- Every new API endpoint: at least the happy path and the main failure modes (validation error, not found, unauthorized).
- Every new database migration/query pattern: an integration test against a real instance of the target database.

## Tooling by stack
- Java: JUnit 5 + Mockito for unit tests; `@SpringBootTest`/`@DataJpaTest` + Testcontainers for integration tests.
- Node/TypeScript: Jest or Vitest for unit tests; `supertest` for HTTP-level integration tests.
- React/Next.js: React Testing Library for components; Playwright for end-to-end flows.

## CI gating
- Tests run on every PR; a PR should not merge with a red test suite or a meaningful coverage drop on the files it touches.

## What NOT to do
- Don't write tests that assert on implementation details (internal function calls, private state) — assert on observable behavior/output.
- Don't mock the thing you're trying to test (e.g. mocking the database in a test whose whole purpose is to verify a query).
