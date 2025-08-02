# ContainerShip Makefile
# Run UI and API services

.PHONY: help install install-ui install-api dev dev-ui dev-api stop clean

# Default target
help:
	@echo "ContainerShip Development Commands:"
	@echo ""
	@echo "  make install     - Install dependencies for both UI and API"
	@echo "  make install-ui  - Install UI dependencies"
	@echo "  make install-api - Install API dependencies"
	@echo "  make dev         - Run both UI and API in development mode"
	@echo "  make dev-ui      - Run only the UI development server"
	@echo "  make dev-api     - Run only the API development server"
	@echo "  make stop        - Stop all background processes"
	@echo "  make clean       - Clean build artifacts and dependencies"
	@echo ""

# Install all dependencies
install: install-ui install-api

# Install UI dependencies
install-ui:
	@echo "Installing UI dependencies..."
	cd ui && npm install

# Install API dependencies
install-api:
	@echo "Installing API dependencies..."
	cd api && pipenv install

# Run both UI and API in development mode
dev:
	@echo "Starting ContainerShip development servers..."
	@echo "UI will be available at: http://localhost:5173"
	@echo "API will be available at: http://localhost:8000"
	@echo "Press Ctrl+C to stop all services"
	@make -j2 dev-ui dev-api

# Run UI development server
dev-ui:
	@echo "Starting UI development server..."
	cd ui && npm run dev

# Run API development server  
dev-api:
	@echo "Starting API development server..."
	cd api && pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Stop all background processes (if running in background)
stop:
	@echo "Stopping development servers..."
	@pkill -f "vite" || true
	@pkill -f "uvicorn" || true
	@echo "All services stopped"

# Clean build artifacts and dependencies
clean:
	@echo "Cleaning build artifacts..."
	cd ui && rm -rf node_modules dist
	cd api && pipenv --rm || true
	@echo "Clean complete"
