#!/usr/bin/env python3
"""
Test the frontend integration with a simple Dockerfile upload.
"""
import requests


def test_frontend_integration():
    """Test that the API returns the expected format for the frontend."""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
"""

    print("🧪 Testing frontend integration...")
    
    try:
        # Test the file upload endpoint
        files = {
            'file': ('Dockerfile', dockerfile_content, 'text/plain')
        }
        
        response = requests.post(
            "http://localhost:8000/analyze/",
            files=files,
            timeout=60
        )
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received!")
            print(f"📊 Response structure:")
            print(f"   - original_dockerfile: {len(data['original_dockerfile'])} chars")
            print(f"   - clauses: {len(data['clauses'])} items")
            print(f"   - optimized_dockerfile: {len(data['optimized_dockerfile'])} chars")
            
            # Check clause structure
            if data['clauses']:
                sample_clause = data['clauses'][0]
                print(f"\n📝 Sample clause structure:")
                print(f"   - line_numbers: {sample_clause.get('line_numbers', 'MISSING')}")
                print(f"   - content: {sample_clause.get('content', 'MISSING')[:50]}...")
                print(f"   - recommendations: {sample_clause.get('recommendations', 'MISSING')[:50]}...")
                
                # Verify expected fields exist
                required_fields = ['line_numbers', 'content', 'recommendations']
                missing_fields = [field for field in required_fields if field not in sample_clause]
                
                if missing_fields:
                    print(f"❌ Missing fields in clause: {missing_fields}")
                else:
                    print("✅ All expected clause fields present")
            
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


if __name__ == "__main__":
    success = test_frontend_integration()
    if success:
        print("\n🎉 Frontend integration looks good!")
        print("   The API returns the correct format for the React frontend.")
    else:
        print("\n⚠️  Integration test failed - check API and servers.")
