# Migration Guide: Unified Package Management

## Overview
ContainerShip has been refactored to use a **unified Pipfile** at the root level instead of separate package management systems for the API and model components.

## What Changed

### Before (Old Structure)
```
containership/
├── api/
│   ├── Pipfile                    # API-specific dependencies
│   ├── Pipfile.lock
│   └── ...
├── model/
│   └── mcp-server/               # Used global requirements.txt
│       └── ...
├── requirements.txt              # Global Python requirements
└── Makefile                      # Separate install commands
```

### After (New Structure)
```
containership/
├── Pipfile                       # Unified Python dependencies
├── Pipfile.lock                  # Generated lock file
├── requirements.txt              # Auto-generated for deployment
├── Makefile                      # Unified commands
├── api/                          # No more Pipfile here
└── model/mcp-server/            # Uses root Pipfile
```

## Migration Steps

### 1. Clean Up Old Environment
```bash
# Remove old API pipenv environment
cd api && pipenv --rm

# Remove old virtual environments (if using venv/virtualenv)
rm -rf venv/
rm -rf api/venv/
rm -rf model/venv/
```

### 2. Install New Unified Environment
```bash
# From the root directory
pipenv install

# Or use the Makefile
make install-python
```

### 3. Update Your Development Workflow

#### Old Commands → New Commands

| Old Command | New Command |
|-------------|-------------|
| `cd api && pipenv install` | `pipenv install` |
| `cd api && pipenv run uvicorn main:app --reload` | `make dev-api` or `pipenv run api` |
| `cd model/mcp-server && python server.py` | `make dev-mcp` or `pipenv run mcp-server` |
| `pip install -r requirements.txt` | `pipenv install` |

#### Available Make Commands
```bash
make install           # Install all dependencies (UI + Python)
make install-python    # Install Python dependencies only
make setup-dev         # Install dev dependencies + pre-commit hooks

make dev              # Run UI + API together
make dev-ui           # Run frontend only
make dev-api          # Run backend only
make dev-mcp          # Run MCP server

make mcp-test         # Test MCP functionality
make mcp-inspector    # Debug MCP with inspector
make rag-init         # Initialize RAG knowledge base

make format           # Format code with black
make lint             # Lint code with flake8
make type-check       # Type checking with mypy
make test             # Run tests

make clean            # Clean all build artifacts
```

## Benefits of Unified Package Management

### ✅ Advantages
- **Simplified Dependency Management**: Single source of truth for all Python packages
- **Consistent Environment**: Same Python packages and versions across all components
- **Easier Development**: No need to manage multiple virtual environments
- **Better CI/CD**: Single environment for testing and deployment
- **Dependency Resolution**: Pipenv handles dependency conflicts automatically
- **Development Tools**: Unified linting, formatting, and testing setup

### ⚠️ Considerations
- **Larger Environment**: All dependencies are installed together (but shared)
- **Lock File**: Single lock file means updates affect all components
- **Python Version**: All components must use the same Python version (3.13)

## New Pipfile Features

### Scripts Section
The Pipfile includes convenient scripts you can run with `pipenv run <script>`:

```toml
[scripts]
api = "uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
api-prod = "uvicorn api.main:app --host 0.0.0.0 --port 8000"
mcp-server = "python model/mcp-server/server.py"
mcp-test = "python model/mcp-server/test_web_search.py"
mcp-inspector = "fastmcp dev model/mcp-server/server.py"
rag-init = "python model/mcp-server/rag_doc_chain.py"
format = "black ."
lint = "flake8 ."
type-check = "mypy ."
test = "pytest"
```

### Development Dependencies
Now includes development tools:
- pytest & pytest-asyncio for testing
- black for code formatting  
- flake8 for linting
- mypy for type checking
- pre-commit for git hooks

## Troubleshooting

### Issue: Import Errors
**Solution**: Make sure you're running commands from the root directory and using the unified environment:
```bash
# Instead of cd api && pipenv run python
pipenv run python api/main.py

# Or use the make commands
make dev-api
```

### Issue: Old Environment Conflicts  
**Solution**: Clean up old environments completely:
```bash
make clean
pipenv install
```

### Issue: Path Issues in Scripts
**Solution**: All paths in the Pipfile scripts are relative to the root directory.

### Issue: VS Code Python Interpreter
**Solution**: Update VS Code to use the new pipenv environment:
1. Open Command Palette (Cmd/Ctrl + Shift + P)
2. Select "Python: Select Interpreter"  
3. Choose the pipenv environment (usually shows as `containership-xxx`)

## Deployment Considerations

### Docker
Update your Dockerfile to use the unified Pipfile:
```dockerfile
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --deploy --system
```

### Traditional Deployment
Use the generated requirements.txt:
```bash
pip install -r requirements.txt
```

### Updating requirements.txt
When you add new dependencies via Pipfile:
```bash
pipenv requirements > requirements.txt
```

## Next Steps

1. **Test the Migration**: Run `make mcp-test` to verify everything works
2. **Update CI/CD**: Update your deployment scripts to use the unified Pipfile
3. **Team Communication**: Share this guide with your team
4. **IDE Configuration**: Update your IDE to use the new Python interpreter

The unified package management makes ContainerShip more maintainable and easier to develop. All Python components now share the same environment while maintaining their modular architecture.
