#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint de métricas
"""

import requests
import json
import pandas as pd
from datetime import datetime

def test_metricas_endpoint():
    """Prueba el endpoint de métricas"""
    
    # URL del backend (ajusta según tu configuración)
    base_url = "https://tu-backend.onrender.com"  # Cambia por tu URL real
    
    print("🔍 Probando endpoint de métricas...")
    print(f"URL: {base_url}/test-metricas")
    
    try:
        # Hacer la petición GET al endpoint
        response = requests.get(f"{base_url}/test-metricas")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint respondió correctamente")
            
            # Mostrar datos originales
            print("\n📊 DATOS ORIGINALES:")
            for hotel in data["datos_originales"]:
                print(f"  - {hotel['Hotel Name']}: {hotel}")
            
            # Mostrar métricas calculadas
            print("\n📈 MÉTRICAS CALCULADAS:")
            for metrica in data["metricas_calculadas"]:
                print(f"  📅 {metrica['fecha']}:")
                print(f"    - Tarifa promedio competidores: {metrica['tarifa_promedio_competidores']}")
                print(f"    - Disponibilidad oferta: {metrica['disponibilidad_oferta']}")
                print(f"    - Diferencia %: {metrica['diferencia_porcentual']}")
                print(f"    - Precios competidores: {metrica['precios_competidores']}")
                print(f"    - Precio principal: {metrica['precio_principal']}")
            
            # Mostrar chartData
            print("\n📊 CHART DATA:")
            for chart_item in data["chartData"]:
                print(f"  📅 {chart_item['date']}:")
                for key, value in chart_item.items():
                    if key != 'date':
                        print(f"    - {key}: {value}")
            
            # Mostrar datos con métricas (como aparecerían en Excel)
            print("\n📋 DATOS CON MÉTRICAS (Excel):")
            for item in data["datos_con_metricas"]:
                print(f"  - {item['Hotel Name']}: {item}")
            
            # Crear un DataFrame de prueba para verificar formato
            df = pd.DataFrame(data["datos_con_metricas"])
            print(f"\n📊 DataFrame generado ({len(df)} filas):")
            print(df.head())
            
            # Verificar que las métricas están en el DataFrame
            metricas_en_df = df[df['Hotel Name'].str.contains('Tarifa promedio|Disponibilidad|Diferencia', na=False)]
            print(f"\n✅ Métricas encontradas en DataFrame ({len(metricas_en_df)} filas):")
            print(metricas_en_df[['Hotel Name'] + [col for col in df.columns if col not in ['Hotel Name', 'URL']]])
            
            return True
            
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_scraper_real():
    """Prueba el scraper real con datos de prueba"""
    
    base_url = "https://tu-backend.onrender.com"  # Cambia por tu URL real
    
    print("\n🔍 Probando scraper real...")
    
    # Datos de prueba para el scraper
    test_data = {
        "hotel_base_urls": [
            "https://www.booking.com/hotel/ar/hotel-principal.html",
            "https://www.booking.com/hotel/ar/competidor-1.html",
            "https://www.booking.com/hotel/ar/competidor-2.html"
        ],
        "days": 3,
        "userEmail": "test@example.com",
        "setName": "Test Group"
    }
    
    try:
        # Crear un taskId único
        task_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Hacer la petición POST al scraper
        response = requests.post(
            f"{base_url}/run-scraper",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scraper iniciado correctamente")
            print(f"Task ID: {data.get('taskId', 'N/A')}")
            print(f"Respuesta: {data}")
            
            # Verificar estado del scraper
            print("\n⏳ Verificando estado del scraper...")
            status_response = requests.get(f"{base_url}/scraper-status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Estado: {status_data}")
            else:
                print(f"❌ Error obteniendo estado: {status_response.status_code}")
                
        else:
            print(f"❌ Error iniciando scraper: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba de scraper: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE MÉTRICAS")
    print("=" * 50)
    
    # Prueba 1: Endpoint de métricas
    success1 = test_metricas_endpoint()
    
    if success1:
        print("\n✅ PRUEBA 1 EXITOSA: Endpoint de métricas funciona correctamente")
    else:
        print("\n❌ PRUEBA 1 FALLIDA: Endpoint de métricas no funciona")
    
    # Prueba 2: Scraper real (opcional)
    print("\n" + "=" * 50)
    print("¿Quieres probar el scraper real? (s/n): ", end="")
    try:
        user_input = input().lower()
        if user_input in ['s', 'si', 'sí', 'y', 'yes']:
            test_scraper_real()
    except KeyboardInterrupt:
        print("\nPrueba cancelada por el usuario")
    
    print("\n🏁 PRUEBAS COMPLETADAS") 