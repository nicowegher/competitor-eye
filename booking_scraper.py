
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def get_hotel_info(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (without opening a browser window)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Explicitly set the path to chromedriver
    service = Service(executable_path="/home/ubuntu/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    try:
        # Wait for the page to load and find the hotel name using its class name
        # The class name 'd2fee87262' seems to be a dynamic part, so let's try a more stable one or a combination
        # Based on inspection, the main hotel name is often within an h1 tag with a specific class.
        # Let's try to find the h1 tag that contains the text 'Barceló Sants' or similar.
        # A more robust way is to find the element by its unique ID if available, or by a more specific CSS selector.
        # From the browser view, the hotel name is 'Barceló Sants' and it's within an h1 tag.
        # Let's try to find the h1 tag that is a direct child of a div with a specific class.
        # Or, we can try to find the element by its text content if it's unique enough.
        
        # Let's try to find the h1 tag with the class 'd2fee87262 pp-header__title' which was present in the previous output.
        # If that doesn't work, we'll try a different approach.
        hotel_name_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.d2fee87262.pp-header__title"))
        )
        hotel_name = hotel_name_element.text.strip()
        
        print(f"Hotel Name: {hotel_name}")
        return {"Hotel Name": hotel_name, "URL": url}

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    finally:
        driver.quit()

if __name__ == '__main__':
    example_url = 'https://www.booking.com/hotel/es/barcelo-sants.es.html'
    hotel_data = get_hotel_info(example_url)
    if hotel_data:
        df = pd.DataFrame([hotel_data])
        print(df)


