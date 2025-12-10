.PHONY: help build up down train backend frontend logs clean test

help:
	@echo "CeliGuard ML - Makefile Commands"
	@echo "================================="
	@echo "make build       - Build all Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make train       - Run training service only"
	@echo "make backend     - Run backend service only"
	@echo "make frontend    - Run frontend service only"
	@echo "make logs        - View logs from all services"
	@echo "make clean       - Remove containers, images, and volumes"
	@echo "make test        - Test the API"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:8501"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

train:
	docker-compose up train

backend:
	docker-compose up -d backend

frontend:
	docker-compose up -d frontend

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all
	rm -rf models/*.pkl

test:
	@echo "Testing API health..."
	@curl -s http://localhost:8000/health | python -m json.tool
