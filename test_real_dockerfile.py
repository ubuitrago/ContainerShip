#!/usr/bin/env python3
"""
Test the new API structure with a real Dockerfile example.
"""
import requests
import json


def main():
    # Real-world Node.js Dockerfile
    dockerfile = """FROM node:16-alpine

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production

# Start the application
CMD ["npm", "start"]
"""

    print("🧪 Testing real-world Dockerfile analysis...")
    
    try:
        print("📡 Sending request...")
        response = requests.post(
            "http://localhost:8000/analyze/",
            json={"content": dockerfile},
            timeout=90  # Extended timeout for comprehensive analysis
        )
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Analysis completed successfully!")
            print(f"\n📊 Analysis Results:")
            print(f"   Original length: {len(data['original_dockerfile'])} chars")
            print(f"   Clauses analyzed: {len(data['clauses'])}")
            print(f"   Optimized length: {len(data['optimized_dockerfile'])} chars")
            
            print(f"\n📋 Clause Details:")
            for i, clause in enumerate(data['clauses'], 1):
                print(f"   {i}. Line {clause.get('line_number', '?')}: {clause.get('instruction', 'N/A')}")
                if clause.get('recommendation'):
                    print(f"      💡 {clause['recommendation'][:80]}...")
                print()
            
            print(f"🔧 Optimized Dockerfile Preview:")
            opt_lines = data['optimized_dockerfile'].split('\n')
            for i, line in enumerate(opt_lines[:10], 1):
                print(f"   {i:2}: {line}")
            if len(opt_lines) > 10:
                print(f"   ... ({len(opt_lines) - 10} more lines)")
            
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - this is expected for comprehensive analysis")
        print("   The analysis includes RAG search, web search, and AI optimization")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 The single endpoint API is working perfectly!")
        print("   Ready for frontend integration!")
    else:
        print("\n⚠️  Test had issues - check server logs")
