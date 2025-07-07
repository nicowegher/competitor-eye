#!/usr/bin/env python3
"""
Script para probar las métricas localmente
"""

import pandas as pd
from datetime import datetime

def calcular_metricas(datos_prueba):
    """Calcula las métricas usando la misma lógica del backend"""
    
    # Extraer nombres de hoteles
    hotelNames = [hotel["Hotel Name"] for hotel in datos_prueba]
    hotel_principal = hotelNames[0]
    competidores = hotelNames[1:]
    
    print(f"🏨 Hotel principal: {hotel_principal}")
    print(f"🏨 Competidores: {competidores}")
    
    # Extraer fechas únicas
    all_dates = set()
    for hotel in datos_prueba:
        for k in hotel.keys():
            if k not in ("Hotel Name", "URL"):
                all_dates.add(k)
    all_dates = sorted(all_dates)
    
    print(f"📅 Fechas encontradas: {all_dates}")
    
    # Calcular métricas
    metricas_resultado = []
    chartData = []
    
    for date in all_dates:
        print(f"\n📊 Procesando fecha: {date}")
        
        # Obtener precios válidos para esta fecha
        precios_validos = {}
        for hotel in datos_prueba:
            name = hotel["Hotel Name"]
            price = hotel.get(date, None)
            if price and price != "N/A":
                try:
                    precios_validos[name] = float(price)
                except:
                    continue
        
        print(f"  💰 Precios válidos: {precios_validos}")
        
        # 1. Calcular tarifa promedio de competidores
        precios_competidores = []
        for name in competidores:
            precio = precios_validos.get(name)
            if precio is not None and isinstance(precio, (int, float)):
                precios_competidores.append(precio)
        
        promedio_competidores = None
        if precios_competidores:
            promedio_competidores = sum(precios_competidores) / len(precios_competidores)
        
        print(f"  📊 Promedio competidores: {promedio_competidores}")
        
        # 2. Calcular disponibilidad de la oferta (%)
        total_hoteles = len(hotelNames)
        hoteles_con_precio = len([name for name in hotelNames if precios_validos.get(name) is not None])
        disponibilidad_porcentaje = round((hoteles_con_precio / total_hoteles) * 100) if total_hoteles > 0 else 0
        disponibilidad = f"{disponibilidad_porcentaje}%"
        
        print(f"  📈 Disponibilidad: {disponibilidad} ({hoteles_con_precio}/{total_hoteles} hoteles)")
        
        # 3. Calcular diferencia porcentual del hotel principal vs promedio de competidores
        diferencia_porcentual = None
        precio_principal = precios_validos.get(hotel_principal)
        if precio_principal is not None and promedio_competidores is not None and promedio_competidores > 0:
            diferencia = ((precio_principal - promedio_competidores) / promedio_competidores) * 100
            diferencia_porcentual = f"{diferencia:+.1f}%" if diferencia != 0 else "0.0%"
        
        print(f"  💹 Diferencia %: {diferencia_porcentual}")
        
        # Agregar métricas al resultado
        metricas_resultado.append({
            "fecha": date,
            "tarifa_promedio_competidores": promedio_competidores,
            "disponibilidad_oferta": disponibilidad,
            "diferencia_porcentual": diferencia_porcentual,
            "precios_competidores": precios_competidores,
            "precio_principal": precio_principal
        })
        
        # Agregar al chartData
        chartData.append({
            "date": date,
            "Tarifa promedio de competidores": promedio_competidores,
            "Disponibilidad de la oferta (%)": disponibilidad,
            "Diferencia % vs. competidores": diferencia_porcentual
        })
    
    return metricas_resultado, chartData

def crear_dataframe_con_metricas(datos_prueba, metricas_resultado):
    """Crea un DataFrame con las métricas incluidas"""
    
    # Extraer fechas únicas
    all_dates = set()
    for hotel in datos_prueba:
        for k in hotel.keys():
            if k not in ("Hotel Name", "URL"):
                all_dates.add(k)
    all_dates = sorted(all_dates)
    
    # Crear DataFrame con métricas para Excel
    datos_con_metricas = datos_prueba.copy()
    for date in all_dates:
        metricas_fecha = next(m for m in metricas_resultado if m["fecha"] == date)
        
        datos_con_metricas.append({
            "Hotel Name": "Tarifa promedio de competidores",
            "URL": "",
            date: metricas_fecha["tarifa_promedio_competidores"]
        })
        datos_con_metricas.append({
            "Hotel Name": "Disponibilidad de la oferta (%)",
            "URL": "",
            date: metricas_fecha["disponibilidad_oferta"]
        })
        datos_con_metricas.append({
            "Hotel Name": "Diferencia % vs. competidores",
            "URL": "",
            date: metricas_fecha["diferencia_porcentual"]
        })
    
    return datos_con_metricas

def test_metricas():
    """Prueba las métricas con datos simulados"""
    
    print("🧪 PRUEBA LOCAL DE MÉTRICAS")
    print("=" * 50)
    
    # Datos de prueba simulados
    datos_prueba = [
        {
            "Hotel Name": "Hotel Principal",
            "URL": "https://example.com/hotel1",
            "2024-01-15": 150.0,
            "2024-01-16": 160.0,
            "2024-01-17": 155.0
        },
        {
            "Hotel Name": "Competidor 1",
            "URL": "https://example.com/hotel2",
            "2024-01-15": 140.0,
            "2024-01-16": 150.0,
            "2024-01-17": "N/A"
        },
        {
            "Hotel Name": "Competidor 2",
            "URL": "https://example.com/hotel3",
            "2024-01-15": 145.0,
            "2024-01-16": "N/A",
            "2024-01-17": 150.0
        }
    ]
    
    print("📊 DATOS DE PRUEBA:")
    for hotel in datos_prueba:
        print(f"  - {hotel['Hotel Name']}: {hotel}")
    
    # Calcular métricas
    print("\n🔢 CALCULANDO MÉTRICAS...")
    metricas_resultado, chartData = calcular_metricas(datos_prueba)
    
    # Mostrar resultados
    print("\n📈 RESULTADOS DE MÉTRICAS:")
    for metrica in metricas_resultado:
        print(f"  📅 {metrica['fecha']}:")
        print(f"    - Tarifa promedio competidores: {metrica['tarifa_promedio_competidores']}")
        print(f"    - Disponibilidad oferta: {metrica['disponibilidad_oferta']}")
        print(f"    - Diferencia %: {metrica['diferencia_porcentual']}")
    
    # Crear DataFrame con métricas
    print("\n📋 CREANDO DATAFRAME CON MÉTRICAS...")
    datos_con_metricas = crear_dataframe_con_metricas(datos_prueba, metricas_resultado)
    
    # Crear DataFrame de pandas
    df = pd.DataFrame(datos_con_metricas)
    
    print(f"\n📊 DATAFRAME FINAL ({len(df)} filas):")
    print(df)
    
    # Verificar que las métricas están en el DataFrame
    metricas_en_df = df[df['Hotel Name'].str.contains('Tarifa promedio|Disponibilidad|Diferencia', na=False)]
    print(f"\n✅ MÉTRICAS EN DATAFRAME ({len(metricas_en_df)} filas):")
    print(metricas_en_df)
    
    # Mostrar chartData
    print("\n📊 CHART DATA:")
    for chart_item in chartData:
        print(f"  📅 {chart_item['date']}:")
        for key, value in chart_item.items():
            if key != 'date':
                print(f"    - {key}: {value}")
    
    # Guardar como Excel para verificar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"test_metricas_{timestamp}.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"\n💾 Excel guardado como: {excel_filename}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_metricas()
        if success:
            print("\n✅ PRUEBA EXITOSA: Las métricas se calculan correctamente")
        else:
            print("\n❌ PRUEBA FALLIDA")
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBA: {e}")
        import traceback
        traceback.print_exc() 