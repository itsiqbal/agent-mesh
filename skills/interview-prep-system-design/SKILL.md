---
name: interview-prep-system-design
description: Framework and topic checklist for system design interviews — scalability, availability, data storage, and classic design questions. Use when studying for or running a mock system design interview.
---
# System Design Interview Prep

## Framework for answering
1. Clarify requirements: functional scope, scale (users, QPS, data size), read/write ratio, consistency/latency needs.
2. Back-of-envelope estimation: storage, bandwidth, QPS — order-of-magnitude, not precision.
3. High-level design: the major components (client, load balancer, API layer, cache, database, queue) and how data flows between them.
4. Deep dive: pick 1-2 components worth going deep on (data model, indexing, partitioning, failure handling).
5. Trade-offs: state alternatives considered and why this one was chosen.

## Core building blocks to know
- Load balancing, horizontal vs vertical scaling, caching (CDN, application cache, cache invalidation), database replication/sharding, CAP theorem, message queues, consistent hashing, rate limiting, CDNs.

## Classic prompts
- Design a URL shortener, a rate limiter, a news feed, a chat system, a ride-sharing dispatch system, a distributed job scheduler, an autocomplete/typeahead service.

## Practice format
- Present the prompt and let the candidate drive (ask clarifying questions, propose the design); nudge with a question if they skip a step (e.g. "what's your estimated QPS?") rather than handing them the framework unprompted.
- Feedback should focus on whether they found the actual bottleneck/interesting trade-off for that prompt, not just whether they drew boxes and arrows.
