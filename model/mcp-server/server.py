from fastmcp import FastMCP
from rag_doc_chain import answer_question
from web_search import (
    search_docker_best_practices, 
    search_security_vulnerabilities, 
    search_performance_optimization,
    WebSearcher
)
import re
from typing import List

# Create MCP server instance
mcp = FastMCP("Docker Expert with Web Search")

@mcp.tool()
def docker_docs(question: str) -> str:
    """
    RAG tool to answer questions about Docker using a knowledge base of Docker documentation.

    Args:
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    return answer_question(question)

@mcp.tool()
def web_search_docker(query: str, max_results: int = 5) -> str:
    """
    Search the web for current Docker-related information, best practices, and solutions.
    
    Args:
        query (str): The search query related to Docker, containerization, or DevOps.
        max_results (int): Maximum number of search results to return (default: 5).
    
    Returns:
        str: Formatted search results with titles, URLs, and summaries.
    """
    searcher = WebSearcher()
    results = searcher.search(query, max_results=max_results)
    
    if not results:
        return f"No web search results found for query: {query}"
    
    formatted_results = f"## Web Search Results for: {query}\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_results += f"### {i}. {result['title']}\n"
        formatted_results += f"**URL**: {result['url']}\n"
        formatted_results += f"**Summary**: {result['snippet']}\n"
        formatted_results += f"**Source**: {result['source']}\n\n"
    
    return formatted_results

@mcp.tool()
def optimize_dockerfile(dockerfile_content: str, technology_stack: str = "") -> str:
    """
    Analyze a Dockerfile and provide comprehensive optimization recommendations using both 
    local documentation and current web search results.
    
    Args:
        dockerfile_content (str): The content of the Dockerfile to analyze.
        technology_stack (str): Optional description of the technology stack (e.g., "Python Flask", "Node.js Express").
    
    Returns:
        str: Comprehensive analysis and optimization recommendations.
    """
    # Extract key information from Dockerfile
    base_image = ""
    packages = []
    
    lines = dockerfile_content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.upper().startswith('FROM'):
            base_image = line.split()[-1] if len(line.split()) > 1 else ""
        elif line.upper().startswith('RUN'):
            # Extract package names (basic regex for common package managers)
            if 'apt-get install' in line or 'apt install' in line:
                packages.extend(re.findall(r'(?:apt-get install|apt install)[^&]*?(\w+(?:-\w+)*)', line))
            elif 'yum install' in line or 'dnf install' in line:
                packages.extend(re.findall(r'(?:yum install|dnf install)[^&]*?(\w+(?:-\w+)*)', line))
            elif 'pip install' in line:
                packages.extend(re.findall(r'pip install[^&]*?(\w+(?:-\w+)*)', line))
            elif 'npm install' in line:
                packages.extend(re.findall(r'npm install[^&]*?(\w+(?:-\w+)*)', line))
    
    # Get analysis from local RAG system
    rag_analysis = answer_question(f"Analyze this Dockerfile and provide optimization recommendations: {dockerfile_content}")
    
    # Get current best practices from web search
    web_best_practices = search_docker_best_practices(f"{base_image} {technology_stack}".strip())
    
    # Get security information
    web_security = search_security_vulnerabilities(base_image, packages[:5])  # Limit packages for search
    
    # Get performance optimization tips
    web_performance = search_performance_optimization(technology_stack)
    
    # Combine all analyses
    comprehensive_analysis = f"""# Comprehensive Dockerfile Analysis

## Local Documentation Analysis
{rag_analysis}

---

{web_best_practices}

---

{web_security}

---

{web_performance}

## Summary and Priority Recommendations

Based on both documentation and current web research, here are the top priority optimizations:

1. **Security First**: Update to latest base images and scan for vulnerabilities
2. **Multi-stage Builds**: Use multi-stage builds to reduce final image size
3. **Layer Optimization**: Combine RUN commands and clean up package caches
4. **Non-root User**: Run containers as non-root user for security
5. **Build Cache**: Order instructions from least to most frequently changing
6. **Current Best Practices**: Follow latest 2024-2025 Docker recommendations from web research

## Dockerfile Context Analysis
- **Base Image**: {base_image if base_image else 'Not detected'}
- **Technology Stack**: {technology_stack if technology_stack else 'Not specified'}
- **Detected Packages**: {', '.join(packages[:10]) if packages else 'None detected'}
"""
    
    return comprehensive_analysis

@mcp.tool()
def search_dockerfile_examples(technology: str, use_case: str = "") -> str:
    """
    Search for Dockerfile examples and templates for specific technologies and use cases.
    
    Args:
        technology (str): The technology or framework (e.g., "Python Flask", "React", "Java Spring").
        use_case (str): Optional specific use case (e.g., "production", "development", "microservice").
    
    Returns:
        str: Search results with Dockerfile examples and best practices.
    """
    query = f"Dockerfile example {technology} {use_case} best practices template 2024"
    
    searcher = WebSearcher()
    results = searcher.search(query, max_results=4, fetch_content=True)
    
    formatted_results = f"## Dockerfile Examples for {technology}\n\n"
    
    if use_case:
        formatted_results += f"**Use Case**: {use_case}\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_results += f"### {i}. {result['title']}\n"
        formatted_results += f"**URL**: {result['url']}\n"
        formatted_results += f"**Summary**: {result['snippet']}\n"
        
        if result.get('content'):
            formatted_results += f"**Key Content**: {result['content'][:800]}...\n"
        
        formatted_results += "\n---\n\n"
    
    return formatted_results

@mcp.tool()
def check_security_best_practices(dockerfile_content: str) -> str:
    """
    Check Dockerfile against current security best practices using both local knowledge and web research.
    
    Args:
        dockerfile_content (str): The Dockerfile content to security check.
    
    Returns:
        str: Security analysis and recommendations.
    """
    # Get security analysis from RAG system
    security_question = f"What are the security issues and recommendations for this Dockerfile: {dockerfile_content}"
    rag_security = answer_question(security_question)
    
    # Extract base image for focused security search
    base_image = ""
    lines = dockerfile_content.strip().split('\n')
    for line in lines:
        if line.strip().upper().startswith('FROM'):
            base_image = line.split()[-1] if len(line.split()) > 1 else ""
            break
    
    # Get current security information from web
    web_security = search_security_vulnerabilities(base_image)
    
    # Also search for general security best practices
    searcher = WebSearcher()
    general_security = searcher.search("Docker container security best practices 2024 2025", max_results=3)
    
    formatted_general = "## Current Security Best Practices:\n\n"
    for i, result in enumerate(general_security, 1):
        formatted_general += f"### {i}. {result['title']}\n"
        formatted_general += f"**URL**: {result['url']}\n"
        formatted_general += f"**Summary**: {result['snippet']}\n\n"
    
    return f"""# Security Analysis Report

## Local Documentation Security Analysis
{rag_security}

---

{web_security}

---

{formatted_general}

## Security Checklist
- [ ] Using minimal base image (distroless, alpine, or scratch when possible)
- [ ] Running as non-root user
- [ ] No secrets in Dockerfile or image layers
- [ ] Using specific image tags, not 'latest'
- [ ] Scanning images for vulnerabilities
- [ ] Using multi-stage builds to exclude build tools from final image
- [ ] Regularly updating base images and dependencies
"""

if __name__ == "__main__":
    # Launch the MCP server with the FastMCP interface
    mcp.run(transport="http", host="127.0.0.1", port=3001)