import os
import asyncio
import aiohttp
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
import dotenv
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv.load_dotenv(PROJECT_ROOT + "/.env")

class WebSearcher:
    """Handles web searches for Docker and containerization information."""
    
    def __init__(self):
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        self.ddgs = DDGS()
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using DuckDuckGo (no API key required)."""
        try:
            results = []
            ddgs_results = self.ddgs.text(query, max_results=max_results)
            
            for result in ddgs_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })
            
            return results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def search_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using Tavily API (if API key is available)."""
        if not self.tavily_api_key:
            return []
        
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["docker.com", "docs.docker.com", "stackoverflow.com", 
                               "github.com", "medium.com", "dev.to"]
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                    "source": "tavily"
                })
            
            return results
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def get_page_content(self, url: str, max_length: int = 2000) -> str:
        """Fetch and extract text content from a webpage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
        except Exception as e:
            print(f"Error fetching page content from {url}: {e}")
            return ""
    
    def search(self, query: str, max_results: int = 5, fetch_content: bool = False) -> List[Dict[str, str]]:
        """Perform web search using available search engines."""
        all_results = []
        
        # Try Tavily first (if available), then DuckDuckGo
        if self.tavily_api_key:
            tavily_results = self.search_tavily(query, max_results // 2)
            all_results.extend(tavily_results)
        
        ddg_results = self.search_duckduckgo(query, max_results - len(all_results))
        all_results.extend(ddg_results)
        
        # Optionally fetch full page content
        if fetch_content:
            for result in all_results:
                if result["url"]:
                    content = self.get_page_content(result["url"])
                    if content:
                        result["content"] = content
        
        return all_results[:max_results]

def search_docker_best_practices(dockerfile_context: str = "") -> str:
    """Search for current Docker best practices and optimization techniques."""
    searcher = WebSearcher()
    
    # Construct search query based on Dockerfile context
    if dockerfile_context:
        query = f"Docker Dockerfile optimization best practices 2024 2025 {dockerfile_context}"
    else:
        query = "Docker Dockerfile optimization best practices security performance 2024 2025"
    
    results = searcher.search(query, max_results=3, fetch_content=True)
    
    search_summary = "## Current Web Search Results:\n\n"
    
    for i, result in enumerate(results, 1):
        search_summary += f"### {i}. {result['title']}\n"
        search_summary += f"**Source**: {result['url']}\n"
        search_summary += f"**Summary**: {result['snippet']}\n"
        
        if result.get('content'):
            search_summary += f"**Key Content**: {result['content'][:500]}...\n"
        
        search_summary += "\n"
    
    return search_summary

def search_security_vulnerabilities(base_image: str = "", packages: List[str] = None) -> str:
    """Search for security vulnerabilities related to Docker images and packages."""
    searcher = WebSearcher()
    
    if packages is None:
        packages = []
    
    # Build search query for security information
    query_parts = ["Docker security vulnerabilities", "container security", "2024 2025"]
    
    if base_image:
        query_parts.append(f'"{base_image}" vulnerabilities')
    
    if packages:
        query_parts.extend([f'"{pkg}" security' for pkg in packages[:3]])  # Limit to avoid too long query
    
    query = " ".join(query_parts)
    
    results = searcher.search(query, max_results=3, fetch_content=True)
    
    search_summary = "## Security Research Results:\n\n"
    
    for i, result in enumerate(results, 1):
        search_summary += f"### {i}. {result['title']}\n"
        search_summary += f"**Source**: {result['url']}\n"
        search_summary += f"**Summary**: {result['snippet']}\n"
        
        if result.get('content'):
            search_summary += f"**Security Info**: {result['content'][:500]}...\n"
        
        search_summary += "\n"
    
    return search_summary

def search_performance_optimization(technology_stack: str = "") -> str:
    """Search for performance optimization techniques for specific technology stacks."""
    searcher = WebSearcher()
    
    query = f"Docker container performance optimization {technology_stack} build time image size 2024"
    
    results = searcher.search(query, max_results=3, fetch_content=True)
    
    search_summary = "## Performance Optimization Research:\n\n"
    
    for i, result in enumerate(results, 1):
        search_summary += f"### {i}. {result['title']}\n"
        search_summary += f"**Source**: {result['url']}\n"
        search_summary += f"**Summary**: {result['snippet']}\n"
        
        if result.get('content'):
            search_summary += f"**Optimization Tips**: {result['content'][:500]}...\n"
        
        search_summary += "\n"
    
    return search_summary

if __name__ == "__main__":
    # Test the web search functionality
    searcher = WebSearcher()
    results = searcher.search("Docker multi-stage build optimization 2024")
    
    print("Search Results:")
    for result in results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Snippet: {result['snippet'][:100]}...")
        print("---")
