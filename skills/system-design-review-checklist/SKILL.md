---
name: system-design-review-checklist
description: Checklist for reviewing system design proposals and architecture — scalability, reliability, consistency, and trade-offs. Use when reviewing a design doc, RFC, or architecture proposal, or when asked to critique a system design.
---
# System Design Review Checklist

## Requirements
- Are functional and non-functional requirements (scale, latency, availability, consistency) stated explicitly? If not, ask before reviewing further.

## Scale & capacity
- Back-of-envelope numbers: expected QPS, data volume, growth rate. Does the design's likely bottleneck (DB, a single service, a queue) actually hold at that scale?

## Reliability & failure modes
- Single points of failure? What happens when a dependency is slow or down — timeout/retry/circuit-breaker, or a cascading failure?
- Data durability: is data replicated/backed up appropriately for its importance?

## Consistency & data model
- Is the consistency requirement (strong vs eventual) stated, and does the chosen datastore/pattern actually deliver it?
- Are schema/API boundaries between services sensible, or is there hidden coupling (e.g. a shared database between two "independent" services)?

## Trade-offs
- Every non-trivial design decision should have a stated alternative and why it was rejected (cost, complexity, latency, team familiarity).

## Security & operability
- AuthN/AuthZ boundaries between services; secrets handling; what does on-call actually see when this breaks (logging/metrics/alerting)?

## How to give feedback
- Separate "must address before building" from "worth discussing, not blocking" — don't treat every open question as a blocker.
- Prefer proposing a concrete alternative over just flagging a concern.
