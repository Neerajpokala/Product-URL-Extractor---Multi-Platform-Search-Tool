import streamlit as st
import pandas as pd
import base64
import sys
import io
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import random

# Initialize session state
if 'scraping_completed' not in st.session_state:
    st.session_state.scraping_completed = False
if 'results_df' not in st.session_state:
    st.session_state.results_df = None

# Scraper Classes and Functions
class AmazonScraper:
    @staticmethod
    def setup_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        return webdriver.Chrome(options=chrome_options)

    @staticmethod
    def extract_product_urls(search_term, progress_bar, num_pages=1):
        driver = AmazonScraper.setup_driver()
        products = []
        
        try:
            for page in range(1, num_pages + 1):
                progress_bar.progress(page / num_pages)
                url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}&page={page}"
                driver.get(url)
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                product_cards = soup.find_all("div", {"data-component-type": "s-search-result"})
                
                for card in product_cards:
                    try:
                        product_link = card.find("a", {"class": "a-link-normal s-no-outline"})
                        if product_link:
                            url = "https://www.amazon.com" + product_link.get('href')
                            products.append({'url': url})
                    except Exception as e:
                        st.error(f"Error extracting product: {e}")
                
                time.sleep(2)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        finally:
            driver.quit()
        
        return products

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }
        self.session = requests.Session()

    def search_products(self, query, progress_bar):
        products = []
        page = 1
        status_text = st.empty()
        
        try:
            while True:
                status_text.text(f"Scraping eBay page {page}...")
                
                encoded_query = quote_plus(query)
                if page == 1:
                    search_url = f"{self.base_url}/sch/i.html?_nkw={encoded_query}&_ipg=240"
                else:
                    search_url = f"{self.base_url}/sch/i.html?_nkw={encoded_query}&_ipg=240&_pgn={page}"
                
                response = self.session.get(search_url, headers=self.headers)
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_listings = soup.find_all('div', class_='s-item__wrapper')
                
                if not product_listings:
                    product_listings = soup.find_all('div', class_='s-item')
                    
                if not product_listings:
                    product_listings = soup.find_all('a', class_='s-item__link')
                
                if not product_listings:
                    break
                
                new_products_found = False
                for listing in product_listings:
                    product_link = listing.find('a', class_='s-item__link') if hasattr(listing, 'find') else listing
                    
                    if product_link and product_link.get('href'):
                        product_url = product_link['href']
                        
                        if '/itm/' in product_url and product_url not in products:
                            clean_url = product_url.split('?')[0]
                            products.append(clean_url)
                            new_products_found = True
                
                if not new_products_found:
                    break
                
                next_button = soup.find('a', {'aria-label': 'Next page'})
                if not next_button:
                    break
                
                progress_bar.progress(min(page / 5, 1.0))
                delay = random.uniform(2, 4)
                time.sleep(delay)
                
                page += 1
                if page > 5:
                    break
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        progress_bar.progress(1.0)
        status_text.empty()
        return [{'url': url} for url in products]

class WalmartScraper:
    def __init__(self):
        self.base_url = "https://www.walmart.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def search_products(self, query, progress_bar):
        search_url = f"{self.base_url}/search?q={query.replace(' ', '+')}"
        products = []
        page = 1
        status_text = st.empty()
        
        try:
            while True:
                status_text.text(f"Scraping Walmart page {page}...")
                current_url = f"{search_url}&page={page}"
                response = requests.get(current_url, headers=self.headers)
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_elements = soup.find_all('a', href=re.compile(r'/ip/'))
                
                if not product_elements:
                    break
                
                for element in product_elements:
                    product_url = urljoin(self.base_url, element['href'])
                    if product_url not in products:
                        products.append(product_url)
                
                progress_bar.progress(min(page / 5, 1.0))
                time.sleep(random.uniform(1, 3))
                page += 1
                
                if page > 5:
                    break
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        progress_bar.progress(1.0)
        status_text.empty()
        return [{'url': url} for url in products]

class AirbnbScraper:
    @staticmethod
    def setup_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

    @staticmethod
    def extract_urls(base_url, progress_bar):
        driver = AirbnbScraper.setup_driver()
        url_list = []
        
        try:
            progress_bar.progress(0.3)
            driver.get(base_url)
            time.sleep(5)
            
            progress_bar.progress(0.6)
            html_content = driver.page_source
            url_pattern = 'labelledby="[^"]+" href="(\/rooms\/\d+[^"]+)"'
            urls = re.findall(url_pattern, html_content)
            
            progress_bar.progress(0.9)
            for url in urls:
                full_url = "https://www.airbnb.com" + url
                url_list.append({'url': full_url})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        finally:
            driver.quit()
            progress_bar.progress(1.0)
        
        return url_list

def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

# Streamlit UI
st.title("Multi-Platform Web Scraper")

# Scraper selection
scraper_option = st.selectbox(
    "Select Platform",
    ["Amazon", "eBay", "Walmart", "Airbnb"]
)

# Input field based on selected scraper
if scraper_option == "Airbnb":
    user_input = st.text_input("Enter Airbnb search URL:")
    input_type = "url"
else:
    user_input = st.text_input("Enter search query:")
    input_type = "query"
    # Show pages slider only for Amazon
    if scraper_option == "Amazon":
        num_pages = st.slider("Number of pages to scrape", 1, 10, 5)

# Scrape button
if st.button("Start Scraping"):
    if user_input:
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        progress_text.text("Scraping in progress...")
        
        try:
            if scraper_option == "Amazon":
                results = AmazonScraper.extract_product_urls(user_input, progress_bar, num_pages)
            elif scraper_option == "eBay":
                scraper = EbayScraper()
                results = scraper.search_products(user_input, progress_bar)
            elif scraper_option == "Walmart":
                scraper = WalmartScraper()
                results = scraper.search_products(user_input, progress_bar)
            elif scraper_option == "Airbnb":
                results = AirbnbScraper.extract_urls(user_input, progress_bar)
            
            if results:
                st.session_state.results_df = pd.DataFrame(results)
                st.session_state.scraping_completed = True
                progress_text.text("Scraping completed!")
            else:
                st.warning("No results found.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        progress_bar.empty()

# Download section
if st.session_state.scraping_completed and st.session_state.results_df is not None:
    st.subheader("Results")
    st.dataframe(st.session_state.results_df)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{scraper_option.lower()}_results_{timestamp}.csv"
    
    st.markdown(get_csv_download_link(st.session_state.results_df, filename), unsafe_allow_html=True)
    st.info(f"Found {len(st.session_state.results_df)} URLs")