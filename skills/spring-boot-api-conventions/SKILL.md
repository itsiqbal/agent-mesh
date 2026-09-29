---
name: spring-boot-api-conventions
description: Conventions for building REST APIs with Java and Spring Boot — layering, DTOs, validation, exception handling, and persistence with JPA/Hibernate. Use when creating or modifying Spring Boot controllers, services, or repositories.
---
# Spring Boot API Conventions

## Layering
- Controller: HTTP concerns only (mapping, status codes, request/response DTOs). No business logic.
- Service: business logic; transactions (`@Transactional`) live here, not in controllers.
- Repository: Spring Data JPA interfaces; custom queries via `@Query` or `Specification`, never string-concatenated SQL.

## DTOs
- Never return JPA entities directly from controllers. Map to a response DTO (MapStruct or a manual mapper).
- Validate request DTOs with `jakarta.validation` annotations (`@NotNull`, `@Size`, `@Email`, etc.) and a global `@ControllerAdvice` to turn `MethodArgumentNotValidException` into a consistent error response.

## Errors
- Central `@ControllerAdvice` mapping domain exceptions to HTTP status + a consistent error body: `{"error": "...", "message": "...", "details": [...]}`.
- Never leak stack traces or raw exception messages to clients in production profiles.

## Persistence
- Migrations via Flyway (or Liquibase if already in use) — never rely on Hibernate `ddl-auto` in shared/prod environments.
- Add an index in the migration that introduces a new query pattern.

## Testing
- Unit test services with JUnit 5 + Mockito.
- Integration test the persistence layer and controllers with `@SpringBootTest` / `@DataJpaTest` / `@WebMvcTest` and Testcontainers for the real database engine (Postgres/MySQL) rather than H2.

## Config
- Externalize config via `application.yml` + Spring profiles (dev/test/prod); secrets come from environment variables / GCP Secret Manager, never hardcoded.
