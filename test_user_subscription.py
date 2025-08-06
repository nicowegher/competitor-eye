#!/usr/bin/env python3
"""
Script para probar la suscripción específica del usuario que tuvo problemas
"""

import os
import mercadopago
from dotenv import load_dotenv
import json
import requests
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configurar SDK de Mercado Pago
sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])
MP_ACCESS_TOKEN = os.environ['MERCADOPAGO_ACCESS_TOKEN']

# ID de la suscripción del usuario (del preapproval_id en la URL)
SUBSCRIPTION_ID = "097b9e32925c4633a8d9a6a895e58210"
USER_EMAIL = "m.miquela@gmail.com"

def check_user_subscription():
    """Verifica el estado de la suscripción específica del usuario"""
    print(f"\n=== VERIFICANDO SUSCRIPCIÓN DEL USUARIO ===")
    print(f"Subscription ID: {SUBSCRIPTION_ID}")
    print(f"User Email: {USER_EMAIL}")
    
    try:
        # Obtener información de la suscripción
        sub = sdk.preapproval().get(SUBSCRIPTION_ID)
        
        if sub["status"] == 200:
            subscription_data = sub["response"]
            print("✅ Información de la suscripción:")
            print(f"   Status: {subscription_data.get('status')}")
            print(f"   Plan ID: {subscription_data.get('preapproval_plan_id')}")
            print(f"   Email: {subscription_data.get('payer_email')}")
            print(f"   External Reference: {subscription_data.get('external_reference')}")
            print(f"   Reason: {subscription_data.get('reason')}")
            print(f"   Created: {subscription_data.get('date_created')}")
            print(f"   Last Modified: {subscription_data.get('last_modified')}")
            
            # Determinar el plan
            plan_id = subscription_data.get('preapproval_plan_id', '')
            plan_mapping = {
                "2c93808497c462520197d744586508be": "esencial",
                "2c93808497c19ac40197d7445b440a20": "pro", 
                "2c93808497d635430197d7445e1c00bc": "market_leader"
            }
            plan = plan_mapping.get(plan_id, "desconocido")
            print(f"   Plan: {plan}")
            
            return subscription_data
        else:
            print(f"❌ Error al obtener suscripción: {sub}")
            return None
            
    except Exception as e:
        print(f"❌ Error al verificar suscripción: {e}")
        return None

def test_webhook_manually():
    """Prueba el webhook manualmente con la suscripción del usuario"""
    print(f"\n=== PROBANDO WEBHOOK MANUALMENTE ===")
    
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": SUBSCRIPTION_ID
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

def check_firestore_user():
    """Verifica si el usuario existe en Firestore y su plan actual"""
    print(f"\n=== VERIFICANDO USUARIO EN FIRESTORE ===")
    
    try:
        import firebase_admin
        from firebase_admin import firestore
        
        # Inicializar Firebase si no está inicializado
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        
        db = firestore.client()
        
        # Buscar usuario por email
        users_ref = db.collection('users')
        users = users_ref.where('email', '==', USER_EMAIL).stream()
        
        user_found = False
        for user in users:
            user_data = user.to_dict()
            print(f"✅ Usuario encontrado:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Plan actual: {user_data.get('plan', 'No definido')}")
            print(f"   Plan actualizado: {user_data.get('plan_updated_at', 'No definido')}")
            print(f"   Subscription ID: {user_data.get('subscription_id', 'No definido')}")
            print(f"   Subscription Status: {user_data.get('subscription_status', 'No definido')}")
            user_found = True
            break
        
        if not user_found:
            print(f"❌ Usuario no encontrado para email: {USER_EMAIL}")
            
    except Exception as e:
        print(f"❌ Error al verificar usuario en Firestore: {e}")

def simulate_webhook_for_user():
    """Simula el webhook para actualizar el plan del usuario"""
    print(f"\n=== SIMULANDO WEBHOOK PARA ACTUALIZAR PLAN ===")
    
    # Primero verificar la suscripción
    subscription_data = check_user_subscription()
    if not subscription_data:
        print("❌ No se pudo obtener información de la suscripción")
        return
    
    # Verificar si el usuario existe
    check_firestore_user()
    
    # Preguntar si quiere simular el webhook
    simulate = input("\n¿Quieres simular el webhook para actualizar el plan? (y/n): ").strip().lower()
    if simulate == 'y':
        test_webhook_manually()
        
        # Verificar nuevamente el usuario después del webhook
        print("\n--- Verificando usuario después del webhook ---")
        check_firestore_user()

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE SUSCRIPCIÓN DEL USUARIO")
    print("=" * 60)
    
    # 1. Verificar suscripción en Mercado Pago
    subscription_data = check_user_subscription()
    
    # 2. Verificar usuario en Firestore
    check_firestore_user()
    
    # 3. Simular webhook si es necesario
    simulate_webhook_for_user()
    
    print("\n🏁 VERIFICACIÓN COMPLETADA") 