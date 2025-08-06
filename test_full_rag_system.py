#!/usr/bin/env python3
"""
Full RAG + Web Search Test - showcasing the complete enhanced MCP system.
"""

import asyncio
import aiohttp

DOCKERFILE_SAMPLE = """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
USER node
CMD ["npm", "start"]"""

async def test_full_enhanced_system():
    """Test the fully enhanced system with RAG + Web Search."""
    print("🚀 ContainerShip Full Enhanced System Test")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test comprehensive analysis
        print("🔍 Testing Comprehensive Analysis with RAG + Web Search...")
        async with session.post(
            "http://localhost:8000/analyze/comprehensive/",
            json={"content": DOCKERFILE_SAMPLE, "technology": "Node.js"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ SUCCESS!")
                print(f"🔍 Technology: {result.get('technology')}")
                print(f"📋 Clauses: {len(result.get('clauses', []))}")
                
                # Show overall optimization (now powered by RAG!)
                optimization = result.get('overall_optimization_suggestions', '')[:400]
                print(f"\n⚡ Overall Optimization (RAG-powered):")
                print(optimization + "..." if len(optimization) == 400 else optimization)
                
                # Show security analysis (now powered by RAG!)
                security = result.get('overall_security_analysis', '')[:400]
                print(f"\n🔒 Security Analysis (RAG-powered):")
                print(security + "..." if len(security) == 400 else security)
                
                # Show examples (web search powered)
                examples = result.get('example_dockerfiles', '')[:300]
                print(f"\n📚 Example Dockerfiles (Web Search):")
                print(examples + "..." if len(examples) == 300 else examples)
                
                # Show individual clause analysis
                if result.get('clauses'):
                    clause = result['clauses'][0]  # First clause
                    print(f"\n📝 Sample Clause Analysis:")
                    print(f"   Content: {clause.get('content', 'N/A')}")
                    print(f"   RAG Recommendations: {clause.get('recommendations', 'N/A')[:200]}...")
                    if clause.get('web_insights'):
                        print(f"   Web Insights: {clause.get('web_insights', 'N/A')[:200]}...")
                
            else:
                print(f"❌ FAILED: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_full_enhanced_system())
