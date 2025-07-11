import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from apify_client import ApifyClient
import pandas as pd
from urllib.parse import urlparse, parse_qs
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar el token desde variable de entorno
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN no está definido en las variables de entorno. Por favor, configúralo antes de ejecutar el scraper.")

# Función para lanzar una ejecución individual del actor y devolver el precio
def fetch_price_for_night(client, base_url, hotel_name, checkin, checkout, currency="USD"):
    run_input = {
        "startUrls": [{"url": base_url}],
        "checkIn": checkin,
        "checkOut": checkout,
        "maxRequestsPerCrawl": 1,
        "maxConcurrency": 1,
        "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": ["US"]},
        "currency": currency,
        "language": "es",
        "maxPagesPerCrawl": 1,
        "maxItems": 1,
        "timeoutSecs": 60,
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

def scrape_booking_data(hotel_base_urls, days=2, nights=1, currency="USD"):
    """
    Scraping de Booking.com para múltiples hoteles, días, noches y moneda.
    """
    logger.info(f"Iniciando scraping para {len(hotel_base_urls)} hoteles por {days} días, {nights} noches, moneda {currency}")
    client = ApifyClient(APIFY_API_TOKEN)
    today = datetime.now()
    # Generar rangos de fechas con la cantidad de noches deseada
    date_ranges = [
        (
            (today + timedelta(days=i)).strftime("%Y-%m-%d"),
            (today + timedelta(days=i+nights)).strftime("%Y-%m-%d")
        )
        for i in range(1, days+1)
    ]
    # Obtener nombres de hoteles
    url_to_name = {}
    for url in hotel_base_urls:
        try:
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
    results = []
    completed = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_task = {
            executor.submit(fetch_price_for_night, client, base_url, hotel_name, checkin, checkout, currency): (base_url, hotel_name, checkin, checkout)
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
            time.sleep(0.5)
    # Construir DataFrame
    df_dict = {}
    for hotel_name, base_url, checkin, price in results:
        if base_url not in df_dict:
            df_dict[base_url] = {"Hotel Name": hotel_name, "URL": base_url}
        df_dict[base_url][checkin] = price
    final_results = list(df_dict.values())
    logger.info(f"Scraping completado. Total de hoteles procesados: {len(final_results)}")
    return final_results

if __name__ == '__main__':
    # Ejemplo de uso manual
    hotel_base_urls = [
        "https://www.booking.com/hotel/ar/el-pueblito-iguazu.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/guamini-mision-puerto-iguazu6.es.html?selected_currency=USD",
    ]
    days = 2
    nights = 1
    currency = "USD"
    scraped_data = scrape_booking_data(hotel_base_urls, days=days, nights=nights, currency=currency)
    print(scraped_data) 