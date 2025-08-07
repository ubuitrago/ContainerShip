"""
Enhanced MCP client integration for the ContainerShip API.
This module provides functions to interact with the web search enhanced MCP server.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional

class EnhancedMCPClient:
    """Client for the enhanced MCP server with web search capabilities."""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/mcp/tools/{tool_name}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def optimize_dockerfile_comprehensive(self, dockerfile_content: str, technology_stack: str = "") -> Dict[str, Any]:
        """Get comprehensive Dockerfile optimization with web research."""
        return await self.call_tool("optimize_dockerfile", {
            "dockerfile_content": dockerfile_content,
            "technology_stack": technology_stack
        })
    
    async def search_docker_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web for Docker-related information."""
        return await self.call_tool("web_search_docker", {
            "query": query,
            "max_results": max_results
        })
    
    async def check_security(self, dockerfile_content: str) -> Dict[str, Any]:
        """Perform security analysis with current web research."""
        return await self.call_tool("check_security_best_practices", {
            "dockerfile_content": dockerfile_content
        })
    
    async def find_examples(self, technology: str, use_case: str = "") -> Dict[str, Any]:
        """Find Dockerfile examples for specific technologies."""
        return await self.call_tool("search_dockerfile_examples", {
            "technology": technology,
            "use_case": use_case
        })
    
    async def query_docs(self, question: str) -> Dict[str, Any]:
        """Query local Docker documentation."""
        return await self.call_tool("docker_docs", {
            "question": question
        })

# Convenience functions for the FastAPI backend
async def get_enhanced_dockerfile_analysis(dockerfile_content: str, technology_stack: str = "") -> str:
    """
    Get enhanced Dockerfile analysis combining local docs and web search.
    This function can be called from the FastAPI backend.
    """
    async with EnhancedMCPClient() as client:
        result = await client.optimize_dockerfile_comprehensive(dockerfile_content, technology_stack)
        
        if "error" in result:
            # Fallback to basic analysis if web search fails
            basic_result = await client.query_docs(f"Analyze this Dockerfile: {dockerfile_content}")
            return basic_result.get("content", "Analysis failed")
        
        return result.get("content", "No analysis available")

async def search_current_docker_practices(query: str) -> str:
    """Search for current Docker practices and return formatted results."""
    async with EnhancedMCPClient() as client:
        result = await client.search_docker_web(query)
        
        if "error" in result:
            return f"Web search failed: {result['error']}"
        
        return result.get("content", "No search results available")

async def get_dockerfile_security_analysis(dockerfile_content: str) -> str:
    """Get comprehensive security analysis with current threat intelligence."""
    async with EnhancedMCPClient() as client:
        result = await client.check_security(dockerfile_content)
        
        if "error" in result:
            # Fallback to basic security analysis
            basic_result = await client.query_docs(f"What are the security issues in this Dockerfile: {dockerfile_content}")
            return basic_result.get("content", "Security analysis failed")
        
        return result.get("content", "No security analysis available")

# Example usage functions for testing
async def test_enhanced_features():
    """Test the enhanced MCP server features."""
    sample_dockerfile = """FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]"""
    
    async with EnhancedMCPClient() as client:
        print("🔍 Testing web search...")
        web_result = await client.search_docker_web("Node.js Docker optimization 2024")
        print(f"Web search result: {len(web_result.get('content', ''))} characters")
        
        print("\n📋 Testing comprehensive analysis...")
        analysis_result = await client.optimize_dockerfile_comprehensive(sample_dockerfile, "Node.js Express")
        print(f"Analysis result: {len(analysis_result.get('content', ''))} characters")
        
        print("\n🛡️ Testing security analysis...")
        security_result = await client.check_security(sample_dockerfile)
        print(f"Security result: {len(security_result.get('content', ''))} characters")
        
        print("\n📚 Testing example search...")
        example_result = await client.find_examples("React TypeScript", "production")
        print(f"Example result: {len(example_result.get('content', ''))} characters")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_enhanced_features())
