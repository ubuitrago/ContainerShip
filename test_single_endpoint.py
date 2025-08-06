#!/usr/bin/env python3
"""
Test script for the simplified single endpoint API.
Tests the new /analyze/ endpoint that returns original, clauses, and optimized Dockerfile.
"""
import requests
import json
import time


def test_analyze_endpoint():
    """Test the new single /analyze/ endpoint."""
    # Sample Dockerfile for testing
    dockerfile_content = """FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
"""

    print("🧪 Testing /analyze/ endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/",
            json={"content": dockerfile_content},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Response received!")
            print(f"📁 Keys in response: {list(data.keys())}")
            
            # Check for required fields
            required_fields = ["original_dockerfile", "clauses", "optimized_dockerfile"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("\n📋 Original Dockerfile length:", len(data["original_dockerfile"]))
            print("🔍 Number of clauses analyzed:", len(data["clauses"]))
            print("⚡ Optimized Dockerfile length:", len(data["optimized_dockerfile"]))
            
            # Show a sample clause
            if data["clauses"]:
                sample_clause = data["clauses"][0]
                print(f"\n📝 Sample clause analysis:")
                print(f"   Line: {sample_clause.get('line_number', 'N/A')}")
                print(f"   Instruction: {sample_clause.get('instruction', 'N/A')}")
                print(f"   Recommendation: {sample_clause.get('recommendation', 'N/A')[:100]}...")
            
            # Show first few lines of optimized Dockerfile
            optimized_lines = data["optimized_dockerfile"].split('\n')[:5]
            print(f"\n⚡ First 5 lines of optimized Dockerfile:")
            for i, line in enumerate(optimized_lines, 1):
                print(f"   {i}: {line}")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_upload_endpoint():
    """Test the /upload/ endpoint with a temporary file."""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
"""
    
    print("\n🧪 Testing /upload/ endpoint...")
    
    try:
        # Create a temporary file-like object
        files = {
            'file': ('Dockerfile', dockerfile_content, 'text/plain')
        }
        
        response = requests.post(
            "http://localhost:8000/upload/",
            files=files,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload endpoint works!")
            print(f"📁 Keys in response: {list(data.keys())}")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing the simplified API endpoints...")
    
    # Wait a moment for the server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test the main analyze endpoint
    analyze_success = test_analyze_endpoint()
    
    # Test the upload endpoint
    upload_success = test_upload_endpoint()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"  /analyze/ endpoint: {'✅ PASS' if analyze_success else '❌ FAIL'}")
    print(f"  /upload/ endpoint: {'✅ PASS' if upload_success else '❌ FAIL'}")
    
    if analyze_success and upload_success:
        print("\n🎉 All tests passed! The API is ready for frontend integration.")
    else:
        print("\n⚠️  Some tests failed. Check the API server logs.")


if __name__ == "__main__":
    main()
