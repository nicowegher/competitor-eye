import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from apify_client import ApifyClient
import pandas as pd
from urllib.parse import urlparse, parse_qs

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
        "proxyConfiguration": {"useApifyProxy": True},
        "currency": "USD",
        "language": "es",
        "maxPagesPerCrawl": 1,
        "maxItems": 1,
    }
    try:
        run = client.actor("voyager/booking-scraper").call(run_input=run_input)
        if run is None or "defaultDatasetId" not in run:
            return (hotel_name, base_url, checkin, "N/A")
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        price = "N/A"
        for item in items:
            if "rooms" in item and item["rooms"]:
                for room in item["rooms"]:
                    if "options" in room and room["options"]:
                        for option in room["options"]:
                            try:
                                price = str(float(option["displayedPrice"]))
                                return (hotel_name, base_url, checkin, price) # Devolver el primer precio encontrado
                            except (ValueError, TypeError, KeyError):
                                continue
        return (hotel_name, base_url, checkin, price)
    except Exception as e:
        print(f"Error para {hotel_name} {checkin}: {e}")
        return (hotel_name, base_url, checkin, "N/A")

def scrape_booking_data(hotel_base_urls):
    client = ApifyClient(APIFY_API_TOKEN)
    today = datetime.now()
    date_ranges = [
        ((today + timedelta(days=i)).strftime("%Y-%m-%d"), (today + timedelta(days=i+1)).strftime("%Y-%m-%d"))
        for i in range(1, 3)
    ]
    # Obtener nombres de hoteles (opcional, se puede mejorar)
    url_to_name = {url: url.split("/hotel/")[-1].split(".")[0].replace("-", " ").title() for url in hotel_base_urls}
    # Lista de tareas
    tasks = []
    for base_url in hotel_base_urls:
        hotel_name = url_to_name[base_url]
        for checkin, checkout in date_ranges:
            tasks.append((base_url, hotel_name, checkin, checkout))
    print(f"Lanzando {len(tasks)} ejecuciones individuales (esto puede tardar varios minutos)...")
    results = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_task = {
            executor.submit(fetch_price_for_night, client, base_url, hotel_name, checkin, checkout): (base_url, hotel_name, checkin, checkout)
            for (base_url, hotel_name, checkin, checkout) in tasks
        }
        for i, future in enumerate(as_completed(future_to_task), 1):
            base_url, hotel_name, checkin, checkout = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"Error en {hotel_name} {checkin}: {exc}")
            if i % 10 == 0 or i == len(tasks):
                print(f"Progreso: {i}/{len(tasks)} ejecuciones completadas")
    # Construir DataFrame
    df_dict = {}
    for hotel_name, base_url, checkin, price in results:
        if base_url not in df_dict:
            df_dict[base_url] = {"Hotel Name": hotel_name, "URL": base_url}
        df_dict[base_url][checkin] = price
    return list(df_dict.values())

def main():
    # URLs base de los hoteles (sin parámetros de fecha)
    hotel_base_urls = [
        "https://www.booking.com/hotel/ar/el-pueblito-iguazu.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/guamini-mision-puerto-iguazu6.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/la-aldea-de-la-selva-lodge.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/esturion.es.html?selected_currency=USD",
        "https://www.booking.com/hotel/ar/exehotelcataratas.es.html?selected_currency=USD",
        # Agrega más URLs aquí si lo deseas
    ]
    
    if APIFY_API_TOKEN == "YOUR_APIFY_API_TOKEN":
        print("ERROR: Por favor, reemplaza 'YOUR_APIFY_API_TOKEN' con tu token real de Apify en el archivo apify_scraper.py.")
        return

    scraped_data = scrape_booking_data(hotel_base_urls)

    if scraped_data:
        df = pd.DataFrame(scraped_data)
        
        # Guardar en Excel
        excel_filename = f"tarifas_hoteles_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(excel_filename, index=False)
        print(f"Datos guardados en {excel_filename}")
        
        # Guardar en CSV
        csv_filename = f"tarifas_hoteles_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Datos guardados en {csv_filename}")
    else:
        print("No se obtuvieron datos de scraping.")

if __name__ == "__main__":
    main()


