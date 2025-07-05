#!/usr/bin/env python3
"""
Test del endpoint de debug
"""

import requests
import json

DEBUG_URL = "https://competitor-eye.onrender.com/debug"

def test_debug_endpoint():
    """Testea el endpoint de debug"""
    print("🧪 TEST DEL ENDPOINT DE DEBUG")
    
    test_data = {
        "test": True,
        "message": "Debug test"
    }
    
    print(f"Enviando POST a: {DEBUG_URL}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            DEBUG_URL,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Debug endpoint funcionando!")
        else:
            print("❌ Debug endpoint falló!")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_debug_endpoint() 