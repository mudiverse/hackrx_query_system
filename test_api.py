#!/usr/bin/env python3
"""
Test script for HackRx 6.0 API
"""

import requests
import json
import time

def test_hackrx_api():
    """Test the HackRx API endpoint."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/hackrx/run"
    
    # Sample request data
    data = {
        "documents": "https://example.com/sample-policy.pdf",  # Replace with actual URL
        "questions": [
            "What is the grace period for premium payment?",
            "Does this policy cover maternity expenses?",
            "What is the waiting period for pre-existing conditions?"
        ]
    }
    
    print("🚀 Testing HackRx 6.0 API")
    print(f"📄 Document URL: {data['documents']}")
    print(f"❓ Questions: {len(data['questions'])}")
    print("-" * 50)
    
    try:
        # Make API request
        start_time = time.time()
        response = requests.post(url, json=data, timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        print(f"⏱️  Request completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📝 Answers: {len(result['answers'])}")
            
            for i, answer in enumerate(result['answers'], 1):
                print(f"\n{i}. {answer[:100]}...")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_check():
    """Test the health check endpoint."""
    
    url = "http://localhost:8000/api/v1/health"
    
    try:
        response = requests.get(url)
        print(f"🏥 Health Check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Service is healthy")
        else:
            print("❌ Service is not healthy")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🧪 HackRx 6.0 API Test Suite")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    print()
    
    # Test main API
    test_hackrx_api()
