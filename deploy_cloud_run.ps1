param(
    [string]$projectId,
    [string]$region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "=== CeliGuard ML Cloud Run Deployment ===" -ForegroundColor Cyan

# Check gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "Google Cloud SDK (gcloud) is not installed. Please install it first."
    exit 1
}

# Get Project ID
if (-not $projectId) {
    $projectId = Read-Host "Enter your Google Cloud Project ID"
}
if (-not $projectId) {
    Write-Error "Project ID is required."
    exit 1
}

# Get Region (already handled by default value in param, but we can keep the prompt if we want to allow override when running interactively without args, but for now let's trust the param or prompt if needed. Actually, if I pass it, I don't want to prompt. The original script prompted for region too.)

if ($PSBoundParameters.ContainsKey('region') -eq $false -and -not $projectId) {
    # Only prompt for region if we are running interactively (implied by missing projectId usually) or if we want to be explicit.
    # But to keep it simple, let's just use the default if not provided, or prompt if the user didn't provide ANY args?
    # Let's stick to the param default for region to make it non-interactive if possible.
    # But the original script prompted.
    # Let's just use the param default.
}


$repoName = "celiguard-repo"

Write-Host "`nSetting project to $projectId..." -ForegroundColor Yellow
gcloud config set project $projectId

Write-Host "`nEnabling necessary APIs (Artifact Registry, Cloud Run)..." -ForegroundColor Yellow
gcloud services enable artifactregistry.googleapis.com run.googleapis.com

Write-Host "`nChecking/Creating Artifact Registry repository '$repoName'..." -ForegroundColor Yellow
$repoExists = gcloud artifacts repositories list --location=$region --filter="name:$repoName" --format="value(name)"
if (-not $repoExists) {
    gcloud artifacts repositories create $repoName --repository-format=docker --location=$region --description="Docker repository for CeliGuard ML"
    Write-Host "Repository created." -ForegroundColor Green
} else {
    Write-Host "Repository already exists." -ForegroundColor Green
}

# Build Backend
$backendImage = "$region-docker.pkg.dev/$projectId/$repoName/celiguard-backend"
Write-Host "`nBuilding and pushing Backend image ($backendImage)..." -ForegroundColor Yellow
# Note: We use -f backend/Dockerfile and context . (current directory)
gcloud builds submit --tag $backendImage . -f backend/Dockerfile

# Deploy Backend
Write-Host "`nDeploying Backend to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy celiguard-backend `
    --image $backendImage `
    --platform managed `
    --region $region `
    --allow-unauthenticated `
    --memory 1Gi

# Get Backend URL
$backendUrl = gcloud run services describe celiguard-backend --platform managed --region $region --format 'value(status.url)'
Write-Host "Backend deployed at: $backendUrl" -ForegroundColor Green

# Build Frontend
$frontendImage = "$region-docker.pkg.dev/$projectId/$repoName/celiguard-frontend"
Write-Host "`nBuilding and pushing Frontend image ($frontendImage)..." -ForegroundColor Yellow
gcloud builds submit --tag $frontendImage . -f frontend/Dockerfile

# Deploy Frontend
Write-Host "`nDeploying Frontend to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy celiguard-frontend `
    --image $frontendImage `
    --platform managed `
    --region $region `
    --allow-unauthenticated `
    --set-env-vars API_URL=$backendUrl `
    --memory 512Mi

$frontendUrl = gcloud run services describe celiguard-frontend --platform managed --region $region --format 'value(status.url)'

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Cyan
Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Green
Write-Host "Backend URL:  $backendUrl" -ForegroundColor Green
