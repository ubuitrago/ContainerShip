#!/usr/bin/env python3
"""
Test the unified /analyze/ endpoint with both JSON and file upload methods.
"""
import requests
import io
import time


def test_json_method():
    """Test the unified endpoint with JSON input."""
    dockerfile_content = """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
"""

    print("🧪 Testing /analyze/ endpoint with JSON input...")
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/",
            json={"content": dockerfile_content},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JSON method works!")
            print(f"   Original length: {len(data['original_dockerfile'])}")
            print(f"   Clauses found: {len(data['clauses'])}")
            print(f"   Optimized length: {len(data['optimized_dockerfile'])}")
            return True
        else:
            print(f"❌ JSON method failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ JSON method error: {e}")
        return False


def test_file_upload_method():
    """Test the unified endpoint with file upload."""
    dockerfile_content = """FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
"""

    print("\n🧪 Testing /analyze/ endpoint with file upload...")
    
    try:
        # Create a file-like object
        files = {
            'file': ('Dockerfile', dockerfile_content, 'text/plain')
        }
        
        response = requests.post(
            "http://localhost:8000/analyze/",
            files=files,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File upload method works!")
            print(f"   Original length: {len(data['original_dockerfile'])}")
            print(f"   Clauses found: {len(data['clauses'])}")
            print(f"   Optimized length: {len(data['optimized_dockerfile'])}")
            return True
        else:
            print(f"❌ File upload method failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ File upload method error: {e}")
        return False


def test_error_handling():
    """Test error handling when neither method is provided."""
    print("\n🧪 Testing error handling...")
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze/",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Error handling works correctly!")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing the unified /analyze/ endpoint...")
    print("⏳ Waiting for servers to be ready...")
    time.sleep(2)
    
    json_success = test_json_method()
    file_success = test_file_upload_method() 
    error_success = test_error_handling()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"  JSON method: {'✅ PASS' if json_success else '❌ FAIL'}")
    print(f"  File upload: {'✅ PASS' if file_success else '❌ FAIL'}")
    print(f"  Error handling: {'✅ PASS' if error_success else '❌ FAIL'}")
    
    if json_success and file_success and error_success:
        print("\n🎉 Unified endpoint works perfectly!")
        print("   Frontend can now use a single endpoint with either:")
        print("   • JSON: POST {\"content\": \"dockerfile\"}")  
        print("   • File: POST with multipart/form-data")
    else:
        print("\n⚠️  Some tests failed. Check server logs.")


if __name__ == "__main__":
    main()
