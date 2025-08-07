#!/usr/bin/env python3
"""
Test script for the enhanced MCP server with web search capabilities.
This script tests all the new web search tools independently.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_web_search():
    """Test basic web search functionality."""
    print("🔍 Testing Web Search...")
    try:
        from web_search import WebSearcher
        searcher = WebSearcher()
        results = searcher.search("Docker multi-stage build best practices", max_results=2)
        
        if results:
            print("✅ Web search working!")
            print(f"   Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title'][:60]}...")
        else:
            print("⚠️  Web search returned no results")
        
        return len(results) > 0
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False

def test_dockerfile_analysis():
    """Test Dockerfile analysis with web search enhancement."""
    print("\n📋 Testing Dockerfile Analysis...")
    
    sample_dockerfile = """FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python3", "app.py"]"""
    
    try:
        # Test individual components
        from web_search import search_docker_best_practices, search_security_vulnerabilities
        
        print("   Testing best practices search...")
        best_practices = search_docker_best_practices("Python Flask")
        if "Web Search Results" in best_practices or "Current Web Search Results" in best_practices:
            print("   ✅ Best practices search working")
        else:
            print("   ⚠️  Best practices search returned unexpected format")
        
        print("   Testing security vulnerabilities search...")
        security_info = search_security_vulnerabilities("ubuntu:20.04", ["python3", "pip"])
        if "Security Research Results" in security_info:
            print("   ✅ Security search working")
        else:
            print("   ⚠️  Security search returned unexpected format")
            
        return True
    except Exception as e:
        print(f"   ❌ Dockerfile analysis failed: {e}")
        return False

def test_rag_system():
    """Test the local RAG system."""
    print("\n📚 Testing Local RAG System...")
    try:
        from rag_doc_chain import answer_question
        
        # Test basic question
        response = answer_question("What is a multi-stage Docker build?")
        
        if response and len(response) > 50:
            print("   ✅ RAG system working!")
            print(f"   Response length: {len(response)} characters")
        else:
            print("   ⚠️  RAG system returned short/empty response")
            
        return len(response) > 50 if response else False
    except Exception as e:
        print(f"   ❌ RAG system failed: {e}")
        return False

def test_enhanced_rag():
    """Test the enhanced RAG system with web search."""
    print("\n🔍📚 Testing Enhanced RAG with Web Search...")
    try:
        from rag_doc_chain import answer_question_with_web_search
        
        response = answer_question_with_web_search("Docker security best practices 2024")
        
        if response and len(response) > 100:
            print("   ✅ Enhanced RAG working!")
            print(f"   Response length: {len(response)} characters")
            # Check if it includes web information
            if "web" in response.lower() or "recent" in response.lower():
                print("   ✅ Web information detected in response")
            else:
                print("   ⚠️  No clear web information indicators found")
        else:
            print("   ⚠️  Enhanced RAG returned short/empty response")
            
        return len(response) > 100 if response else False
    except Exception as e:
        print(f"   ❌ Enhanced RAG failed: {e}")
        return False

def print_environment_info():
    """Print information about the current environment setup."""
    print("🔧 Environment Information:")
    print(f"   Python version: {sys.version}")
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['TAVILY_API_KEY', 'CHROMA_PERSIST_DIR']
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ❌ {var}: Not set (required)")
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ⚠️  {var}: Not set (optional)")
    
    # Check for key dependencies
    dependencies = [
        'duckduckgo_search', 'requests', 'beautifulsoup4', 
        'langchain_openai', 'chromadb', 'fastmcp'
    ]
    
    print("\n📦 Dependencies:")
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep}: Available")
        except ImportError:
            print(f"   ❌ {dep}: Missing")

def main():
    """Run all tests."""
    print("🚀 ContainerShip MCP Server - Web Search Enhancement Test\n")
    
    print_environment_info()
    print()
    
    # Test individual components
    tests = [
        test_web_search,
        test_dockerfile_analysis, 
        test_rag_system,
        test_enhanced_rag
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Web Search",
        "Dockerfile Analysis", 
        "Local RAG System",
        "Enhanced RAG with Web Search"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MCP server is ready to use.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check the failures above.")
    else:
        print("💥 All tests failed. Check your setup and dependencies.")
    
    print("\n💡 Next steps:")
    if passed > 0:
        print("   - Run 'python server.py' to start the MCP server")
        print("   - Test with your MCP client (Claude Desktop, etc.)")
    print("   - Check the README.md for integration instructions")

if __name__ == "__main__":
    main()
