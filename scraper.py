import requests
from bs4 import BeautifulSoup
import json
import time
import logging

class FergusonScraper:
    def __init__(self):
        self.base_url = "https://www.ferguson.com"
        self.brand_urls = {
            'KOHLER': 'https://www.ferguson.com/category/brands/kohler/_/N-zbq3n5',
            'TOTO': 'https://www.ferguson.com/category/brands/toto/_/N-zbq40g'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def get_products_for_brand(self, brand_name, brand_url):
        """Get all products for a specific brand"""
        products = []
        page = 1
        
        while True:
            try:
                # Construct URL with pagination
                url = f"{brand_url}?page={page}"
                print(f"Scraping {brand_name} - Page {page}")
                
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    print(f"Failed to get page {page} for {brand_name}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all product containers
                product_containers = soup.find_all('div', class_='product-container')
                
                if not product_containers:
                    print(f"No more products found for {brand_name} on page {page}")
                    break
                
                for container in product_containers:
                    product = self.extract_product_info(container, brand_name)
                    if product:
                        products.append(product)
                        print(f"Added product: {product['name']}")
                
                # Check if there's a next page
                next_button = soup.find('a', {'aria-label': 'Next'})
                if not next_button:
                    print(f"No more pages for {brand_name}")
                    break
                
                page += 1
                time.sleep(2)  # Be nice to the server
                
            except Exception as e:
                print(f"Error on page {page} for {brand_name}: {e}")
                break
        
        return products

    def extract_product_info(self, container, brand_name):
        """Extract product information from container"""
        try:
            # Get product name
            name_elem = container.find('a', class_='product-description')
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            product_url = self.base_url + name_elem['href']
            
            # Get product ID
            product_id = container.get('data-itemid', '')
            
            # Get price
            price_elem = container.find('span', class_='price')
            price = None
            if price_elem:
                price_text = price_elem.text.strip().replace('$', '').replace(',', '')
                try:
                    price = float(price_text)
                except:
                    pass
            
            # Get image
            img_elem = container.find('img', class_='product-image')
            image_url = img_elem['src'] if img_elem else None
            
            # Get category
            category_elem = container.find('div', class_='product-category')
            category = category_elem.text.strip() if category_elem else 'Uncategorized'
            
            # Get description
            desc_elem = container.find('div', class_='product-details')
            description = desc_elem.text.strip() if desc_elem else ''
            
            # Get specifications
            specs = {}
            spec_list = container.find_all('div', class_='specification')
            for spec in spec_list:
                label = spec.find('span', class_='label')
                value = spec.find('span', class_='value')
                if label and value:
                    specs[label.text.strip()] = value.text.strip()
            
            # Get model number
            model_elem = container.find('div', class_='model-number')
            model_number = model_elem.text.strip() if model_elem else ''
            
            return {
                'id': product_id,
                'name': name,
                'brand': brand_name,
                'price': price,
                'model_number': model_number,
                'category': category,
                'description': description,
                'specifications': specs,
                'image_url': image_url,
                'product_url': product_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting product info: {e}")
            return None

    def scrape_all_products(self):
        """Scrape all products from both brands"""
        all_products = []
        
        for brand_name, brand_url in self.brand_urls.items():
            print(f"\nStarting to scrape {brand_name} products...")
            brand_products = self.get_products_for_brand(brand_name, brand_url)
            all_products.extend(brand_products)
            print(f"Found {len(brand_products)} {brand_name} products")
            
            # Save progress after each brand
            self.save_products(all_products)
            time.sleep(3)  # Pause between brands
        
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
    print("Starting scraper...")
    products = scraper.scrape_all_products()
    print(f"\nScraping completed. Total products found: {len(products)}")

if __name__ == "__main__":
    main()
