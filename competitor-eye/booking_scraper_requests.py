
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup

def get_hotel_info_requests(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the hotel name. This might need adjustment based on Booking.com's HTML structure.
        hotel_name_tag = soup.find('h2', class_='d2fee87262 pp-header__title') or \
                         soup.find('h2', id='hp_hotel_name') or \
                         soup.find('h1', class_='d2fee87262 pp-header__title')

        hotel_name = hotel_name_tag.text.strip() if hotel_name_tag else 'Nombre de hotel no encontrado'
        
        # For now, we'll just get the hotel name. Price extraction will be more complex.
        print(f"Hotel Name: {hotel_name}")
        return {"Hotel Name": hotel_name, "URL": url}

    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud para {url}: {e}")
        return None
    except Exception as e:
        print(f"Error al parsear {url}: {e}")
        return None

if __name__ == '__main__':
    example_url = 'https://www.booking.com/hotel/es/hotel-barcelona-plaza.es.html'
    hotel_data = get_hotel_info_requests(example_url)
    if hotel_data:
        df = pd.DataFrame([hotel_data])
        print(df)


