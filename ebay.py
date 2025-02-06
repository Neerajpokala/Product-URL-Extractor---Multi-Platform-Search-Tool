import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin, quote_plus

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
            'DNT': '1'  # Do Not Track header
        }
        self.session = requests.Session()
        
    def search_products(self, query):
        products = []
        page = 1
        
        try:
            while True:
                print(f"Scraping page {page}...")
                
                # Construct the search URL with pagination
                encoded_query = quote_plus(query)
                if page == 1:
                    search_url = f"{self.base_url}/sch/i.html?_nkw={encoded_query}&_ipg=240"  # 240 items per page
                else:
                    search_url = f"{self.base_url}/sch/i.html?_nkw={encoded_query}&_ipg=240&_pgn={page}"
                
                print(f"Fetching URL: {search_url}")
                
                # Use session to maintain cookies
                response = self.session.get(search_url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all product listings
                product_listings = soup.find_all('div', class_='s-item__wrapper')
                
                if not product_listings:
                    # Try alternative selector
                    product_listings = soup.find_all('div', class_='s-item')
                    
                if not product_listings:
                    print("No product listings found. Trying alternative selectors...")
                    # Try to find direct product links
                    product_listings = soup.find_all('a', class_='s-item__link')
                
                if not product_listings:
                    print("No more products found.")
                    break
                
                new_products_found = False
                for listing in product_listings:
                    # Try to find the product link
                    product_link = listing.find('a', class_='s-item__link') if hasattr(listing, 'find') else listing
                    
                    if product_link and product_link.get('href'):
                        product_url = product_link['href']
                        
                        # Filter out non-product URLs and sponsored links
                        if '/itm/' in product_url and product_url not in products:
                            # Clean the URL by removing tracking parameters
                            clean_url = product_url.split('?')[0]
                            print(f"Found product URL: {clean_url}")
                            products.append(clean_url)
                            new_products_found = True
                
                if not new_products_found:
                    print("No new products found on this page.")
                    break
                
                # Check for next page button
                next_button = soup.find('a', {'aria-label': 'Next page'})
                if not next_button:
                    print("No next page button found.")
                    break
                
                # Get total number of items if available
                total_items = soup.find('h1', class_='srp-controls__count-heading')
                if total_items:
                    print(f"Total items found: {total_items.text.strip()}")
                
                # Random delay between requests (2-4 seconds)
                delay = random.uniform(2, 4)
                print(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
                
                page += 1
                
                # Optional: limit to first 5 pages
                if page > 5:
                    print("Reached maximum page limit.")
                    break
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        return products
    
    def save_to_csv(self, products, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Product URL'])
            for url in products:
                writer.writerow([url])

def main():
    scraper = EbayScraper()
    search_query = input("Enter your search query (e.g., 's24 ultra'): ")
    
    print("Starting scraping process...")
    products = scraper.search_products(search_query)
    
    filename = f"ebay_{search_query.replace(' ', '_')}_products.csv"
    scraper.save_to_csv(products, filename)
    
    print(f"\nScraping completed!")
    print(f"Found {len(products)} unique product URLs")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()