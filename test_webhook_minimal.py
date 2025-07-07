#!/usr/bin/env python3
"""
Test minimalista del webhook
"""

import requests
import json

WEBHOOK_URL = "https://competitor-eye.onrender.com/mercado-pago-webhook"

def test_minimal():
    """Test minimalista"""
    print("🧪 TEST MINIMALISTA DEL WEBHOOK")
    
    # Test más simple posible
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": "test_123"
        },
        "test_user_id": "test_user_123",
        "test_plan": "esencial"
    }
    
    print(f"Enviando a: {WEBHOOK_URL}")
    print(f"Data: {json.dumps(webhook_data, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
        else:
            print("❌ FAILED!")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_minimal() 