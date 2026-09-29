---
name: gcp-deployment
description: Deploying and configuring services on Google Cloud Platform — Cloud Run, GKE, Cloud SQL, Memorystore, Artifact Registry, Cloud Build, and Secret Manager. Use for any deployment, infrastructure, or CI/CD task targeting GCP.
---
# GCP Deployment

## Compute
- Default to Cloud Run for stateless HTTP services (Java/Node/Next.js) — it's simpler to operate than GKE. Reach for GKE only when you need long-running workers, custom networking, or you're already running a cluster.
- Containerize with a minimal multi-stage Dockerfile (build stage + slim runtime image); never ship dev dependencies or build tools in the final image.

## Data
- Cloud SQL for MySQL/PostgreSQL; enable automated backups and a maintenance window before going to production.
- Memorystore for Redis.
- Connect from Cloud Run/GKE via the Cloud SQL Auth Proxy or private IP + Serverless VPC Access, not a public IP with an open firewall rule.

## Secrets & config
- All secrets (DB passwords, API keys) go in Secret Manager and are mounted as env vars/volumes at deploy time — never baked into the image or committed to the repo.

## CI/CD
- Pipeline (Cloud Build or GitHub Actions): install -> lint -> test -> build image -> push to Artifact Registry -> deploy to Cloud Run/GKE.
- Require tests to pass before a deploy step runs; use a separate build per service rather than one monolithic pipeline when services are independently deployable.

## Infra as code
- Define infrastructure (Cloud Run services, Cloud SQL instances, IAM bindings) in Terraform; avoid manual console changes to anything that matters for reproducibility.

## Safety
- Never run `terraform destroy`, delete a Cloud SQL instance, or delete a production Cloud Run revision without explicit user confirmation.
