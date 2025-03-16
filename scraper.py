import requests
from bs4 import BeautifulSoup
import json
import time
import logging

class FergusonScraper:
    def __init__(self):
        self.base_url = "https://www.ferguson.com"
        self.plumbing_url = "https://www.ferguson.com/category/plumbing"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
    def get_all_categories(self):
        """Get all plumbing categories"""
        try:
            response = requests.get(self.plumbing_url, headers=self.headers)
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

    def get_products_from_category(self, category_url):
        """Get all products from a specific category"""
        products = []
        page = 1
        
        while True:
            try:
                url = f"{category_url}?page={page}"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_cards = soup.find_all('div', class_='product-card')
                
                if not product_cards:
                    break
                
                for card in product_cards:
                    product = self.extract_product_info(card)
                    if product:
                        products.append(product)
                
                page += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
                
        return products

    def extract_product_info(self, card):
        """Extract information from a product card"""
        try:
            title = card.find('h2', class_='product-title').text.strip()
            price_elem = card.find('span', class_='price')
            price = float(price_elem.text.replace('$', '').replace(',', '')) if price_elem else None
            
            product_link = card.find('a', class_='product-link')
            product_url = self.base_url + product_link['href'] if product_link else None
            product_id = card.get('data-product-id', '')
            
            img = card.find('img')
            image_url = img['src'] if img else None
            
            brand_elem = card.find('div', class_='brand')
            brand = brand_elem.text.strip() if brand_elem else None
            
            return {
                'id': product_id,
                'name': title,
                'price': price,
                'brand': brand,
                'image_url': image_url,
                'product_url': product_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error extracting product info: {e}")
            return None

    def scrape_all_plumbing_products(self):
        """Main function to scrape all plumbing products"""
        all_products = []
        categories = self.get_all_categories()
        
        for category in categories:
            print(f"Scraping category: {category['name']}")
            products = self.get_products_from_category(category['url'])
            all_products.extend(products)
            self.save_products(all_products)
            time.sleep(2)
            
        return all_products
    
    def save_products(self, products, filename='ferguson_products.json'):
        """Save products to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(products, f, indent=2)
            print(f"Saved {len(products)} products to {filename}")
        except Exception as e:
            print(f"Error saving products: {e}")
