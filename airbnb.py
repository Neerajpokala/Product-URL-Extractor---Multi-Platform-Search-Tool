from selenium import webdriver
from selenium_stealth import stealth
import time
import re 
import pandas as pd
from datetime import datetime

def setup_driver():
    """Set up and return a Chrome WebDriver with stealth options."""
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    # Stealth setup to avoid detection
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    return driver

def extract_urls(base_url):
    """Extract property URLs from the given Airbnb page."""
    driver = setup_driver()
    url_list = []
    
    try:
        # Load the page
        driver.get(base_url)
        time.sleep(5)  # Wait for page to load completely
        
        # Fetch page source
        html_content = driver.page_source
        
        # Define regex pattern for property URLs
        url_pattern = 'labelledby="[^"]+" href="(\/rooms\/\d+[^"]+)"'
        
        # Find all matching URLs
        urls = re.findall(url_pattern, html_content)
        
        # Create full URLs and store them
        for url in urls:
            full_url = "https://www.airbnb.com" + url
            url_list.append({'url': full_url})
        
        print(f"Found {len(url_list)} URLs")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        driver.quit()
        
    return url_list

def save_to_csv(urls, filename=None):
    """Save the extracted URLs to a CSV file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"airbnb_urls_{timestamp}.csv"
    
    df = pd.DataFrame(urls)
    df.to_csv(filename, index=False)
    print(f"Saved {len(urls)} URLs to {filename}")

def main():
    # Get input URL
    base_url = input("Enter the Airbnb search URL: ")
    
    print("Starting URL extraction...")
    urls = extract_urls(base_url)
    
    if urls:
        save_to_csv(urls)
    else:
        print("No URLs found.")

if __name__ == "__main__":
    main()