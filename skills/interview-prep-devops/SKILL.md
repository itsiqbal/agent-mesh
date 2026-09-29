---
name: interview-prep-devops
description: Topic checklist and question bank for DevOps/SRE interviews — CI/CD, containers, orchestration, infrastructure as code, cloud networking, and incident response. Use when studying for or running a mock DevOps interview.
---
# DevOps Interview Prep

## CI/CD
- Pipeline stages, build caching, artifact management, blue-green/canary/rolling deployments, feature flags vs deployment.

## Containers & orchestration
- Docker fundamentals (layers, image size, multi-stage builds), Kubernetes core objects (Pod, Deployment, Service, Ingress, ConfigMap/Secret), how a request reaches a pod, resource requests/limits and autoscaling (HPA).

## Infrastructure as code
- Terraform state management, drift, modules; the trade-off between IaC and manual/console changes.

## Cloud & networking (GCP focus)
- VPCs/subnets, load balancers, Cloud SQL/Memorystore connectivity patterns, IAM basics, Secret Manager, the difference between Cloud Run/GKE/Compute Engine and when to use each.

## Observability & incident response
- The three pillars (logs, metrics, traces), SLIs/SLOs/error budgets, what a good alert looks like (actionable, not noisy), a structured incident-response walkthrough (detect, mitigate, root-cause, postmortem).

## Sample question types
- "Walk me through what happens when a pod crash-loops", "design a CI/CD pipeline for a microservice on GCP", "how would you debug a service that's slow only under load", "what's in a good postmortem".

## Practice format
- Favor scenario-based questions ("it's 3am, this alert fires, what do you do") over pure definitions — probe for a methodical debugging process.
