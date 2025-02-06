from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def setup_driver():
    """Set up and return a Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def extract_product_urls(search_term, num_pages=1):
    """
    Extract product URLs from Amazon search results.
    
    Args:
        search_term (str): The search term to look for on Amazon
        num_pages (int): Number of pages to scrape (default: 1)
    
    Returns:
        list: List of dictionaries containing product URLs and titles
    """
    driver = setup_driver()
    products = []
    
    try:
        for page in range(1, num_pages + 1):
            # Format the Amazon search URL
            url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}&page={page}"
            
            # Load the page
            driver.get(url)
            
            # Wait for the products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-item"))
            )
            
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all product containers
            product_cards = soup.find_all("div", {"data-component-type": "s-search-result"})
            
            for card in product_cards:
                try:
                    # Extract product URL and title
                    product_link = card.find("a", {"class": "a-link-normal s-no-outline"})
                    if product_link:
                        url = "https://www.amazon.com" + product_link.get('href')
                        title = card.find("span", {"class": "a-text-normal"})
                        title_text = title.text.strip() if title else "No title found"
                        
                        products.append({
                            # 'title': title_text,
                            'url': url
                        })
                except Exception as e:
                    print(f"Error extracting product: {e}")
            
            # Add a random delay between pages to avoid being blocked
            time.sleep(random.uniform(2, 4))
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    return products

def save_to_csv(products, filename='amazon_products.csv'):
    """Save the extracted products to a CSV file."""
    df = pd.DataFrame(products)
    df.to_csv(filename, index=False)
    print(f"Saved {len(products)} products to {filename}")

def main():
    # Example usage
    search_term = input("Enter the product to search for: ")
    num_pages = int(input("Enter the number of pages to scrape (default 1): ") or "1")
    
    print(f"Searching for '{search_term}' on Amazon...")
    products = extract_product_urls(search_term, num_pages)
    
    if products:
        save_to_csv(products)
    else:
        print("No products found.")

if __name__ == "__main__":
    main()