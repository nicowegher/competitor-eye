#!/usr/bin/env python3
"""
Script simple para testear el webhook de Mercado Pago
"""

import requests
import json

WEBHOOK_URL = "https://competitor-eye.onrender.com/mercado-pago-webhook"

def test_webhook_with_test_data(user_id="test_user_123", plan="esencial"):
    """Testea el webhook con datos de prueba"""
    print(f"🧪 TESTEANDO WEBHOOK CON DATOS DE PRUEBA")
    print(f"Usuario: {user_id}")
    print(f"Plan: {plan}")
    
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": "test_preapproval_123"
        },
        "test_user_id": user_id,
        "test_plan": plan
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"\nEnviando POST a {WEBHOOK_URL}")
    print(f"Body: {json.dumps(webhook_data, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=webhook_data, headers=headers, timeout=30)
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook respondió correctamente")
            print("📋 Verifica en Firestore que el usuario tenga el plan actualizado")
        else:
            print("❌ Webhook falló")
            
    except Exception as e:
        print(f"❌ Error al testear webhook: {e}")

if __name__ == "__main__":
    print("🧪 TEST SIMPLE DEL WEBHOOK")
    print("=" * 40)
    
    # Datos de prueba
    user_id = input("UID de Firebase (o presiona Enter para usar 'test_user_123'): ").strip()
    if not user_id:
        user_id = "test_user_123"
    
    print("\nPlanes disponibles:")
    plans = ["esencial", "pro", "market_leader"]
    for i, plan in enumerate(plans, 1):
        print(f"{i}. {plan}")
    
    plan_choice = input("\nSelecciona el plan (1-3, o presiona Enter para 'esencial'): ").strip()
    
    if plan_choice.isdigit() and 1 <= int(plan_choice) <= 3:
        selected_plan = plans[int(plan_choice) - 1]
    else:
        selected_plan = "esencial"
    
    test_webhook_with_test_data(user_id, selected_plan) 