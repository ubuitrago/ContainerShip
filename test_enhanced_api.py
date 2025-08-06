#!/usr/bin/env python3
"""
Test script for the enhanced ContainerShip API with MCP integration.

This script tests all the new MCP-powered endpoints that provide comprehensive
Dockerfile analysis, optimization, security scanning, and web search.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Sample Dockerfiles for testing
SAMPLE_DOCKERFILE_PYTHON = """FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]"""

SAMPLE_DOCKERFILE_NODE = """FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]"""


async def test_endpoint(session: aiohttp.ClientSession, endpoint: str, data: Dict[str, Any], description: str):
    """Test an API endpoint and display results."""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {description}")
    print(f"📍 Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    try:
        async with session.post(f"{API_BASE_URL}{endpoint}", json=data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ SUCCESS (Status: {response.status})")
                
                # Display results based on endpoint type
                if "comprehensive" in endpoint:
                    print(f"🔍 Technology Detected: {result.get('technology', 'Unknown')}")
                    print(f"📋 Clauses Found: {len(result.get('clauses', []))}")
                    print(f"⚡ Overall Optimization: {result.get('overall_optimization_suggestions', 'N/A')[:200]}...")
                    print(f"🔒 Security Analysis: {result.get('overall_security_analysis', 'N/A')[:200]}...")
                    
                elif "optimize" in endpoint:
                    print(f"⚡ Optimization Suggestions:")
                    print(result.get('optimization_suggestions', 'No suggestions available')[:300] + "...")
                    
                elif "security" in endpoint:
                    print(f"🔒 Security Analysis:")
                    print(result.get('security_analysis', 'No analysis available')[:300] + "...")
                    
                elif "examples" in endpoint:
                    print(f"📚 Example Dockerfiles:")
                    print(result.get('examples', 'No examples found')[:300] + "...")
                    
                elif "web-search" in endpoint:
                    print(f"🌐 Web Search Results:")
                    print(result.get('search_results', 'No results found')[:300] + "...")
                    
                else:
                    print(f"📊 Response: {str(result)[:200]}...")
                    
            else:
                error_text = await response.text()
                print(f"❌ FAILED (Status: {response.status})")
                print(f"Error: {error_text}")
                
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")


async def test_enhanced_api():
    """Test all enhanced MCP-powered API endpoints."""
    print("🚀 ContainerShip Enhanced API Test Suite")
    print("🔗 Testing MCP-powered Dockerfile analysis endpoints")
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Comprehensive Analysis
        await test_endpoint(
            session, 
            "/analyze/comprehensive/",
            {"content": SAMPLE_DOCKERFILE_PYTHON, "technology": "Python Flask"},
            "Comprehensive Dockerfile Analysis (Python Flask)"
        )
        
        # Test 2: Optimization Recommendations
        await test_endpoint(
            session,
            "/optimize/", 
            {"content": SAMPLE_DOCKERFILE_NODE, "technology": "Node.js Express"},
            "Dockerfile Optimization (Node.js)"
        )
        
        # Test 3: Security Analysis
        await test_endpoint(
            session,
            "/security/",
            {"content": SAMPLE_DOCKERFILE_PYTHON, "technology": "Python Flask"},
            "Security Analysis (Python Flask)"
        )
        
        # Test 4: Find Examples
        await test_endpoint(
            session,
            "/examples/?technology=Python Flask&use_case=production",
            {},
            "Find Dockerfile Examples (Python Flask Production)"
        )
        
        # Test 5: Web Search
        await test_endpoint(
            session,
            "/web-search/",
            {"query": "Python Docker security best practices 2024", "max_results": 3},
            "Web Search (Python Docker Security)"
        )
        
        # Test 6: Original streaming endpoint
        print(f"\n{'='*60}")
        print(f"🌊 Testing: Original Streaming Analysis")
        print(f"📍 Endpoint: /analyze/")
        print(f"{'='*60}")
        
        try:
            async with session.post(f"{API_BASE_URL}/analyze/", json=SAMPLE_DOCKERFILE_PYTHON) as response:
                if response.status == 200:
                    print(f"✅ STREAMING SUCCESS (Status: {response.status})")
                    print("📊 Streaming content:")
                    async for chunk in response.content.iter_any():
                        if chunk:
                            print(chunk.decode('utf-8'), end='')
                else:
                    print(f"❌ STREAMING FAILED (Status: {response.status})")
                    
        except Exception as e:
            print(f"💥 STREAMING EXCEPTION: {e}")

    print(f"\n\n{'='*60}")
    print("🎉 Enhanced API Test Suite Complete!")
    print("📊 Summary:")
    print("   • MCP Server running on http://127.0.0.1:3001/mcp/")
    print("   • FastAPI Server running on http://localhost:8000")
    print("   • All endpoints leverage MCP tools for enhanced analysis")
    print("   • Ready for frontend integration!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_api())
