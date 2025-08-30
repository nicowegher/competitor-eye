#!/usr/bin/env python3
"""
Script para crear una suscripción de prueba en Mercado Pago
"""

import os
import mercadopago
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Configurar SDK de Mercado Pago
sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])

# IDs de planes
MP_PLAN_IDS = {
    "esencial": "2c93808497c462520197d744586508be",
    "pro": "2c93808497c19ac40197d7445b440a20",
    "market_leader": "2c93808497d635430197d7445e1c00bc"
}

def create_test_subscription(plan_name, user_id, user_email):
    """Crea una suscripción de prueba"""
    print(f"\n=== CREANDO SUSCRIPCIÓN DE PRUEBA PARA PLAN: {plan_name.upper()} ===")
    
    plan_id = MP_PLAN_IDS[plan_name]
    
    # Datos de la suscripción
    subscription_data = {
        "preapproval_plan_id": plan_id,
        "payer_email": user_email,
        "external_reference": user_id,  # Este es el UID de Firebase
        "back_url": "https://hotelrateshopper.com/dashboard",
        "reason": f"Suscripción de prueba - Plan {plan_name}"
    }
    
    print("Datos de la suscripción:")
    print(json.dumps(subscription_data, indent=2))
    
    try:
        # Crear la suscripción
        result = sdk.preapproval().create(subscription_data)
        
        print(f"\nStatus Code: {result['status']}")
        
        if result['status'] == 201 and result['response']:
            subscription = result['response']
            print("✅ Suscripción creada exitosamente:")
            print(f"   ID: {subscription.get('id')}")
            print(f"   Status: {subscription.get('status')}")
            print(f"   User ID: {subscription.get('external_reference')}")
            print(f"   Plan ID: {subscription.get('preapproval_plan_id')}")
            print(f"   Email: {subscription.get('payer_email')}")
            print(f"   Init Point: {subscription.get('init_point')}")
            
            print(f"\n📋 Para testear el webhook:")
            print(f"1. Ve a: {subscription.get('init_point')}")
            print(f"2. Completa el pago (usa tarjeta de prueba)")
            print(f"3. Mercado Pago enviará el webhook automáticamente")
            print(f"4. O usa Postman con el ID: {subscription.get('id')}")
            
            return subscription.get('id')
        else:
            print("❌ Error al crear suscripción")
            print(f"Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error al crear suscripción: {e}")
        return None

def test_webhook_with_real_subscription(subscription_id):
    """Testea el webhook con una suscripción real"""
    import requests
    
    print(f"\n=== TESTEANDO WEBHOOK CON SUSCRIPCIÓN REAL ===")
    print(f"Subscription ID: {subscription_id}")
    
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": subscription_id
        }
    }
    
    webhook_url = "https://competitor-eye.onrender.com/mercado-pago-webhook"
    
    print(f"Enviando POST a {webhook_url}")
    print(f"Body: {json.dumps(webhook_data, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook respondió correctamente")
        else:
            print("❌ Webhook falló")
            
    except Exception as e:
        print(f"❌ Error al testear webhook: {e}")

if __name__ == "__main__":
    print("🧪 CREACIÓN DE SUSCRIPCIÓN DE PRUEBA")
    print("=" * 50)
    
    # Datos de prueba
    user_id = input("Ingresa el UID de Firebase del usuario: ").strip()
    user_email = input("Ingresa el email del usuario: ").strip()
    
    if not user_id or not user_email:
        print("❌ Se requieren UID y email")
        exit(1)
    
    print("\nPlanes disponibles:")
    for i, plan in enumerate(MP_PLAN_IDS.keys(), 1):
        print(f"{i}. {plan}")
    
    plan_choice = input("\nSelecciona el plan (1-3): ").strip()
    plan_names = list(MP_PLAN_IDS.keys())
    
    if plan_choice.isdigit() and 1 <= int(plan_choice) <= 3:
        selected_plan = plan_names[int(plan_choice) - 1]
        
        # Crear suscripción
        subscription_id = create_test_subscription(selected_plan, user_id, user_email)
        
        if subscription_id:
            # Preguntar si quiere testear el webhook
            test_webhook = input("\n¿Quieres testear el webhook ahora? (y/n): ").strip().lower()
            if test_webhook == 'y':
                test_webhook_with_real_subscription(subscription_id)
    else:
        print("❌ Selección inválida") 