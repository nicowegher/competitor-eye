#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de tareas programadas
"""

import requests
import json
import os
from datetime import datetime

# Configuración
BASE_URL = "https://tu-app.onrender.com"  # Cambiar por tu URL real
SCHEDULER_TOKEN = "XbV970HTpIQKtsMux6kYfe3uS"  # Token que aparece en los logs

def test_health_check():
    """Prueba el endpoint de health check"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_scheduled_tasks_status():
    """Prueba el endpoint de estado de tareas programadas"""
    try:
        response = requests.get(f"{BASE_URL}/test-scheduled-tasks")
        print(f"✅ Test scheduled tasks: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Test scheduled tasks failed: {e}")
        return False

def test_execute_scheduled_tasks():
    """Prueba el endpoint de ejecución de tareas programadas"""
    try:
        url = f"{BASE_URL}/execute-scheduled-tasks?token={SCHEDULER_TOKEN}"
        response = requests.post(url)
        print(f"✅ Execute scheduled tasks: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Execute scheduled tasks failed: {e}")
        return False

def test_scraper_status():
    """Prueba el endpoint de estado del scraper"""
    try:
        response = requests.get(f"{BASE_URL}/scraper-status")
        print(f"✅ Scraper status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Scraper status failed: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🧪 Iniciando pruebas del sistema de tareas programadas")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Scheduled Tasks Status", test_scheduled_tasks_status),
        ("Scraper Status", test_scraper_status),
        ("Execute Scheduled Tasks", test_execute_scheduled_tasks),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Probando: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LAS PRUEBAS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resumen: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs para más detalles.")

if __name__ == "__main__":
    main() 