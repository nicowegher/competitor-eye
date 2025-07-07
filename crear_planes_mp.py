import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.environ["MERCADOPAGO_ACCESS_TOKEN"]

# Precios mensuales
PRECIO_ESENCIAL = 7200
PRECIO_PRO = 21600
PRECIO_MARKET = 30000

# Planes mensuales
PLANES_MENSUALES = [
    ("Plan Esencial Mensual", PRECIO_ESENCIAL, 1, "months"),
    ("Plan Pro Mensual", PRECIO_PRO, 1, "months"),
    ("Plan Market Leader Mensual", PRECIO_MARKET, 1, "months")
]

# Plan anual esencial: 1 mes de descuento (11 meses)
PRECIO_ESENCIAL_ANUAL = PRECIO_ESENCIAL * 11
# Plan anual pro: 22% de descuento respecto a 12 meses
PRECIO_PRO_ANUAL = int(PRECIO_PRO * 12 * 0.78)
# Plan anual market leader: 31% de descuento respecto a 12 meses
PRECIO_MARKET_ANUAL = int(PRECIO_MARKET * 12 * 0.69)

PLANES_ANUALES = [
    ("Plan Esencial Anual", PRECIO_ESENCIAL_ANUAL, 12, "months"),
    ("Plan Pro Anual", PRECIO_PRO_ANUAL, 12, "months"),
    ("Plan Market Leader Anual", PRECIO_MARKET_ANUAL, 12, "months")
]

BACK_URL = "https://competitor-eye.onrender.com/dashboard"

# --- BORRAR PLANES EXISTENTES (solo los de test) ---
def borrar_planes_existentes():
    url = "https://api.mercadopago.com/preapproval_plan/search"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for plan in data.get('results', []):
            plan_id = plan['id']
            print(f"Eliminando plan: {plan['reason']} ({plan_id})")
            del_url = f"https://api.mercadopago.com/preapproval_plan/{plan_id}"
            del_resp = requests.delete(del_url, headers=headers)
            print(f"  Status: {del_resp.status_code} - {del_resp.text}")
    else:
        print(f"No se pudieron listar los planes. Status: {response.status_code}")
        print(response.text)

# --- CREAR PLANES NUEVOS ---
def crear_planes(planes):
    ids = {}
    for nombre, precio, frecuencia, frecuencia_tipo in planes:
        url = "https://api.mercadopago.com/preapproval_plan"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "reason": nombre,
            "auto_recurring": {
                "frequency": frecuencia,
                "frequency_type": frecuencia_tipo,
                "transaction_amount": precio,
                "currency_id": "ARS"
            },
            "back_url": BACK_URL
        }
        response = requests.post(url, headers=headers, json=data)
        resp_json = response.json()
        print(f"{nombre}: {response.status_code} {resp_json}\n")
        if response.status_code == 201 and 'id' in resp_json:
            ids[nombre] = resp_json['id']
    return ids

if __name__ == "__main__":
    print("Borrando planes existentes...")
    borrar_planes_existentes()
    print("\nCreando planes mensuales...")
    ids_mensuales = crear_planes(PLANES_MENSUALES)
    print("\nCreando planes anuales...")
    ids_anuales = crear_planes(PLANES_ANUALES)
    print("\n=== IDs DE PLANES CREADOS ===")
    print("--- Mensuales ---")
    for nombre, _precio, _f, _t in PLANES_MENSUALES:
        print(f"{nombre}: {ids_mensuales.get(nombre, 'ERROR')}")
    print("--- Anuales ---")
    for nombre, _precio, _f, _t in PLANES_ANUALES:
        print(f"{nombre}: {ids_anuales.get(nombre, 'ERROR')}")
    print("\nListo!") 