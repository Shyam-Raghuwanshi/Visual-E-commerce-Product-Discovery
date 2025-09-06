#!/usr/bin/env python3
"""
Simple test script to verify API functionality
"""

import requests
import json

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:8001"
    
    endpoints_to_test = [
        "/",
        "/api/health",
        "/api/categories", 
        "/api/products/categories",
        "/docs"
    ]
    
    print("Testing API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.text[:100]}...")
            else:
                print(f"  Error: {response.text}")
            print()
        except requests.exceptions.ConnectionError:
            print(f"  Error: Could not connect to {url}")
            print()
        except Exception as e:
            print(f"  Error: {str(e)}")
            print()

if __name__ == "__main__":
    test_api_endpoints()
