---
name: deploy-gcp
description: "Deploy a service to GCP."
---

# $deploy-gcp
Deploy a service to GCP.

## Steps
1. Confirm target environment (dev/staging/prod) and service name with the user before doing anything.
2. Run the full test suite; stop and report if anything fails.
3. Lint/build the service; build the container image following the gcp-deployment skill's Dockerfile guidance.
4. Push the image to Artifact Registry.
5. For prod: confirm with the user before deploying — this is a high-impact action per the global rules.
6. Deploy to Cloud Run/GKE using the existing Terraform/CI configuration if one exists; otherwise propose one rather than improvising manual `gcloud` commands against prod.
7. Run a smoke test against the deployed service (basic health check / key endpoint) and report the result, including the new revision/URL and how to roll back.
