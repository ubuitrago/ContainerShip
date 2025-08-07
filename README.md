# ContainerShip
Web-App Container optimizer via LLMs with **Enhanced Web Search Capabilities**

ContainerShip now combines local Docker documentation with real-time web search to provide the most current Docker optimization recommendations, security updates, and best practices.

## ✨ New Features

### 🔍 Web Search Integration
- **Real-time Docker Information**: Access current best practices, security vulnerabilities, and optimization techniques
- **Multi-source Search**: DuckDuckGo (no API key) + optional Tavily API for enhanced results
- **Intelligent Synthesis**: Combines local documentation with current web research

### 🛡️ Enhanced Security Analysis
- Current vulnerability scanning and threat intelligence
- Up-to-date security best practices from the web
- Base image and package-specific security research

### ⚡ Advanced Optimization
- Performance optimization based on current industry practices
- Technology-specific recommendations with web research
- Multi-stage build optimizations with latest techniques

### 📚 Comprehensive Knowledge Base
- Local RAG system with extensive Docker documentation
- Web-enhanced responses for current information
- Dockerfile examples and templates from current sources

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI        │    │  MCP Server     │
│   (Frontend)    │◄──►│   (Backend)      │◄──►│  (AI Engine)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                    ┌────────────────────┼────────────────────┐
                                    │                    │                    │
                              ┌─────▼─────┐    ┌────────▼────────┐    ┌──────▼──────┐
                              │Local RAG  │    │  Web Search     │    │   LLM       │
                              │(ChromaDB) │    │ (DuckDuckGo/    │    │  (GPT-4)    │
                              │           │    │  Tavily)        │    │             │
                              └───────────┘    └─────────────────┘    └─────────────┘
```

# Development

## 🔧 Unified Package Management
ContainerShip now uses a **unified Pipfile** at the root level for all Python dependencies (API, MCP server, and ML models), making development and deployment much simpler.

### Quick Start
First run the following.
```bash
make install
```

Then run the next two commands in separate terminals.

```bash
make dev-mcp
make dev
```

### Development Environment
```bash
# Set up complete development environment (includes pre-commit hooks)
make setup-dev

# Run all services
make dev              # UI + API
make dev-ui           # Frontend only  
make dev-api          # Backend API only
make dev-mcp          # MCP server only
```

## Front-End (React)
```bash
make dev-ui
# Or manually:
cd ui && npm run dev
```

## Backend (FastAPI)
The API now uses the unified Python environment:
```bash
make dev-api
# Or manually:
pipenv run api
```

The API will be available at:
- API Root: http://localhost:8000/
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## MCP Server with Web Search
The MCP server uses the same unified environment:

### Quick Start
```bash
# Test the enhanced MCP server
make mcp-test

# Start the MCP server
make dev-mcp

# Debug with MCP inspector
make mcp-inspector

# Initialize knowledge base (first run)
make rag-init
```

### Manual Commands
```bash
# All using the unified pipenv environment
pipenv run mcp-server       # Start MCP server
pipenv run mcp-test         # Test functionality  
pipenv run mcp-inspector    # Debug interface
pipenv run rag-init         # Initialize RAG system
```

### Environment Configuration
### Environment Configuration
1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Configure your API keys in `.env`**:
   - `OPENAI_API_KEY` (required)
   - `TAVILY_API_KEY` (optional, for enhanced web search)

### Enhanced Tools Available

1. **`docker_docs`** - Query local Docker documentation
2. **`web_search_docker`** - Real-time web search for Docker information  
3. **`optimize_dockerfile`** - Comprehensive analysis with web research
4. **`search_dockerfile_examples`** - Find current examples and templates
5. **`check_security_best_practices`** - Security analysis with current threat intel

### MCP Inspector Testing
Start the MCP Inspector to test the enhanced functionality:
```bash
make mcp-inspector
```

You may get a request to download a Node.js package, say yes (this is likely the inspector). Eventually, your browser should open a new tab for MCP Inspector. 

Ensure the settings of the server are correct by referring to the values in the settings. They should be set to the following:
* `Transport Type` -> `Streamable HTTP`
* `URL` -> `http://localhost:8000/mcp`

Now, you should be ready to connect to the running server and test it. 

Click the "connect" button on the bottom left. After successfully connecting, you should be able to view all the enhanced tools under the __Tools__ tab.

<img src="docs/img/MCP-Inspector.png" max_width="700px">

## Development Tools

### Code Quality
```bash
make format      # Format code with black
make lint        # Lint with flake8  
make type-check  # Type checking with mypy
make test        # Run tests
```

## Testing

Use the bad Dockerfile
SORUCE: https://www.infoq.com/articles/docker-size-dive/