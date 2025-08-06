#!/usr/bin/env python3
"""
Simple test for working MCP functionality - focusing on web search and examples.
"""

import asyncio
import aiohttp
import json

# API Configuration  
API_BASE_URL = "http://localhost:8000"

SAMPLE_DOCKERFILE = """FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]"""

async def test_working_endpoints():
    """Test only the endpoints we know are working."""
    print("🧪 Testing Working MCP Endpoints")
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Web Search (we know this works)
        print("\n🌐 Testing Web Search...")
        async with session.post(f"{API_BASE_URL}/web-search/", json={
            "query": "Docker Python best practices", 
            "max_results": 3
        }) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Web Search Success - {len(result.get('search_results', ''))} chars")
                print(f"Preview: {result.get('search_results', '')[:150]}...")
            else:
                print(f"❌ Web Search Failed - Status: {response.status}")
        
        # Test 2: Dockerfile Examples (should work)
        print("\n📚 Testing Dockerfile Examples...")
        async with session.post(f"{API_BASE_URL}/examples/?technology=Python&use_case=production", json={}) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Examples Success - {len(result.get('examples', ''))} chars")
                print(f"Preview: {result.get('examples', '')[:150]}...")
            else:
                print(f"❌ Examples Failed - Status: {response.status}")
        
        # Test 3: Try a basic analyze call
        print("\n📋 Testing Basic Analysis...")
        async with session.post(f"{API_BASE_URL}/analyze/", json=SAMPLE_DOCKERFILE) as response:
            if response.status == 200:
                print("✅ Basic Analysis Started (streaming)")
                content = ""
                async for chunk in response.content.iter_any():
                    if chunk:
                        chunk_text = chunk.decode('utf-8')
                        content += chunk_text
                        if len(content) > 500:  # Stop after 500 chars
                            print(f"Preview: {content[:500]}...")
                            break
            else:
                print(f"❌ Basic Analysis Failed - Status: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_working_endpoints())
