import requests
import json
import time
from typing import Dict, List, Optional

class HomeDepotScraper:
    def __init__(self):
        self.api_key = "YOUR_SERPAPI_KEY"  # You'll need to replace this with your actual SerpApi key
        self.base_url = "https://serpapi.com/search"
        self.brands = {
            "KOHLER": "Kohler",
            "TOTO": "TOTO"
        }
        
    def get_products_for_brand(self, brand: str, category: str = "Bathroom") -> List[Dict]:
        """Fetch products for a specific brand from Home Depot via SerpApi."""
        products = []
        start = 0
        
        while True:
            params = {
                "engine": "home_depot",
                "api_key": self.api_key,
                "q": f"{brand} {category}",
                "start": start,
                "store_id": "store_id",  # Replace with your local store ID
                "delivery_zip": "zip_code"  # Replace with your delivery zip code
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                data = response.json()
                
                if "products" not in data or not data["products"]:
                    break
                    
                for product in data["products"]:
                    product_info = {
                        "brand": brand,
                        "name": product.get("title", ""),
                        "model": product.get("model_number", ""),
                        "price": product.get("price", 0),
                        "description": product.get("description", ""),
                        "specifications": product.get("specifications", {}),
                        "image_url": product.get("images", [["]])[0][0] if product.get("images") else "",
                        "product_url": product.get("link", ""),
                        "rating": product.get("rating", 0),
                        "review_count": product.get("reviews", 0)
                    }
                    products.append(product_info)
                
                start += len(data["products"])
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching products for {brand}: {str(e)}")
                break
        
        return products

    def scrape_all_products(self) -> None:
        """Scrape all products from specified brands and save to JSON."""
        all_products = []
        
        for brand in self.brands.values():
            print(f"Fetching {brand} products...")
            products = self.get_products_for_brand(brand)
            all_products.extend(products)
            print(f"Found {len(products)} {brand} products")
        
        # Save to JSON file
        with open("homedepot_products.json", "w") as f:
            json.dump(all_products, f, indent=2)
        
        print(f"Total products saved: {len(all_products)}")

if __name__ == "__main__":
    scraper = HomeDepotScraper()
    scraper.scrape_all_products()
