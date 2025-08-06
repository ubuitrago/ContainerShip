# Docker Expert MCP Server with Web Search

An enhanced Model Context Protocol (MCP) server that provides comprehensive Docker expertise by combining local documentation with real-time web search capabilities.

## Features

### Core Capabilities
- **Local RAG System**: Query extensive Docker documentation using semantic search
- **Web Search Integration**: Access current Docker best practices, security updates, and optimization techniques
- **Dockerfile Analysis**: Comprehensive analysis combining local knowledge with current web research
- **Security Scanning**: Check Dockerfiles against current security best practices
- **Performance Optimization**: Get up-to-date performance tuning recommendations
- **Example Search**: Find current Dockerfile templates and examples for specific technologies

### Available Tools

1. **`docker_docs`** - Query local Docker documentation knowledge base
2. **`web_search_docker`** - Search the web for current Docker information
3. **`optimize_dockerfile`** - Comprehensive Dockerfile optimization with web research
4. **`search_dockerfile_examples`** - Find Dockerfile examples for specific technologies
5. **`check_security_best_practices`** - Security analysis with current threat information

## Setup

### Prerequisites
- Python 3.13 (managed via unified Pipfile)
- OpenAI API key
- (Optional) Tavily API key for enhanced web search

### Installation

1. **Install unified dependencies** (from repository root):
```bash
# Using make (recommended)
make install-python

# Or manually with pipenv
pipenv install
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env file with your API keys
```

3. **Initialize the knowledge base** (first run):
```bash
# Using make (from repository root)
make rag-init

# Or manually with pipenv
pipenv run rag-init
```

### Configuration

#### Required Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for LLM and embeddings

#### Optional Environment Variables
- `TAVILY_API_KEY`: For enhanced web search (fallback to DuckDuckGo if not provided)
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB storage (default: `chroma_db`)

## Usage

### Starting the Server (from repository root)
```bash
# Using make (recommended)
make dev-mcp

# Or manually with pipenv
pipenv run mcp-server
```

The server will start on `http://127.0.0.1:8000`

### Testing the Setup
```bash
# Test all MCP functionality
make mcp-test

# Or manually
pipenv run mcp-test
```

### Debugging with MCP Inspector
```bash
# Start MCP inspector
make mcp-inspector

# Or manually
pipenv run mcp-inspector
```

### Example Tool Calls

#### Basic Docker Documentation Query
```json
{
  "tool": "docker_docs",
  "arguments": {
    "question": "How do I optimize Docker image layers?"
  }
}
```

#### Web Search for Current Information
```json
{
  "tool": "web_search_docker",
  "arguments": {
    "query": "Docker security vulnerabilities 2024",
    "max_results": 3
  }
}
```

#### Comprehensive Dockerfile Analysis
```json
{
  "tool": "optimize_dockerfile",
  "arguments": {
    "dockerfile_content": "FROM ubuntu:20.04\nRUN apt-get update && apt-get install -y python3\nCOPY . /app\nWORKDIR /app\nCMD python3 app.py",
    "technology_stack": "Python Flask"
  }
}
```

#### Security Best Practices Check
```json
{
  "tool": "check_security_best_practices",
  "arguments": {
    "dockerfile_content": "FROM node:16\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nEXPOSE 3000\nCMD [\"npm\", \"start\"]"
  }
}
```

#### Find Dockerfile Examples
```json
{
  "tool": "search_dockerfile_examples",
  "arguments": {
    "technology": "React TypeScript",
    "use_case": "production"
  }
}
```

## Integration with AI Systems

This MCP server can be integrated with:
- **Claude Desktop**: Add to your `claude_desktop_config.json`
- **VS Code**: Use with MCP-compatible extensions
- **Custom AI Applications**: Via HTTP or MCP protocol

### Claude Desktop Configuration
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docker-expert": {
      "command": "pipenv",
      "args": ["run", "mcp-server"],
      "cwd": "/path/to/containership",
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Architecture

### Components

1. **RAG System** (`rag_doc_chain.py`)
   - ChromaDB vector store for Docker documentation
   - OpenAI embeddings for semantic search
   - GPT-4 for response generation

2. **Web Search** (`web_search.py`)
   - DuckDuckGo search (no API key required)
   - Tavily search (enhanced results with API key)
   - Content extraction and summarization

3. **MCP Server** (`server.py`)
   - FastMCP framework for protocol handling
   - Tool registration and routing
   - Response formatting and error handling

### Data Flow
1. Client sends tool request via MCP protocol
2. Server processes request and determines information sources needed
3. Local RAG system queries documentation knowledge base
4. Web search fetches current information (if applicable)
5. LLM synthesizes comprehensive response
6. Formatted result returned to client

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `pipenv install` from the repository root
2. **API Key Errors**: Check that `OPENAI_API_KEY` is set in your `.env` file at the repository root
3. **ChromaDB Issues**: Delete `chroma_db` directory and reinitialize with `make rag-init`
4. **Web Search Failures**: Web search will gracefully fall back if APIs are unavailable
5. **Path Issues**: Make sure you're running commands from the repository root directory

### Debugging
- Use `make mcp-test` to run comprehensive functionality tests
- Enable verbose logging by setting environment variables
- Check network connectivity for web search functionality
- Verify API key permissions and quotas

## Contributing

To add new tools or enhance existing functionality:

1. Add new tool functions to `server.py` with appropriate `@mcp.tool()` decorators
2. Implement supporting functions in relevant modules
3. Update documentation and examples
4. Test thoroughly with different input scenarios

## License

This project is part of the ContainerShip repository. See the main repository for license information.
