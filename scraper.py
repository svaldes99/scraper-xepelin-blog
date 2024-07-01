import sys
import json
import os
import pygsheets
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import unicodedata
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Función para limpiar el texto de tildes y diacríticos
def limpiar_string(texto):
    texto_limpio = ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
    return texto_limpio

# Función para extraer los detalles de cada noticia
def extract_news_details(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(2)

    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ArticleSingle_title__0DNjm"))
        ).text.strip()
    except TimeoutException:
        title = "No title found"

    try:
        category = driver.find_element(By.CSS_SELECTOR, "a.text-primary-main").text.strip()
    except NoSuchElementException:
        category = "No category found"

    try:
        read_time_text = driver.find_element(By.CSS_SELECTOR, "div.Text_body__snVk8").text.strip()
        read_time = int(read_time_text.split()[0])
    except (NoSuchElementException, ValueError):
        read_time = 0

    try:
        author = driver.find_element(By.CSS_SELECTOR, "div.text-sm").text.strip()
    except NoSuchElementException:
        author = "No author found"

    driver.quit()

    return {
        "title": title,
        "category": category,
        "read_time": read_time,
        "author": author
    }

# Función para extraer todas las noticias de una página
def extract_all_news(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)

    try:
        while True:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.inline-flex.cursor-pointer"))
            ).click()
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "button.inline-flex.cursor-pointer.disabled"))
            )
    except TimeoutException:
        pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    news_links = [a_tag.get('href') for a_tag in soup.find_all('a', class_='absolute z-10 h-full w-full') if a_tag.get('href')]

    driver.quit()

    news_details = []
    for link in news_links:
        news_detail = extract_news_details(link)
        news_details.append(news_detail)

        # Limpieza de los datos
        news_detail['title'] = limpiar_string(news_detail['title'])
        news_detail['category'] = limpiar_string(news_detail['category'])
        news_detail['author'] = limpiar_string(news_detail['author'])

        
    
    return news_details

# Función para extraer todas las categorías disponibles en el blog
def extract_all_categories(base_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(base_url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    category_links = [a_tag.get('href').split('/')[-1] for a_tag in soup.find_all('a', class_='relative z-10 flex cursor-pointer items-center py-[11px] text-xs font-semibold tracking-wide text-xsky-700 transition duration-300 hover:text-xindigo-500 xl:text-sm') if a_tag.get('href')]

    driver.quit()
    
    return category_links

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)

    category = sys.argv[1]

    if category == "todo":
        base_url = 'https://xepelin.com/blog'
        categories = extract_all_categories(base_url)
    else:
        categories = [category]

    all_news_details = []

    for category in categories:
        url = f'https://xepelin.com/blog/{category}'
        try:
            news_details = extract_all_news(url)
            all_news_details.extend(news_details)
        except Exception as e:
            print(f"Error processing category '{category}': {e}")

    news_json = json.dumps(all_news_details, indent=4, ensure_ascii=False)

    try:
        # Obtener la ruta de las credenciales de Google Sheets del archivo .env
        credentials_path = os.getenv('CREDENTIALS_PATH')

        # Crear un cliente de Google Sheets y autenticarse
        gc = pygsheets.authorize(service_file=credentials_path)

        # Obtener el ID de la hoja de cálculo del archivo .env
        spreadsheet_id = os.getenv('SPREADSHEET_ID')

        # Abrir la hoja de cálculo por su ID
        sh = gc.open_by_key(spreadsheet_id)

        # Seleccionar la primera hoja
        wks = sh[0]

        # Borrar los datos antiguos
        wks.clear()

        # Convertir la lista de diccionarios en filas de datos
        if all_news_details:
            columns = list(all_news_details[0].keys())
            values = [list(news_item.values()) for news_item in all_news_details]

            # Insertar los títulos de las columnas en la primera fila
            wks.insert_rows(row=0, number=0, values=[columns])

            # Insertar los valores de las noticias en las filas siguientes
            wks.insert_rows(row=1, number=len(values), values=values)

        print("News details have been written to the Google Sheet.")

    except Exception as e:
        print(f"Error writing to Google Sheet: {e}")
        sys.exit(1)
