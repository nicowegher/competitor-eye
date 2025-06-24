#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del scraper mejorado
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "https://tu-app-en-render.onrender.com"  # Cambiar por tu URL de Render
TEST_DATA = {
    "ownHotelUrl": "https://www.booking.com/hotel/ar/el-pueblito-iguazu.es.html?selected_currency=USD",
    "competitorHotelUrls": [
        "https://www.booking.com/hotel/ar/guamini-mision-puerto-iguazu6.es.html?selected_currency=USD"
    ],
    "daysToScrape": 1
}

def test_health_check():
    """Prueba el endpoint de health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_scraper_start():
    """Prueba iniciar el scraper"""
    print("\n🚀 Probando inicio del scraper...")
    try:
        response = requests.post(
            f"{BASE_URL}/run-scraper",
            json=TEST_DATA,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Respuesta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Scraper iniciado correctamente")
            return True
        else:
            print("❌ Error al iniciar scraper")
            return False
            
    except Exception as e:
        print(f"❌ Error al iniciar scraper: {e}")
        return False

def test_scraper_status():
    """Prueba el endpoint de status del scraper"""
    print("\n📊 Probando status del scraper...")
    try:
        response = requests.get(f"{BASE_URL}/scraper-status")
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Status obtenido correctamente")
            print(f"   Estado: {status}")
            return status
        else:
            print(f"❌ Error al obtener status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error al obtener status: {e}")
        return None

def monitor_scraper_progress(max_wait_time=300):
    """Monitorea el progreso del scraper"""
    print(f"\n⏱️  Monitoreando progreso (máximo {max_wait_time}s)...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait_time:
        status = test_scraper_status()
        
        if status:
            # Verificar si el estado cambió
            if status != last_status:
                print(f"\n📈 Estado actualizado:")
                print(f"   Ejecutándose: {status.get('is_running', 'N/A')}")
                print(f"   Progreso: {status.get('progress', 'N/A')}%")
                print(f"   Error: {status.get('error', 'Ninguno')}")
                
                if status.get('result'):
                    print(f"   ✅ Scraper completado!")
                    print(f"   CSV URL: {status['result'].get('csvFileUrl', 'N/A')}")
                    print(f"   XLSX URL: {status['result'].get('xlsxFileUrl', 'N/A')}")
                    return True
                
                if status.get('error'):
                    print(f"   ❌ Scraper falló: {status['error']}")
                    return False
                
                last_status = status
        
        # Esperar 10 segundos antes de la siguiente verificación
        time.sleep(10)
    
    print("⏰ Tiempo de espera agotado")
    return False

def test_download_endpoints():
    """Prueba los endpoints de descarga"""
    print("\n📥 Probando endpoints de descarga...")
    
    endpoints = [
        ("/datos", "GET"),
        ("/descargar-csv", "GET"),
        ("/descargar-excel", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            print(f"   {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint} funciona correctamente")
            else:
                print(f"   ⚠️  {endpoint} retornó {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error en {endpoint}: {e}")

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SCRAPER MEJORADO")
    print("=" * 50)
    print(f"URL Base: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Prueba 1: Health Check
    if not test_health_check():
        print("\n❌ Health check falló. Verificar que la aplicación esté corriendo.")
        return
    
    # Prueba 2: Endpoints de descarga
    test_download_endpoints()
    
    # Prueba 3: Iniciar scraper
    if not test_scraper_start():
        print("\n❌ No se pudo iniciar el scraper.")
        return
    
    # Prueba 4: Monitorear progreso
    success = monitor_scraper_progress(max_wait_time=300)  # 5 minutos máximo
    
    if success:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("El scraper mejorado está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron o el scraper no completó en tiempo.")
    
    print("\n" + "=" * 50)
    print("FIN DE PRUEBAS")

if __name__ == "__main__":
    main() 