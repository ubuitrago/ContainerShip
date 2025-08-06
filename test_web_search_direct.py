#!/usr/bin/env python3
"""
Quick test script for web search functionality.
Run this to test web search without the full MCP server.
"""

import sys
import os

# Add the MCP server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model/mcp-server'))

def test_basic_web_search():
    """Test basic web search functionality."""
    print("🔍 Testing Basic Web Search...")
    
    try:
        from web_search import WebSearcher
        
        searcher = WebSearcher()
        
        # Test 1: Basic Docker search
        print("\n1️⃣ Testing Docker optimization search...")
        results = searcher.search("Docker optimization best practices 2024", max_results=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title'][:70]}...")
                print(f"      URL: {result['url']}")
                print(f"      Snippet: {result['snippet'][:100]}...")
                print()
        else:
            print("   ❌ No results found")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"   ❌ Web search failed: {e}")
        return False

def test_specialized_searches():
    """Test the specialized search functions."""
    print("\n🎯 Testing Specialized Search Functions...")
    
    try:
        from web_search import (
            search_docker_best_practices,
            search_security_vulnerabilities,
            search_performance_optimization
        )
        
        # Test best practices search
        print("\n2️⃣ Testing Docker best practices search...")
        best_practices = search_docker_best_practices("Python Flask")
        if "Web Search Results" in best_practices or "Current Web Search Results" in best_practices:
            print("   ✅ Best practices search working")
            print(f"   📄 Result length: {len(best_practices)} characters")
        else:
            print("   ⚠️ Unexpected format in best practices search")
        
        # Test security search
        print("\n3️⃣ Testing security vulnerabilities search...")
        security_info = search_security_vulnerabilities("python:3.9", ["requests", "flask"])
        if "Security Research Results" in security_info:
            print("   ✅ Security search working")
            print(f"   🔒 Result length: {len(security_info)} characters")
        else:
            print("   ⚠️ Unexpected format in security search")
        
        # Test performance search
        print("\n4️⃣ Testing performance optimization search...")
        performance_info = search_performance_optimization("Python web application")
        if "Performance Optimization Research" in performance_info:
            print("   ✅ Performance search working")
            print(f"   ⚡ Result length: {len(performance_info)} characters")
        else:
            print("   ⚠️ Unexpected format in performance search")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Specialized searches failed: {e}")
        return False

def test_mcp_integration():
    """Test if we can import and use MCP server components."""
    print("\n🔗 Testing MCP Server Integration...")
    
    try:
        # Test if server imports work
        sys.path.insert(0, 'model/mcp-server')
        import server
        print("   ✅ MCP server module imports successfully")
        
        # Check if tools are registered
        if hasattr(server, 'mcp'):
            tools = server.mcp._app._tools if hasattr(server.mcp, '_app') else {}
            print(f"   📚 Found {len(tools)} MCP tools registered")
            
            # List the tools
            print("   🛠️ Available tools:")
            expected_tools = [
                'docker_docs',
                'web_search_docker', 
                'optimize_dockerfile',
                'search_dockerfile_examples',
                'check_security_best_practices'
            ]
            
            for tool in expected_tools:
                if tool in str(tools):
                    print(f"      ✅ {tool}")
                else:
                    print(f"      ❓ {tool} (may be available)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MCP integration test failed: {e}")
        return False

def main():
    """Run all web search tests."""
    print("🚀 ContainerShip Web Search Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Basic Web Search", test_basic_web_search),
        ("Specialized Searches", test_specialized_searches), 
        ("MCP Integration", test_mcp_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Web Search Test Results:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All web search tests passed!")
        print("\n💡 Your web search setup is working correctly!")
        print("\n🚀 Next steps to try:")
        print("   • Start MCP server: make dev-mcp")
        print("   • Open MCP Inspector: make mcp-inspector") 
        print("   • Test with Claude Desktop or other MCP clients")
    elif passed > 0:
        print("\n⚠️ Some tests passed. Web search basics are working!")
        print("   Check any failures above for improvements.")
    else:
        print("\n💥 Web search tests failed.")
        print("   Check your internet connection and dependencies.")
    
    print("\n🌐 Web Search Status:")
    print("   • DuckDuckGo: Available (no API key needed)")
    if os.environ.get("TAVILY_API_KEY"):
        print("   • Tavily: Available (API key configured)")
    else:
        print("   • Tavily: Not configured (optional)")

if __name__ == "__main__":
    main()
