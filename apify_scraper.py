import time
import random
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

# Función para lanzar una ejecución individual del actor con retry logic y backoff exponencial
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
        "requestHandlerTimeoutSecs": 30,
        "maxRequestRetries": 3,
    }
    
    max_retries = 5
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Iniciando scraper para {hotel_name} - {checkin} (intento {attempt + 1}/{max_retries})")
            run = client.actor("voyager/booking-scraper").call(run_input=run_input)
            
            if run is None or "defaultDatasetId" not in run:
                logger.warning(f"No se pudo obtener dataset para {hotel_name} - {checkin}")
                return (hotel_name, base_url, checkin, None, None, None)
                
            dataset_id = run["defaultDatasetId"]
            items = client.dataset(dataset_id).list_items().items
            
            if not items:
                logger.warning(f"No se encontraron items para {hotel_name} - {checkin}")
                return (hotel_name, base_url, checkin, None, None, None)
                
            price = None
            rating = None
            reviews = None
            
            for item in items:
                # Extraer rating y reviews del item (solo una vez, son datos estáticos)
                if rating is None:
                    rating = item.get("rating")
                    reviews = item.get("reviews")
                
                if "rooms" in item and item["rooms"]:
                    for room in item["rooms"]:
                        if "options" in room and room["options"]:
                            for option in room["options"]:
                                try:
                                    price = str(float(option["displayedPrice"]))
                                    logger.info(f"Precio encontrado para {hotel_name} - {checkin}: {price}")
                                    return (hotel_name, base_url, checkin, price, rating, reviews)
                                except (ValueError, TypeError, KeyError):
                                    continue
                                    
            logger.warning(f"No se encontró precio válido para {hotel_name} - {checkin}")
            return (hotel_name, base_url, checkin, price, rating, reviews)
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detectar errores de rate limiting
            if "429" in error_msg or "too many requests" in error_msg or "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    # Backoff exponencial con jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), 30)
                    logger.warning(f"Rate limit detectado para {hotel_name} - {checkin}. Esperando {delay:.1f}s antes del reintento {attempt + 2}")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Rate limit persistente para {hotel_name} - {checkin} después de {max_retries} intentos")
                    return (hotel_name, base_url, checkin, None, None, None)
            else:
                # Otros errores - no reintentar
                logger.error(f"Error para {hotel_name} {checkin}: {e}")
                return (hotel_name, base_url, checkin, None, None, None)
    
    return (hotel_name, base_url, checkin, None, None, None)

def scrape_booking_data(hotel_base_urls, days=2, nights=1, currency="USD", start_date=None):
    """
    Scraping de Booking.com para múltiples hoteles, días, noches y moneda.
    
    Args:
        hotel_base_urls: Lista de URLs de hoteles
        days: Número de días a analizar
        nights: Número de noches por reserva
        currency: Moneda para los precios
        start_date: Fecha de inicio en formato "YYYY-MM-DD". Si es None, usa hoy.
    """
    logger.info(f"Iniciando scraping para {len(hotel_base_urls)} hoteles por {days} días, {nights} noches, moneda {currency}")
    logger.info(f"DEBUG - start_date recibido en scraper: {start_date} (tipo: {type(start_date)})")
    client = ApifyClient(APIFY_API_TOKEN)
    
    # Determinar fecha de inicio
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            logger.info(f"Usando fecha de inicio personalizada: {start_date}")
        except ValueError:
            logger.warning(f"Fecha de inicio inválida: {start_date}. Usando fecha actual.")
            start_datetime = datetime.now()
    else:
        start_datetime = datetime.now()
        logger.info(f"Usando fecha actual como inicio: {start_datetime.strftime('%Y-%m-%d')}")
    
    # Generar rangos de fechas con la cantidad de noches deseada
    date_ranges = [
        (
            (start_datetime + timedelta(days=i)).strftime("%Y-%m-%d"),
            (start_datetime + timedelta(days=i+nights)).strftime("%Y-%m-%d")
        )
        for i in range(0, days)
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
    with ThreadPoolExecutor(max_workers=15) as executor:
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
                results.append((hotel_name, base_url, checkin, None, None, None))
            # Delay reducido para acelerar el proceso
            time.sleep(0.5)
    # Construir DataFrame y recopilar metadata de hoteles
    df_dict = {}
    hotel_metadata = {}  # Diccionario: base_url -> {"rating": X, "reviews": Y, "name": Z}
    
    for hotel_name, base_url, checkin, price, rating, reviews in results:
        # Construir datos de precios por fecha
        if base_url not in df_dict:
            df_dict[base_url] = {"Hotel Name": hotel_name, "URL": base_url}
        
        # Recopilar metadata una vez por hotel (del primer resultado exitoso)
        if base_url not in hotel_metadata and (rating is not None or reviews is not None):
            hotel_metadata[base_url] = {
                "rating": rating,
                "reviews": reviews,
                "name": hotel_name
            }
            logger.info(f"Metadata recopilada para {hotel_name}: rating={rating}, reviews={reviews}")
        
        # Si nights > 1 y price es numérico, dividir por nights para obtener precio por noche
        if price is not None:
            try:
                price_float = float(price)
                if nights > 1:
                    price_float = round(price_float / nights, 2)
                df_dict[base_url][checkin] = price_float
            except Exception:
                df_dict[base_url][checkin] = price
        else:
            df_dict[base_url][checkin] = price
    
    final_results = list(df_dict.values())
    logger.info(f"Scraping completado. Total de hoteles procesados: {len(final_results)}")
    logger.info(f"Metadata recopilada para {len(hotel_metadata)} hoteles")
    
    # Retornar resultados y metadata
    return final_results, hotel_metadata

if __name__ == '__main__':
    # Ejemplo de uso manual
    hotel_base_urls = [
        "https://www.booking.com/hotel/ar/el-pueblito-iguazu.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/guamini-mision-puerto-iguazu6.es.html?selected_currency=USD",
    ]
    days = 2
    nights = 1
    currency = "USD"
    scraped_data, hotel_metadata = scrape_booking_data(hotel_base_urls, days=days, nights=nights, currency=currency)
    print(scraped_data)
    print("Metadata:", hotel_metadata) 