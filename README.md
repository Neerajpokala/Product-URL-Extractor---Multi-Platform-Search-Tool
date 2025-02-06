# Product URL Extractor - Multi-Platform Search Tool

A Streamlit application that extracts product URLs from multiple e-commerce platforms including Amazon, eBay, Walmart, and Airbnb. This tool allows users to search for products across different platforms and obtain a list of product URLs, which can be downloaded as CSV files.

![Streamlit App Demo](https://raw.githubusercontent.com/your-username/your-repo-name/main/demo.gif)

## 🌟 Features

- Multi-platform support:
  - Amazon product search
  - eBay product search
  - Walmart product search
  - Airbnb listing search
- User-friendly Streamlit interface
- Progress tracking during scraping
- CSV export functionality
- Automated pagination handling
- Rate limiting and anti-blocking measures

## 📁 Project Structure

```
product-url-extractor/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── scrapers/
│   ├── amazon.py          # Amazon scraper script
│   ├── ebay.py            # eBay scraper script
│   ├── walmart.py         # Walmart scraper script
│   └── airbnb.py          # Airbnb scraper script
└── README.md              # Project documentation
```

## 🔧 Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/product-url-extractor.git
cd product-url-extractor
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate     # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Streamlit app:
```bash
streamlit run app.py
```

## 💻 Usage

1. Select a platform (Amazon, eBay, Walmart, or Airbnb)
2. Enter your search query or URL (for Airbnb)
3. For Amazon, optionally adjust the number of pages to scrape
4. Click "Start Scraping"
5. Wait for the scraping to complete
6. Download the results as a CSV file

## 🔍 Detailed Component Breakdown

### Amazon Scraper (`amazon.py`)
```python
class AmazonScraper:
    def extract_product_urls(search_term, num_pages=1):
        """
        Extracts product URLs from Amazon search results using Selenium.
        Features:
        - Headless browser automation
        - Anti-detection measures
        - Pagination support
        - Product URL extraction
        """
```

The Amazon scraper uses Selenium with headless Chrome to:
- Navigate through search result pages
- Extract product URLs while avoiding detection
- Handle pagination automatically
- Process multiple pages of results

### eBay Scraper (`ebay.py`)
```python
class EbayScraper:
    def search_products(query):
        """
        Scrapes product URLs from eBay search results using requests.
        Features:
        - Session management
        - Custom headers
        - Multiple selectors for reliability
        - Automatic pagination
        """
```

The eBay scraper uses requests and BeautifulSoup to:
- Maintain sessions for consistent requests
- Use multiple CSS selectors for reliable extraction
- Handle pagination with next page detection
- Clean and validate product URLs

### Walmart Scraper (`walmart.py`)
```python
class WalmartScraper:
    def search_products(query):
        """
        Extracts product URLs from Walmart search results.
        Features:
        - Regular expression based URL extraction
        - Automatic pagination
        - Rate limiting
        """
```

The Walmart scraper implements:
- Regular expression based URL matching
- Automated pagination handling
- Rate limiting to avoid blocking
- URL validation and cleaning

### Airbnb Scraper (`airbnb.py`)
```python
class AirbnbScraper:
    def extract_urls(base_url):
        """
        Extracts listing URLs from Airbnb search results using Selenium.
        Features:
        - Stealth browser automation
        - Pattern-based URL extraction
        - Anti-bot detection measures
        """
```

The Airbnb scraper uses Selenium with stealth features to:
- Navigate search results without detection
- Extract listing URLs using regex patterns
- Handle dynamic content loading
- Implement anti-bot detection measures

### Streamlit Interface (`app.py`)

The main application integrates all scrapers into a unified interface with:
- Platform selection dropdown
- Dynamic input fields based on platform
- Progress tracking during scraping
- Results display and download functionality
- Session state management
- Error handling and user feedback

## ⚙️ Configuration

The scrapers include various configuration options:
- User agent rotation
- Request delays
- Page limits
- Headers customization

These can be modified in the respective scraper files to adjust behavior as needed.

## 🔒 Security & Rate Limiting

The application implements several measures to avoid detection and blocking:
- Random delays between requests
- Custom user agents
- Session management
- Request headers customization
- Maximum page limits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please review and comply with the terms of service of each platform before use.

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- Selenium and BeautifulSoup4 for making web scraping possible
- The open-source community for various utilities and libraries used

---
Made with ❤️ by [Neeraj Pokala]
