import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.environ["MERCADOPAGO_ACCESS_TOKEN"]

PLANES = [
    ("Plan Esencial", 7200),
    ("Plan Pro", 21600),
    ("Plan Market Leader", 30000)
]

BACK_URL = "https://TU-DOMINIO.com"  # Cambia esto por tu dashboard real

for nombre, precio in PLANES:
    url = "https://api.mercadopago.com/preapproval_plan"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "reason": nombre,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": precio,
            "currency_id": "ARS"
        },
        "back_url": BACK_URL
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"{nombre}: {response.status_code} {response.json()}\n") 