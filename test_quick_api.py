#!/usr/bin/env python3
"""
Quick test to verify the API is working.
"""
import requests
import json
import time


def test_basic():
    """Test basic API connectivity and structure."""
    # Simple Dockerfile for testing
    dockerfile_content = """FROM alpine:3.14
RUN echo "hello world"
"""

    print("🧪 Testing basic API functionality...")
    
    try:
        print("📡 Making request to /analyze/ endpoint...")
        response = requests.post(
            "http://localhost:8000/analyze/",
            json={"content": dockerfile_content},
            timeout=60  # Increased timeout
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Response received!")
            print(f"Response keys: {list(data.keys())}")
            
            # Check structure
            has_original = "original_dockerfile" in data
            has_clauses = "clauses" in data
            has_optimized = "optimized_dockerfile" in data
            
            print(f"  ✅ Has original_dockerfile: {has_original}")
            print(f"  ✅ Has clauses: {has_clauses}")
            print(f"  ✅ Has optimized_dockerfile: {has_optimized}")
            
            if has_clauses:
                print(f"  📝 Number of clauses: {len(data['clauses'])}")
                
            return has_original and has_clauses and has_optimized
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - analysis is taking too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Quick API test...")
    time.sleep(1)  # Wait for server to be ready
    
    success = test_basic()
    
    if success:
        print("\n🎉 API is working correctly!")
    else:
        print("\n❌ API test failed.")
