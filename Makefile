# ContainerShip Makefile
# Run UI and API services with unified Python environment

.PHONY: help install install-ui install-python dev dev-ui dev-api dev-mcp stop clean test

# Default target
help:
	@echo "ContainerShip Development Commands:"
	@echo ""
	@echo "  make install      - Install dependencies for both UI and Python (API + MCP)"
	@echo "  make install-ui   - Install UI dependencies"
	@echo "  make install-python - Install Python dependencies (API + MCP + Model)"
	@echo "  make dev          - Run both UI and API in development mode"
	@echo "  make dev-ui       - Run only the UI development server"
	@echo "  make dev-api      - Run only the API development server"
	@echo "  make dev-mcp      - Run the MCP server"
	@echo "  make mcp-test     - Test the MCP server functionality"
	@echo "  make mcp-inspector - Start MCP inspector for debugging"
	@echo "  make rag-init     - Initialize the RAG knowledge base"
	@echo "  make test         - Run Python tests"
	@echo "  make test-setup   - Test unified package management setup"
	@echo "  make format       - Format Python code with black"
	@echo "  make lint         - Lint Python code with flake8"
	@echo "  make stop         - Stop all background processes"
	@echo "  make clean        - Clean build artifacts and dependencies"
	@echo ""

# Install all dependencies
install: install-ui install-python

# Install UI dependencies
install-ui:
	@echo "Installing UI dependencies..."
	cd ui && npm install

# Install Python dependencies (unified for API, MCP, and Model)
install-python:
	@echo "Installing Python dependencies (API + MCP + Model)..."
	pipenv install

# Install development dependencies
install-dev: install-python
	@echo "Installing development dependencies..."
	pipenv install --dev

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
	pipenv run api

# Run API in production mode
api-prod:
	@echo "Starting API in production mode..."
	pipenv run api-prod

# Run MCP server
dev-mcp:
	@echo "Starting MCP server..."
	pipenv run mcp-server

# Test MCP server functionality
mcp-test:
	@echo "Testing MCP server functionality..."
	pipenv run mcp-test

# Start MCP inspector
mcp-inspector:
	@echo "Starting MCP inspector..."
	pipenv run mcp-inspector

# Initialize RAG knowledge base
rag-init:
	@echo "Initializing RAG knowledge base..."
	pipenv run rag-init

# Run tests
test:
	@echo "Running Python tests..."
	pipenv run test

# Test unified setup
test-setup:
	@echo "Testing unified package management setup..."
	pipenv run test-setup

# Format code
format:
	@echo "Formatting Python code..."
	pipenv run format

# Lint code  
lint:
	@echo "Linting Python code..."
	pipenv run lint

# Type checking
type-check:
	@echo "Running type checks..."
	pipenv run type-check

# Stop all background processes (if running in background)
stop:
	@echo "Stopping development servers..."
	@pkill -f "vite" || true
	@pkill -f "uvicorn" || true
	@pkill -f "python.*server.py" || true
	@echo "All services stopped"

# Clean build artifacts and dependencies
clean:
	@echo "Cleaning build artifacts..."
	cd ui && rm -rf node_modules dist
	pipenv --rm || true
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete"

# Development environment setup
setup-dev: install-dev
	@echo "Setting up development environment..."
	pipenv run pre-commit install
	@echo "Development environment ready!"
