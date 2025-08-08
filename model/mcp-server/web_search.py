import os
import asyncio
import aiohttp
import re
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
        """Search using Tavily API focusing on security databases."""
        if not self.tavily_api_key:
            return []
        
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["github.com", "nvd.nist.gov", "cisa.gov", 
                               "mitre.org", "cve.org", "security.snyk.io"]
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
    
    def search_cve_specific(self, target: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Search specifically for CVE information in security databases using only Tavily."""
        if not self.tavily_api_key:
            return []
            
        cve_focused_queries = [
            f'site:github.com/advisories "{target}" CVE-',
            f'site:nvd.nist.gov "{target}" CVE-',
            f'site:cisa.gov "{target}" CVE-',
            f'"{target}" CVE-2024',
            f'"{target}" CVE-2023'
        ]
        
        all_results = []
        for query in cve_focused_queries:
            results = self.search_tavily(query, max_results=1)
            for result in results:
                # Only include results that actually contain CVE references
                if 'CVE-' in result['snippet']:
                    result['cve_focused'] = True
                    all_results.append(result)
        
        return all_results[:max_results]
    
    def search(self, query: str, max_results: int = 5, fetch_content: bool = False) -> List[Dict[str, str]]:
        """Perform web search using only Tavily API."""
        all_results = []
        
        # Use only Tavily for high-quality, focused results
        if self.tavily_api_key:
            tavily_results = self.search_tavily(query, max_results)
            all_results.extend(tavily_results)
        else:
            print("Warning: No Tavily API key found. Cannot perform web search.")
            return []
        
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
    """Search for CVEs and security vulnerabilities specific to Docker images and packages."""
    searcher = WebSearcher()
    
    if packages is None:
        packages = []
    
    # Extract image name and version for targeted CVE search
    image_name = ""
    image_version = ""
    if base_image:
        if ":" in base_image:
            image_name, image_version = base_image.split(":", 1)
        else:
            image_name = base_image
            image_version = "latest"
    
    search_summary = "## 🔍 CVE and Security Vulnerability Analysis\n\n"
    found_any_cves = False
    
    # Search 1: Use specialized CVE search for the base image
    if image_name:
        search_summary += f"### Base Image Analysis: `{base_image}`\n\n"
        
        cve_results = searcher.search_cve_specific(image_name, max_results=3)
        
        if cve_results:
            for i, result in enumerate(cve_results, 1):
                search_summary += f"#### CVE Finding {i}\n\n"
                search_summary += f"**Title:** {result['title']}\n\n"
                search_summary += f"**Source:** [{result['url']}]({result['url']})\n\n"
                search_summary += f"**Details:** {result['snippet']}\n\n"
                
                # Extract CVE IDs from snippet
                cve_matches = re.findall(r'CVE-\d{4}-\d+', result['snippet'])
                if cve_matches:
                    search_summary += f"**CVE IDs:** `{', '.join(set(cve_matches))}`\n\n"
                    found_any_cves = True
                
                search_summary += "---\n\n"
        
        # Also try searching with the full image name including registry
        if "/" in image_name:
            base_name = image_name.split("/")[-1]
            additional_results = searcher.search_cve_specific(base_name, max_results=2)
            
            for result in additional_results:
                if result not in cve_results:  # Avoid duplicates
                    search_summary += f"#### Additional CVE Finding\n\n"
                    search_summary += f"**Title:** {result['title']}\n\n"
                    search_summary += f"**Source:** [{result['url']}]({result['url']})\n\n"
                    search_summary += f"**Details:** {result['snippet']}\n\n"
                    
                    cve_matches = re.findall(r'CVE-\d{4}-\d+', result['snippet'])
                    if cve_matches:
                        search_summary += f"**CVE IDs:** `{', '.join(set(cve_matches))}`\n\n"
                        found_any_cves = True
                    
                    search_summary += "---\n\n"
    
    # Search 2: Package-specific CVE vulnerabilities
    if packages:
        search_summary += f"### 📦 Package CVE Analysis\n\n"
        
        for pkg in packages[:3]:  # Limit to top 3 packages
            search_summary += f"#### Package: `{pkg}`\n\n"
            
            pkg_cve_results = searcher.search_cve_specific(pkg, max_results=2)
            
            if pkg_cve_results:
                for result in pkg_cve_results:
                    search_summary += f"- **Source:** [{result['url']}]({result['url']})\n"
                    search_summary += f"- **Finding:** {result['snippet'][:200]}...\n"
                    
                    cve_matches = re.findall(r'CVE-\d{4}-\d+', result['snippet'])
                    if cve_matches:
                        search_summary += f"- **CVEs:** `{', '.join(set(cve_matches))}`\n"
                        found_any_cves = True
                    search_summary += "\n"
            else:
                search_summary += f"- ✅ No specific CVEs found for `{pkg}`\n\n"
    
    # Check if we found any actual CVE information
    if not found_any_cves:
        search_summary += f"""### ℹ️ No Specific CVEs Found

**Search Results:** No specific CVE vulnerabilities were found for `{base_image}` in the major security databases.

**This could mean:**
- ✅ The base image is relatively secure with no known public CVEs
- 🔍 The image may be too new or too specific for indexed vulnerabilities  
- 📦 The vulnerabilities may be in underlying OS packages rather than the application layer

### 🛠️ Recommended Actions

#### Local Scanning Tools
```bash
# Scan with Docker Scout
docker scout cves {base_image}

# Scan with Trivy  
trivy image {base_image}

# Scan with Snyk
snyk container test {base_image}
```

#### Check Official Sources
- 📋 Monitor the official image repository for security updates
- 🔔 Set up notifications from the image maintainer
- 🏷️ Consider using minimal base images like `distroless` or `alpine`

"""
    else:
        search_summary += f"""### ⚠️ CVE Findings Summary

**⚡ Action Required:** CVE references found in security databases.

#### 🎯 Next Steps
1. **Review Impact:** Analyze each CVE for severity and applicability to your use case
2. **Version Check:** Verify if your specific image version is affected
3. **Update Strategy:** Plan update to latest patched version if available
4. **Alternative Images:** Consider switching to alternative base images if critical vulnerabilities exist

#### 🔍 Severity Assessment
- Look for **CRITICAL** and **HIGH** severity CVEs
- Check if vulnerabilities are **actively exploited**
- Verify if patches or workarounds are available

"""
    
    # Add summary recommendations
    search_summary += """
### 🛡️ Security Best Practices

#### 📅 Regular Maintenance
- **Image Updates:** Update to latest base image versions monthly
- **CVE Monitoring:** Set up automated scanning for new CVEs
- **Dependency Management:** Keep all packages updated and remove unnecessary ones

#### 🔧 Security Tools
- **Continuous Scanning:** Use tools like Trivy, Snyk, or Docker Scout
- **CI/CD Integration:** Add vulnerability scanning to your build pipeline
- **Runtime Protection:** Implement runtime security monitoring

#### � Key Resources
- [GitHub Security Advisories](https://github.com/advisories/)
- [NIST National Vulnerability Database](https://nvd.nist.gov/)
- [CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
"""
    
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
