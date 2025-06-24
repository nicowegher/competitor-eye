import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from apify_client import ApifyClient
import pandas as pd
from urllib.parse import urlparse, parse_qs
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your Apify API token
APIFY_API_TOKEN = "apify_api_RTGzqkBR6KvQMttGgZsAxIhp6xBBYc0mueZW"

# Función para lanzar una ejecución individual del actor y devolver el precio
def fetch_price_for_night(client, base_url, hotel_name, checkin, checkout):
    # Los parámetros de fecha se pasan directamente al input del actor
    run_input = {
        "startUrls": [{"url": base_url}],
        "checkIn": checkin,
        "checkOut": checkout,
        "maxRequestsPerCrawl": 1,
        "maxConcurrency": 1,
        "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": ["US"]},
        "currency": "USD",
        "language": "es",
        "maxPagesPerCrawl": 1,
        "maxItems": 1,
        "timeoutSecs": 60,  # Timeout más corto para evitar bloqueos
    }
    
    try:
        logger.info(f"Iniciando scraper para {hotel_name} - {checkin}")
        run = client.actor("voyager/booking-scraper").call(run_input=run_input)
        
        if run is None or "defaultDatasetId" not in run:
            logger.warning(f"No se pudo obtener dataset para {hotel_name} - {checkin}")
            return (hotel_name, base_url, checkin, "N/A")
        
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        
        if not items:
            logger.warning(f"No se encontraron items para {hotel_name} - {checkin}")
            return (hotel_name, base_url, checkin, "N/A")
        
        price = "N/A"
        for item in items:
            if "rooms" in item and item["rooms"]:
                for room in item["rooms"]:
                    if "options" in room and room["options"]:
                        for option in room["options"]:
                            try:
                                price = str(float(option["displayedPrice"]))
                                logger.info(f"Precio encontrado para {hotel_name} - {checkin}: {price}")
                                return (hotel_name, base_url, checkin, price)
                            except (ValueError, TypeError, KeyError):
                                continue
        
        logger.warning(f"No se encontró precio válido para {hotel_name} - {checkin}")
        return (hotel_name, base_url, checkin, price)
        
    except Exception as e:
        logger.error(f"Error para {hotel_name} {checkin}: {e}")
        return (hotel_name, base_url, checkin, "N/A")

def scrape_booking_data(hotel_base_urls, days=2):
    """
    Función principal para hacer scraping de datos de Booking.com
    """
    logger.info(f"Iniciando scraping para {len(hotel_base_urls)} hoteles por {days} días")
    
    client = ApifyClient(APIFY_API_TOKEN)
    today = datetime.now()
    
    # Generar rangos de fechas
    date_ranges = [
        ((today + timedelta(days=i)).strftime("%Y-%m-%d"), (today + timedelta(days=i+1)).strftime("%Y-%m-%d"))
        for i in range(1, days+1)
    ]
    
    # Obtener nombres de hoteles
    url_to_name = {}
    for url in hotel_base_urls:
        try:
            # Extraer nombre del hotel de la URL
            hotel_id = url.split("/hotel/")[-1].split(".")[0]
            hotel_name = hotel_id.replace("-", " ").title()
            url_to_name[url] = hotel_name
        except:
            url_to_name[url] = f"Hotel_{len(url_to_name) + 1}"
    
    # Crear lista de tareas
    tasks = []
    for base_url in hotel_base_urls:
        hotel_name = url_to_name[base_url]
        for checkin, checkout in date_ranges:
            tasks.append((base_url, hotel_name, checkin, checkout))
    
    logger.info(f"Total de tareas a ejecutar: {len(tasks)}")
    
    # Ejecutar tareas con ThreadPoolExecutor
    results = []
    completed = 0
    
    # Usar menos workers para evitar sobrecarga
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_task = {
            executor.submit(fetch_price_for_night, client, base_url, hotel_name, checkin, checkout): (base_url, hotel_name, checkin, checkout)
            for (base_url, hotel_name, checkin, checkout) in tasks
        }
        
        for future in as_completed(future_to_task):
            base_url, hotel_name, checkin, checkout = future_to_task[future]
            completed += 1
            
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Progreso: {completed}/{len(tasks)} - {hotel_name} - {checkin}")
            except Exception as exc:
                logger.error(f"Error en {hotel_name} {checkin}: {exc}")
                results.append((hotel_name, base_url, checkin, "N/A"))
            
            # Pausa entre requests para evitar rate limiting
            time.sleep(1)
    
    # Construir DataFrame
    df_dict = {}
    for hotel_name, base_url, checkin, price in results:
        if base_url not in df_dict:
            df_dict[base_url] = {"Hotel Name": hotel_name, "URL": base_url}
        df_dict[base_url][checkin] = price
    
    final_results = list(df_dict.values())
    logger.info(f"Scraping completado. Total de hoteles procesados: {len(final_results)}")
    
    return final_results

def main():
    """
    Función principal para ejecutar el scraper desde línea de comandos
    """
    # URLs base de los hoteles (sin parámetros de fecha)
    hotel_base_urls = [
        "https://www.booking.com/hotel/ar/el-pueblito-iguazu.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/guamini-mision-puerto-iguazu6.es.html?selected_currency=USD",
        # Agrega más URLs aquí si lo deseas
    ]
    days = 1  # Cambia este valor para probar con más días
    
    if APIFY_API_TOKEN == "YOUR_APIFY_API_TOKEN":
        logger.error("ERROR: Por favor, reemplaza 'YOUR_APIFY_API_TOKEN' con tu token real de Apify en el archivo apify_scraper.py.")
        return

    try:
        scraped_data = scrape_booking_data(hotel_base_urls, days=days)

        if scraped_data:
            df = pd.DataFrame(scraped_data)
            
            # Guardar en Excel
            excel_filename = f"tarifas_hoteles_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(excel_filename, index=False)
            logger.info(f"Datos guardados en {excel_filename}")
            
            # Guardar en CSV
            csv_filename = f"tarifas_hoteles_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(csv_filename, index=False)
            logger.info(f"Datos guardados en {csv_filename}")
        else:
            logger.warning("No se obtuvieron datos de scraping.")
            
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")

if __name__ == '__main__':
    main()


