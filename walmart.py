import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin
import re

class WalmartScraper:
    def __init__(self):
        self.base_url = "https://www.walmart.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
    def search_products(self, query):
        search_url = f"{self.base_url}/search?q={query.replace(' ', '+')}"
        products = []
        page = 1
        
        try:
            while True:
                print(f"Scraping page {page}...")
                current_url = f"{search_url}&page={page}"
                response = requests.get(current_url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                product_elements = soup.find_all('a', href=re.compile(r'/ip/'))
                
                if not product_elements:
                    break
                
                for element in product_elements:
                    product_url = urljoin(self.base_url, element['href'])
                    if product_url not in products:
                        products.append(product_url)
                
                # Random delay between requests (1-3 seconds)
                time.sleep(random.uniform(1, 3))
                page += 1
                
                # Optional: limit to first 5 pages for testing
                if page > 5:
                    break
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        return products
    
    def save_to_csv(self, products, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Product URL'])
            for url in products:
                writer.writerow([url])
                
def main():
    scraper = WalmartScraper()
    search_query = input("Enter your search query (e.g., 's24 ultra'): ")
    
    print("Starting scraping process...")
    products = scraper.search_products(search_query)
    
    filename = f"walmart_{search_query.replace(' ', '_')}_products.csv"
    scraper.save_to_csv(products, filename)
    
    print(f"\nScraping completed!")
    print(f"Found {len(products)} unique product URLs")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()