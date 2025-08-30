#!/usr/bin/env python3
"""
Script para probar el endpoint de tareas programadas.
"""

import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_scheduler_endpoint():
    """Prueba el endpoint de tareas programadas."""
    
    # URL del endpoint
    base_url = "https://competitor-eye.onrender.com"
    endpoint = "/execute-scheduled-tasks"
    
    # Token de prueba (debe coincidir con SCHEDULER_TOKEN en Render)
    test_token = "t0sUS4i6o5f3vt9rBu2o7WTMf7GkSCoT"
    
    # URL completa con token
    url = f"{base_url}{endpoint}?token={test_token}"
    
    print("=" * 50)
    print("🧪 PRUEBA DEL ENDPOINT DE SCHEDULER")
    print("=" * 50)
    print(f"URL: {url}")
    print()
    
    try:
        # Hacer la petición POST
        response = requests.post(url, timeout=30)
        
        print(f"📊 RESULTADO:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ ÉXITO: El endpoint funciona correctamente")
        elif response.status_code == 401:
            print("❌ ERROR: Token inválido - Verifica SCHEDULER_TOKEN en Render")
        else:
            print(f"⚠️  ADVERTENCIA: Status code inesperado: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    test_scheduler_endpoint() 