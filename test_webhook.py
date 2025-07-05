#!/usr/bin/env python3
"""
Script de prueba para verificar el webhook de Mercado Pago
Simula las notificaciones que enviaría Mercado Pago
"""

import requests
import json
import os
from datetime import datetime

# URL del webhook (ajusta según tu dominio)
WEBHOOK_URL = "https://competitor-eye.onrender.com/mercado-pago-webhook"

# IDs de planes de Mercado Pago
MP_PLAN_IDS = {
    "esencial": "2c93808497c462520197d744586508be",
    "pro": "2c93808497c19ac40197d7445b440a20",
    "market_leader": "2c93808497d635430197d7445e1c00bc"
}

def test_webhook_notification(plan_name, user_id="test_user_123"):
    """Simula una notificación de Mercado Pago para un plan específico"""
    
    mp_plan_id = MP_PLAN_IDS[plan_name]
    
    # Simular el body que enviaría Mercado Pago
    webhook_body = {
        "type": "preapproval",
        "data": {
            "id": f"test_preapproval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    }
    
    # Headers que enviaría Mercado Pago
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MercadoPago Webhook/1.0"
    }
    
    print(f"\n=== PROBANDO WEBHOOK PARA PLAN: {plan_name.upper()} ===")
    print(f"URL: {WEBHOOK_URL}")
    print(f"Body: {json.dumps(webhook_body, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_body,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook respondió correctamente")
        else:
            print("❌ Webhook falló")
            
    except Exception as e:
        print(f"❌ Error al probar webhook: {e}")

def test_different_notification_types():
    """Prueba diferentes tipos de notificaciones"""
    
    # 1. Notificación de preapproval (suscripción autorizada)
    print("\n=== PRUEBA 1: Notificación de preapproval ===")
    webhook_body = {
        "type": "preapproval",
        "data": {
            "id": "test_preapproval_authorized"
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_body,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Notificación de subscription_preapproval
    print("\n=== PRUEBA 2: Notificación de subscription_preapproval ===")
    webhook_body = {
        "type": "subscription_preapproval",
        "data": {
            "id": "test_subscription_preapproval"
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_body,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Notificación con body vacío
    print("\n=== PRUEBA 3: Body vacío ===")
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_webhook_endpoint():
    """Prueba que el endpoint esté disponible"""
    print("\n=== PRUEBA DE DISPONIBILIDAD DEL ENDPOINT ===")
    
    try:
        # Cambiar a GET para probar disponibilidad
        response = requests.get(WEBHOOK_URL.replace('/mercado-pago-webhook', '/'), timeout=10)
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ El servidor está funcionando")
        else:
            print("❌ El servidor no responde correctamente")
            
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL WEBHOOK DE MERCADO PAGO")
    print("=" * 60)
    
    # 1. Probar disponibilidad del servidor
    test_webhook_endpoint()
    
    # 2. Probar diferentes tipos de notificaciones
    test_different_notification_types()
    
    # 3. Probar webhook para cada plan
    for plan in ["esencial", "pro", "market_leader"]:
        test_webhook_notification(plan)
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")
    print("\n📋 INSTRUCCIONES:")
    print("1. Revisa los logs del servidor para ver los detalles del webhook")
    print("2. Verifica en Firestore que los usuarios se actualicen correctamente")
    print("3. Asegúrate de que la URL del webhook esté configurada en Mercado Pago") 