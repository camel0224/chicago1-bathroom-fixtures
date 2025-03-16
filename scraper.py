import requests
from bs4 import BeautifulSoup
import json
import time
import logging

class FergusonScraper:
    def __init__(self):
        self.base_url = "https://www.ferguson.com"
        self.brands = {
            'kohler': '/brands/kohler',
            'toto': '/brands/toto'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def get_brand_categories(self, brand_url):
        """Get all categories for a specific brand"""
        try:
            response = requests.get(self.base_url + brand_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            categories = []
            category_links = soup.find_all('a', class_='category-link')
            
            for link in category_links:
                category_url = self.base_url + link['href']
                category_name = link.text.strip()
                categories.append({
                    'name': category_name,
                    'url': category_url
                })
            
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def get_products_from_category(self, category_url, brand):
        """Get all products from a specific category"""
        products = []
        page = 1
        
        while True:
            try:
                # Add brand filter to URL
                url = f"{category_url}?page={page}&brand={brand}"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_cards = soup.find_all('div', class_='product-card')
                
                if not product_cards:
                    break
                
                for card in product_cards:
                    product = self.extract_product_info(card, brand)
                    if product:
                        products.append(product)
                
                # Check for next page
                next_button = soup.find('a', class_='next-page')
                if not next_button:
                    break
                
                page += 1
                time.sleep(1)  # Be nice to the server
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
                
        return products

    def extract_product_info(self, card, brand):
        """Extract information from a product card"""
        try:
            # Basic product info
            title = card.find('h2', class_='product-title').text.strip()
            
            # Get price
            price_elem = card.find('span', class_='price')
            price = float(price_elem.text.replace('$', '').replace(',', '')) if price_elem else None
            
            # Get product link and ID
            product_link = card.find('a', class_='product-link')
            product_url = self.base_url + product_link['href'] if product_link else None
            product_id = card.get('data-product-id', '')
            
            # Get image
            img = card.find('img')
            image_url = img['src'] if img else None
            
            # Get description
            desc_elem = card.find('div', class_='description')
            description = desc_elem.text.strip() if desc_elem else ''
            
            # Get specifications
            specs = {}
            spec_list = card.find_all('div', class_='specification')
            for spec in spec_list:
                key = spec.find('span', class_='label')
                value = spec.find('span', class_='value')
                if key and value:
                    specs[key.text.strip()] = value.text.strip()
            
            return {
                'id': product_id,
                'name': title,
                'price': price,
                'brand': brand.upper(),
                'image_url': image_url,
                'product_url': product_url,
                'description': description,
                'specifications': specs,
                'category': self.get_product_category(card),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting product info: {e}")
            return None

    def get_product_category(self, card):
        """Extract category from breadcrumb"""
        try:
            breadcrumb = card.find('div', class_='breadcrumb')
            if breadcrumb:
                return breadcrumb.text.strip()
            return "Uncategorized"
        except:
            return "Uncategorized"

    def scrape_brand_products(self):
        """Scrape all products from Kohler and TOTO"""
        all_products = []
        
        for brand, brand_url in self.brands.items():
            print(f"Scraping {brand.upper()} products...")
            categories = self.get_brand_categories(brand_url)
            
            for category in categories:
                print(f"Scraping category: {category['name']}")
                products = self.get_products_from_category(category['url'], brand)
                all_products.extend(products)
                
                # Save progress after each category
                self.save_products(all_products)
                time.sleep(2)  # Be nice to the server
        
        return all_products
    
    def save_products(self, products, filename='ferguson_products.json'):
        """Save products to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(products, f, indent=2)
            print(f"Saved {len(products)} products to {filename}")
        except Exception as e:
            print(f"Error saving products: {e}")

def main():
    scraper = FergusonScraper()
    products = scraper.scrape_brand_products()
    print(f"Total products scraped: {len(products)}")

if __name__ == "__main__":
    main()
