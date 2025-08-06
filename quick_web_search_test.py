#!/usr/bin/env python3
"""
Simple web search test - run this anytime to verify web search is working.
Usage: pipenv run python quick_web_search_test.py
"""

import sys
import os

# Add MCP server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model/mcp-server'))

def test_web_search():
    """Quick test of web search functionality."""
    print("🔍 Quick Web Search Test")
    print("-" * 30)
    
    try:
        from web_search import WebSearcher
        
        searcher = WebSearcher()
        
        # Test search
        print("🔎 Searching: 'Docker best practices 2024'")
        results = searcher.search("Docker best practices 2024", max_results=2)
        
        if results:
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   🔗 {result['url']}")
                print(f"   📄 {result['snippet'][:100]}...")
            
            print(f"\n🎉 Web search is working!")
            return True
        else:
            print("❌ No results found")
            return False
            
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False

if __name__ == "__main__":
    test_web_search()
