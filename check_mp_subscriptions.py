#!/usr/bin/env python3
"""
Script para verificar planes y suscripciones de Mercado Pago y simular el webhook
"""

import os
import mercadopago
from dotenv import load_dotenv
import json
from datetime import datetime
import requests

# Cargar variables de entorno
load_dotenv()

# Configurar SDK de Mercado Pago
sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])
MP_ACCESS_TOKEN = os.environ['MERCADOPAGO_ACCESS_TOKEN']

# IDs de planes
MP_PLAN_IDS = {
    "esencial": "2c93808497c462520197d744586508be",
    "pro": "2c93808497c19ac40197d7445b440a20",
    "market_leader": "2c93808497d635430197d7445e1c00bc"
}

WEBHOOK_URL = "https://competitor-eye.onrender.com/mercado-pago-webhook"

# Usar requests para obtener el plan

def check_plan_status(plan_name):
    """Verifica el estado de un plan específico"""
    plan_id = MP_PLAN_IDS[plan_name]
    print(f"\n=== VERIFICANDO PLAN: {plan_name.upper()} ===")
    print(f"Plan ID: {plan_id}")
    try:
        url = f"https://api.mercadopago.com/preapproval_plan/{plan_id}"
        headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            plan_data = resp.json()
            print(f"Estado: {plan_data.get('status')}")
            print(f"Razón: {plan_data.get('reason')}")
            print(f"Precio: {plan_data.get('auto_recurring', {}).get('transaction_amount')} {plan_data.get('auto_recurring', {}).get('currency_id')}")
            print(f"Frecuencia: {plan_data.get('auto_recurring', {}).get('frequency')} {plan_data.get('auto_recurring', {}).get('frequency_type')}")
            print(f"Init Point: {plan_data.get('init_point')}")
        else:
            print(f"❌ No se pudo obtener información del plan. Status: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ Error al verificar plan: {e}")

def get_subscription_by_id(preapproval_id):
    """Obtiene información de una suscripción por ID"""
    print(f"\n=== CONSULTANDO SUSCRIPCIÓN: {preapproval_id} ===")
    try:
        sub = sdk.preapproval().get(preapproval_id)
        if sub['status'] == 200 and sub['response']:
            sub_data = sub['response']
            print(json.dumps(sub_data, indent=2, ensure_ascii=False))
            return sub_data
        else:
            print("❌ No se encontró la suscripción")
    except Exception as e:
        print(f"❌ Error al consultar suscripción: {e}")
    return None

def test_webhook_simulation(preapproval_id, secret=None):
    """Simula el envío de una notificación de webhook"""
    print("\n=== SIMULACIÓN DE WEBHOOK ===")
    webhook_data = {
        "type": "preapproval",
        "data": {
            "id": preapproval_id
        }
    }
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["x-signature"] = secret
    print(f"Enviando POST a {WEBHOOK_URL} con body:")
    print(json.dumps(webhook_data, indent=2))
    response = requests.post(WEBHOOK_URL, json=webhook_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def instrucciones_postman(preapproval_id, secret=None):
    print("\n=== INSTRUCCIONES PARA POSTMAN ===")
    print(f"1. Método: POST")
    print(f"2. URL: {WEBHOOK_URL}")
    print(f"3. Headers:")
    print(f"   Content-Type: application/json")
    if secret:
        print(f"   x-signature: {secret}")
    print(f"4. Body (raw, JSON):")
    print(json.dumps({
        "type": "preapproval",
        "data": {"id": preapproval_id}
    }, indent=2))
    print(f"5. Envía la petición y revisa que la respuesta sea OK.")
    print(f"6. Verifica en Firestore que el usuario tenga el plan actualizado.")

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE PLANES Y SUSCRIPCIONES MERCADO PAGO")
    print("=" * 60)
    # 1. Verificar estado de cada plan
    for plan in MP_PLAN_IDS.keys():
        check_plan_status(plan)
    print("\nPuedes consultar una suscripción específica para simular el webhook.")
    preapproval_id = input("Ingresa el ID de una suscripción real de Mercado Pago: ").strip()
    if preapproval_id:
        get_subscription_by_id(preapproval_id)
        usar_secret = input("¿Quieres usar la clave secreta del webhook? (y/n): ").strip().lower() == 'y'
        secret = None
        if usar_secret:
            secret = input("Pega aquí la clave secreta: ").strip()
        test_webhook_simulation(preapproval_id, secret)
        instrucciones_postman(preapproval_id, secret)
    print("\n🏁 VERIFICACIÓN COMPLETADA") 