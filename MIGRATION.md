# Migration Guide: v1.0 → v2.0

This guide helps you migrate from the old monolithic structure to the new Dockerized architecture.

## Overview of Changes

### Old Structure (v1.0)
```
celiguard-ml/
├── api.py                    # Backend
├── frontend.py               # Frontend
├── data_and_model.py        # Training
├── requirements.txt          # All dependencies
├── celiac_risk_model.pkl    # Model
├── model_metadata.pkl       # Metadata
└── start.sh                 # Deployment
```

### New Structure (v2.0)
```
celiguard-ml/
├── backend/                  # Backend service
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Frontend service
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── train/                    # Training service
│   ├── train_model.py
│   ├── requirements.txt
│   └── Dockerfile
├── models/                   # Shared models
└── docker-compose.yml        # Orchestration
```

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Create a backup of your current working directory
cd ..
cp -r celiguard-ml celiguard-ml-backup
cd celiguard-ml
```

### Step 2: Verify Git Status

```bash
# Check current status
git status

# Commit any pending changes
git add .
git commit -m "Backup before restructuring"
```

### Step 3: Pull New Structure

```bash
# Pull the latest changes
git pull origin main

# Or if starting fresh
git fetch origin
git reset --hard origin/main
```

### Step 4: Verify New Structure

```bash
# Check that new directories exist
ls -la backend/
ls -la frontend/
ls -la train/
ls -la models/

# Verify Docker Compose file
cat docker-compose.yml
```

### Step 5: Test the New Setup

```bash
# Build and start all services
docker-compose up --build

# In another terminal, check if services are running
docker-compose ps

# Check logs
docker-compose logs
```

### Step 6: Verify Functionality

1. **Check Frontend**: http://localhost:8501
2. **Check Backend**: http://localhost:8000/health
3. **Check API Docs**: http://localhost:8000/docs
4. **Test Prediction**: Fill form and click "Predict Risk"

### Step 7: Clean Up Old Files (Optional)

Once you've verified everything works:

```bash
# Remove old files
rm api.py
rm frontend.py
rm data_and_model.py
rm requirements.txt
rm start.sh
rm render_start.sh

# Move old model files to models directory (if not already there)
mv celiac_risk_model.pkl models/ 2>/dev/null || true
mv model_metadata.pkl models/ 2>/dev/null || true

# Commit the cleanup
git add .
git commit -m "Remove legacy files after migration"
```

## Code Changes Reference

### Backend Changes

**Old (`api.py`):**
```python
model = joblib.load('celiac_risk_model.pkl')
metadata = joblib.load('model_metadata.pkl')
```

**New (`backend/app.py`):**
```python
model_path = os.getenv('MODEL_PATH', '../models/celiac_risk_model.pkl')
metadata_path = os.getenv('METADATA_PATH', '../models/model_metadata.pkl')
model = joblib.load(model_path)
metadata = joblib.load(metadata_path)
```

### Frontend Changes

**Old (`frontend.py`):**
```python
API_URL = os.getenv("API_URL", "http://localhost:8000")
```

**New (`frontend/app.py`):**
```python
# Same, but now configurable via Docker Compose
API_URL = os.getenv("API_URL", "http://localhost:8000")
# In Docker: API_URL = "http://backend:8000"
```

### Training Changes

**Old (`data_and_model.py`):**
```python
joblib.dump(final_model, 'celiac_risk_model.pkl')
joblib.dump(metadata, 'model_metadata.pkl')
```

**New (`train/train_model.py`):**
```python
output_dir = os.getenv('MODEL_OUTPUT_DIR', '../models')
os.makedirs(output_dir, exist_ok=True)
model_filename = os.path.join(output_dir, 'celiac_risk_model.pkl')
metadata_filename = os.path.join(output_dir, 'model_metadata.pkl')
joblib.dump(final_model, model_filename)
joblib.dump(metadata, metadata_filename)
```

## Environment Variables

### Old Deployment
Environment variables were set in shell scripts:
```bash
export API_URL="http://localhost:8000"
```

### New Deployment
Environment variables are set in `docker-compose.yml`:
```yaml
environment:
  - API_URL=http://backend:8000
  - MODEL_PATH=/app/../models/celiac_risk_model.pkl
```

Or in `.env` file:
```bash
API_URL=http://backend:8000
MODEL_PATH=/app/../models/celiac_risk_model.pkl
```

## Deployment Changes

### Old Deployment

**Local:**
```bash
# Terminal 1
uvicorn api:app --reload

# Terminal 2
streamlit run frontend.py
```

**Render:**
```bash
bash render_start.sh
```

### New Deployment

**Local (Docker):**
```bash
docker-compose up
```

**Local (Manual):**
```bash
# Terminal 1
cd backend && uvicorn app:app --reload

# Terminal 2
cd frontend && streamlit run app.py
```

**Production:**
```bash
docker-compose up -d
```

## Troubleshooting Migration Issues

### Issue: "Model not found"

**Solution:**
```bash
# Ensure models are in the correct directory
ls -la models/

# If missing, retrain
docker-compose up train

# Or manually
cd train
python train_model.py
```

### Issue: "Cannot connect to backend"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check Docker network
docker network ls
docker network inspect celiguard-ml_celiguard-network

# Restart services
docker-compose restart
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill the process or change ports in docker-compose.yml
# Change:
ports:
  - "8001:8000"  # Use 8001 instead of 8000
  - "8502:8501"  # Use 8502 instead of 8501
```

### Issue: "Old virtual environment conflicts"

**Solution:**
```bash
# Remove old virtual environments
rm -rf venv/
rm -rf backend/venv/
rm -rf frontend/venv/
rm -rf train/venv/

# Use Docker instead
docker-compose up --build
```

## Rollback Procedure

If you need to rollback to the old version:

```bash
# Stop new services
docker-compose down

# Restore from backup
cd ..
rm -rf celiguard-ml
mv celiguard-ml-backup celiguard-ml
cd celiguard-ml

# Or use git
git reset --hard <previous-commit-hash>
```

## Verification Checklist

After migration, verify:

- [ ] All three services start successfully
- [ ] Frontend accessible at http://localhost:8501
- [ ] Backend accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns OK: http://localhost:8000/health
- [ ] Can make predictions through frontend
- [ ] Model files exist in models/ directory
- [ ] Docker containers are running: `docker-compose ps`
- [ ] No errors in logs: `docker-compose logs`

## Benefits of New Structure

✅ **Easier Deployment**: One command instead of multiple terminals
✅ **Better Isolation**: Each service in its own container
✅ **Scalability**: Can scale services independently
✅ **Consistency**: Same environment everywhere (dev, staging, prod)
✅ **Documentation**: Better organized and comprehensive
✅ **Maintainability**: Clear separation of concerns
✅ **Portability**: Works on any system with Docker

## Getting Help

If you encounter issues during migration:

1. Check the logs: `docker-compose logs`
2. Review QUICKSTART.md for common issues
3. Check ARCHITECTURE.md for system details
4. Verify STRUCTURE.txt for correct file organization
5. Contact the development team

## Post-Migration Tasks

After successful migration:

1. Update any CI/CD pipelines to use Docker
2. Update deployment documentation
3. Train team members on new structure
4. Update monitoring and logging configurations
5. Test backup and restore procedures
6. Update production deployment scripts

## Summary

The migration from v1.0 to v2.0 brings significant improvements in:
- **Architecture**: Modular and scalable
- **Deployment**: Simplified with Docker
- **Documentation**: Comprehensive and organized
- **Development**: Better developer experience

The new structure is production-ready and follows modern best practices for containerized applications.
