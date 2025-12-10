# Deploy CeliGuard ML to Google Cloud Run

This script automates the deployment of the CeliGuard ML application to Google Cloud Run.

## Prerequisites
- Google Cloud SDK (`gcloud`) installed and authenticated (`gcloud auth login`).
- A Google Cloud Project created.

## Usage
Run this script in PowerShell:
`.\deploy_cloud_run.ps1`

You will be prompted to enter your Google Cloud Project ID and a region (default: us-central1).

## Script Content
The script performs the following steps:
1.  **Configuration**: Sets up project ID and region.
2.  **Enable APIs**: Enables Artifact Registry and Cloud Run APIs.
3.  **Create Repository**: Creates a Docker repository in Artifact Registry if it doesn't exist.
4.  **Build Images**: Builds backend and frontend images using Cloud Build and pushes them to the repository.
5.  **Deploy Backend**: Deploys the backend service to Cloud Run.
6.  **Deploy Frontend**: Deploys the frontend service to Cloud Run, linking it to the backend URL.

## Manual Deployment
If you prefer to run commands manually:

```bash
# Set variables
$PROJECT_ID="your-project-id"
$REGION="us-central1"
$REPO_NAME="celiguard-repo"

# Enable APIs
gcloud services enable artifactregistry.googleapis.com run.googleapis.com

# Create Repository
gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION

# Build Backend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/celiguard-backend . -f backend/Dockerfile

# Deploy Backend
gcloud run deploy celiguard-backend --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/celiguard-backend --platform managed --region $REGION --allow-unauthenticated

# Get Backend URL
$BACKEND_URL=$(gcloud run services describe celiguard-backend --platform managed --region $REGION --format 'value(status.url)')

# Build Frontend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/celiguard-frontend . -f frontend/Dockerfile

# Deploy Frontend
gcloud run deploy celiguard-frontend --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/celiguard-frontend --platform managed --region $REGION --allow-unauthenticated --set-env-vars API_URL=$BACKEND_URL
```
