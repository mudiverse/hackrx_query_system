#!/usr/bin/env python3
"""
Improved test script for HackRx 6.0 API with actual document URL
"""

import requests
import json
import time

def test_hackrx_api():
    """Test the HackRx API endpoint with the actual document URL."""
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/v1/hackrx/run"
    
    # Headers including authorization
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer 273418978cb9f079f5da0cd221de3a8c4ae3d5a9b29477367d3e51c2f3763444"
    }
    
    # Request data with the actual HackRx document URL
    data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "Does this policy cover maternity expenses?"
        ]
    }
    
    print("🚀 Testing HackRx 6.0 API")
    print(f"📄 Document URL: {data['documents'][:50]}...")
    print(f"❓ Questions: {len(data['questions'])}")
    print(f"🔑 Authorization: Bearer token provided")
    print("-" * 50)
    
    try:
        # Make API request
        start_time = time.time()
        response = requests.post(url, json=data, headers=headers, timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        print(f"⏱️  Request completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📝 Answers: {len(result['answers'])}")
            
            for i, answer in enumerate(result['answers'], 1):
                print(f"\n{i}. {answer[:200]}...")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_check():
    """Test the health check endpoint."""
    
    url = "http://127.0.0.1:8000/api/v1/health"
    
    try:
        response = requests.get(url)
        print(f"🏥 Health Check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Service is healthy")
            result = response.json()
            print(f"📋 Service: {result.get('service', 'Unknown')}")
        else:
            print("❌ Service is not healthy")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_status():
    """Test the status endpoint."""
    
    url = "http://127.0.0.1:8000/api/v1/status"
    
    try:
        response = requests.get(url)
        print(f"📊 Status Check: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status', 'Unknown')}")
            print(f"🔍 Index exists: {result.get('index_status', {}).get('index_exists', False)}")
            print(f"🚀 Ready for queries: {result.get('ready_for_queries', False)}")
        else:
            print("❌ Status check failed")
    except Exception as e:
        print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    print("🧪 HackRx 6.0 API Test Suite")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    print()
    
    # Test status
    test_status()
    print()
    
    # Test main API
    test_hackrx_api()
