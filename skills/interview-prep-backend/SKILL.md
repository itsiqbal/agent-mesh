---
name: interview-prep-backend
description: Topic checklist and question bank for backend engineering interviews — Java/Spring, Node.js, APIs, databases, concurrency, and data structures/algorithms. Use when studying for or running a mock backend interview.
---
# Backend Interview Prep

## Core CS
- Data structures (arrays, hash maps, trees, graphs, heaps), algorithmic complexity (Big-O), common patterns (two pointers, sliding window, BFS/DFS, dynamic programming).

## Language/framework depth
- Java: OOP principles, collections internals, concurrency (threads, executors, synchronized/locks, concurrent collections), JVM memory model basics, Spring (DI, bean lifecycle, transactions, AOP).
- Node.js/TypeScript: event loop, async/await vs callbacks/promises, streams, module system, common pitfalls (blocking the event loop).

## APIs & databases
- REST vs RPC vs GraphQL trade-offs; idempotency; pagination; versioning.
- SQL: joins, indexing, transactions/isolation levels, normalization; NoSQL: when to use document/key-value stores, CAP theorem basics.

## System-level
- Caching strategies, message queues, idempotent consumers, rate limiting, basic distributed-systems vocabulary (overlaps with interview-prep-system-design for deeper questions).

## Sample question types
- "Design a rate limiter", "explain how a HashMap resizes", "what happens when two transactions deadlock", "walk through what happens when this Spring Boot request comes in".

## Practice format
- Coding questions: expect the candidate to talk through their approach before/while coding, discuss complexity, and consider edge cases.
- Conceptual questions: probe for genuine understanding with a follow-up "why" rather than accepting a memorized definition.
