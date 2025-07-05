#!/usr/bin/env python3
"""
Script de debug para el webhook de Mercado Pago
"""

import requests
import json

WEBHOOK_URL = "https://competitor-eye.onrender.com/mercado-pago-webhook"

def test_webhook_step_by_step():
    """Testea el webhook paso a paso"""
    print("🔍 DEBUG DEL WEBHOOK")
    print("=" * 40)
    
    # Test 1: Body vacío
    print("\n1. Test con body vacío:")
    try:
        response = requests.post(WEBHOOK_URL, json={}, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Body mínimo
    print("\n2. Test con body mínimo:")
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": "test_123"
        }
    }
    try:
        response = requests.post(WEBHOOK_URL, json=webhook_data, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test completo
    print("\n3. Test completo con datos de prueba:")
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": "test_preapproval_123"
        },
        "test_user_id": "test_user_123",
        "test_plan": "esencial"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=webhook_data, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_health_endpoint():
    """Testea el endpoint de health"""
    print("\n🏥 Test del endpoint de health:")
    try:
        response = requests.get("https://competitor-eye.onrender.com/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_webhook_step_by_step() 