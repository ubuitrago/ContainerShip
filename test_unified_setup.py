#!/usr/bin/env python3
"""
Test script to verify unified package management is working correctly.
This should be run from the repository root using: pipenv run python test_unified_setup.py
"""

import sys
import os
import importlib
from pathlib import Path

def test_import(module_name, description=""):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name:<25} {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name:<25} {description} - {e}")
        return False

def test_path_accessibility():
    """Test if key project paths are accessible."""
    print("\n📁 Path Accessibility:")
    
    paths = [
        ("api/main.py", "FastAPI application"),
        ("model/mcp-server/server.py", "MCP server"),
        ("model/mcp-server/web_search.py", "Web search module"),
        ("model/mcp-server/rag_doc_chain.py", "RAG system"),
        ("ui/package.json", "Frontend package.json"),
        (".env.example", "Environment template")
    ]
    
    for path, description in paths:
        if Path(path).exists():
            print(f"✅ {path:<30} {description}")
        else:
            print(f"❌ {path:<30} {description} - Not found")

def test_environment_variables():
    """Test environment variable setup."""
    print("\n🔧 Environment Variables:")
    
    env_vars = [
        ("OPENAI_API_KEY", "OpenAI API key", True),
        ("TAVILY_API_KEY", "Tavily API key", False),
        ("CHROMA_PERSIST_DIR", "ChromaDB directory", False)
    ]
    
    for var, description, required in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var:<20} {description} - Set")
        elif required:
            print(f"❌ {var:<20} {description} - Missing (required)")
        else:
            print(f"⚠️  {var:<20} {description} - Not set (optional)")

def main():
    print("🚀 ContainerShip Unified Package Management Test")
    print("=" * 60)
    
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Working Directory: {os.getcwd()}")
    print(f"📦 Python Path: {sys.executable}")
    
    # Test core dependencies
    print("\n📚 Core Dependencies:")
    core_deps = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("openai", "OpenAI API client"),
        ("langchain_openai", "LangChain OpenAI integration"),
        ("langchain_chroma", "LangChain ChromaDB integration"),
        ("chromadb", "ChromaDB vector database"),
    ]
    
    core_passed = 0
    for module, desc in core_deps:
        if test_import(module, desc):
            core_passed += 1
    
    # Test web search dependencies
    print("\n🔍 Web Search Dependencies:")
    web_deps = [
        ("duckduckgo_search", "DuckDuckGo search"),
        ("requests", "HTTP requests"),
        ("bs4", "BeautifulSoup HTML parsing"),
        ("aiohttp", "Async HTTP client"),
    ]
    
    web_passed = 0
    for module, desc in web_deps:
        if test_import(module, desc):
            web_passed += 1
    
    # Test MCP dependencies
    print("\n🔗 MCP Dependencies:")
    mcp_deps = [
        ("mcp", "Model Context Protocol"),
        ("fastmcp", "FastMCP framework"),
    ]
    
    mcp_passed = 0
    for module, desc in mcp_deps:
        if test_import(module, desc):
            mcp_passed += 1
    
    # Test optional dependencies
    print("\n⚡ Optional Dependencies:")
    opt_deps = [
        ("tavily", "Tavily search API"),
        ("pytest", "Testing framework"),
        ("black", "Code formatter"),
        ("flake8", "Code linter"),
    ]
    
    opt_passed = 0
    for module, desc in opt_deps:
        if test_import(module, desc):
            opt_passed += 1
    
    # Test project structure
    test_path_accessibility()
    
    # Test environment
    test_environment_variables()
    
    # Test project modules
    print("\n🏗️  Project Modules:")
    sys.path.insert(0, os.getcwd())
    
    project_modules = []
    
    # Test if we can import from api
    try:
        from api import main as api_main
        print("✅ api.main                   FastAPI application module")
        project_modules.append(True)
    except ImportError as e:
        print(f"❌ api.main                   FastAPI application module - {e}")
        project_modules.append(False)
    
    # Test if we can import MCP server components
    try:
        sys.path.insert(0, "model/mcp-server")
        import web_search
        print("✅ web_search                 Web search functionality")
        project_modules.append(True)
    except ImportError as e:
        print(f"❌ web_search                 Web search functionality - {e}")
        project_modules.append(False)
    
    try:
        import rag_doc_chain
        print("✅ rag_doc_chain              RAG system")
        project_modules.append(True)
    except ImportError as e:
        print(f"❌ rag_doc_chain              RAG system - {e}")
        project_modules.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary:")
    print(f"   Core Dependencies:    {core_passed}/{len(core_deps)}")
    print(f"   Web Search:          {web_passed}/{len(web_deps)}")  
    print(f"   MCP Dependencies:    {mcp_passed}/{len(mcp_deps)}")
    print(f"   Optional:            {opt_passed}/{len(opt_deps)}")
    print(f"   Project Modules:     {sum(project_modules)}/{len(project_modules)}")
    
    total_passed = core_passed + web_passed + mcp_passed + sum(project_modules)
    total_tests = len(core_deps) + len(web_deps) + len(mcp_deps) + len(project_modules)
    
    print(f"   Overall:             {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Your unified environment is ready.")
        print("\n💡 Next steps:")
        print("   - Run 'make dev-api' to start the FastAPI server")
        print("   - Run 'make dev-mcp' to start the MCP server") 
        print("   - Run 'make dev-ui' to start the React frontend")
        print("   - Run 'make dev' to start everything together")
    elif total_passed > total_tests * 0.8:
        print("\n⚠️  Most tests passed. Check the failures above.")
        print("   - Make sure you ran 'pipenv install' from the repository root")
        print("   - Check your .env file for required API keys")
    else:
        print("\n💥 Many tests failed. Please check your setup:")
        print("   1. Run 'pipenv install' from the repository root")
        print("   2. Set up your .env file with required API keys")
        print("   3. Make sure you're in the correct directory")

if __name__ == "__main__":
    main()
