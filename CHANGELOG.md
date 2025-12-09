# Changelog

All notable changes to the CeliGuard ML project will be documented in this file.

## [2.0.0] - 2025-12-10

### 🎉 Major Restructuring

#### Added
- **Organized Project Structure**: Separated code into `backend/`, `frontend/`, and `train/` directories
- **Docker Support**: Full containerization with Docker and Docker Compose
- **Individual Dockerfiles**: Separate Dockerfile for each service
- **Shared Models Volume**: Centralized model storage accessible by all services
- **Comprehensive Documentation**:
  - Updated main README.md with Docker instructions
  - Individual README.md for each service
  - QUICKSTART.md for quick deployment
  - ARCHITECTURE.md with system diagrams
  - Component-specific documentation
- **Deployment Scripts**:
  - `deploy.sh` for Linux/Mac
  - `deploy.bat` for Windows
  - Makefile for common operations
- **Environment Configuration**:
  - `.env.example` with all configuration options
  - Environment variable support in all services
- **Docker Ignore Files**: Optimized Docker builds with `.dockerignore`
- **Health Checks**: Docker health checks for all services

#### Changed
- **Backend**: Moved from `api.py` to `backend/app.py`
- **Frontend**: Moved from `frontend.py` to `frontend/app.py`
- **Training**: Moved from `data_and_model.py` to `train/train_model.py`
- **Model Loading**: Updated to use configurable paths via environment variables
- **API URL**: Frontend now uses environment variable for backend URL
- **Dependencies**: Split requirements.txt into service-specific files

#### Improved
- **Deployment**: One-command deployment with `docker-compose up`
- **Isolation**: Each service runs in its own container
- **Networking**: Services communicate via Docker network
- **Scalability**: Architecture supports horizontal scaling
- **Development**: Easier local development with separate services
- **Documentation**: Much more comprehensive and organized

#### Technical Details
- Python 3.11-slim base images for all services
- Multi-stage builds for optimized image sizes
- Volume mounting for model persistence
- CORS configuration for frontend-backend communication
- Automatic model loading on backend startup
- Health check endpoints for monitoring

### 🔧 Configuration
- Backend runs on port 8000
- Frontend runs on port 8501
- Training service runs as a one-time job
- Models stored in `./models` directory
- All services connected via `celiguard-network`

---

## [1.0.0] - Previous Version

### Initial Release
- Basic FastAPI backend (`api.py`)
- Streamlit frontend (`frontend.py`)
- Model training script (`data_and_model.py`)
- Single requirements.txt
- Bash deployment scripts for Render
- Basic README documentation

### Features
- Random Forest ML model
- 13 clinical features
- 3-class risk prediction (Low/Moderate/High)
- REST API with FastAPI
- Interactive Streamlit UI
- Synthetic data generation

---

## Migration Guide (v1.0 → v2.0)

### For Existing Users

1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Remove Old Virtual Environments** (if any)
   ```bash
   rm -rf venv/
   ```

3. **Use Docker Deployment**
   ```bash
   docker-compose up --build
   ```

### File Mapping
- `api.py` → `backend/app.py`
- `frontend.py` → `frontend/app.py`
- `data_and_model.py` → `train/train_model.py`
- `requirements.txt` → Split into service-specific files

### Environment Variables
Old deployment scripts used hardcoded values. New version uses:
- `MODEL_PATH` - Path to model file
- `METADATA_PATH` - Path to metadata file
- `API_URL` - Backend API URL
- `MODEL_OUTPUT_DIR` - Training output directory

---

## Future Roadmap

### Planned Features
- [ ] Model versioning system
- [ ] Prediction history and analytics
- [ ] User authentication
- [ ] Database integration for storing predictions
- [ ] Real-time monitoring dashboard
- [ ] A/B testing for model versions
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline
- [ ] Automated testing suite
- [ ] API rate limiting
- [ ] Caching layer for predictions
- [ ] Model performance tracking
- [ ] Data drift detection
- [ ] Model retraining pipeline

### Under Consideration
- GraphQL API option
- Mobile app (React Native)
- Multi-language support
- Export predictions to PDF
- Integration with EHR systems (for real deployment)
- Real patient data support (with proper validation)

---

## Notes

- This project uses **synthetic data** and is for **research/educational purposes only**
- Not intended for clinical decision-making
- Always consult qualified healthcare professionals for medical decisions
