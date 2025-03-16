import streamlit as st
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Chicago Bathroom Fixtures - Kohler & TOTO",
    page_icon="🚽",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .product-image {
        width: 100%;
        height: 250px;
        object-fit: contain;
        margin-bottom: 15px;
    }
    .product-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .product-brand {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .kohler-brand {
        background: #0066cc;
        color: white;
    }
    .toto-brand {
        background: #e31837;
        color: white;
    }
    .product-price {
        font-size: 24px;
        font-weight: bold;
        color: #27ae60;
        margin: 10px 0;
    }
    .product-rating {
        color: #f39c12;
        margin-bottom: 10px;
    }
    .product-specs {
        font-size: 14px;
        color: #7f8c8d;
        margin: 10px 0;
    }
    .view-button {
        display: inline-block;
        padding: 8px 16px;
        background: #3498db;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        transition: background 0.3s;
    }
    .view-button:hover {
        background: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

def load_products():
    """Load products from JSON file"""
    try:
        with open("homedepot_products.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Product data not found. Please run the scraper first.")
        return []
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        return []

def filter_products(products, search_query, selected_brand, min_price, max_price):
    """Filter products based on user selections"""
    filtered = products

    # Filter by brand
    if selected_brand != "All":
        filtered = [p for p in filtered if p["brand"].upper() == selected_brand.upper()]

    # Filter by price range
    filtered = [p for p in filtered if min_price <= p["price"] <= max_price]

    # Filter by search query
    if search_query:
        search_terms = search_query.lower().split()
        filtered = [p for p in filtered if
                   any(term in p["name"].lower() or
                       term in p["description"].lower() or
                       term in str(p.get("specifications", {})).lower()
                       for term in search_terms)]

    return filtered

def main():
    st.title("Chicago Bathroom Fixtures")
    st.subheader("Premium Kohler & TOTO Products")

    # Load products
    products = load_products()
    
    if not products:
        return

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Brand selection
        selected_brand = st.selectbox(
            "Brand",
            ["All", "KOHLER", "TOTO"]
        )

        # Price range
        prices = [p["price"] for p in products if p["price"]]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 5000
        
        price_range = st.slider(
            "Price Range ($)",
            min_value=float(min_price),
            max_value=float(max_price),
            value=(float(min_price), float(max_price))
        )

    # Search bar
    search_query = st.text_input("Search products", "")

    # Filter products
    filtered_products = filter_products(
        products,
        search_query,
        selected_brand,
        price_range[0],
        price_range[1]
    )

    # Display products in a grid
    cols = st.columns(3)
    for idx, product in enumerate(filtered_products):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{product['image_url']}" class="product-image" onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
                <div class="product-title">{product['name']}</div>
                <div class="product-brand {'kohler-brand' if product['brand'].upper() == 'KOHLER' else 'toto-brand'}">{product['brand']}</div>
                <div class="product-price">${product['price']:,.2f}</div>
                <div class="product-rating">★ {product['rating']} ({product['review_count']} reviews)</div>
                <div class="product-specs">
                    <strong>Model:</strong> {product['model']}<br>
                    {product['description'][:200]}...
                </div>
                <a href="{product['product_url']}" target="_blank" class="view-button">View on Home Depot</a>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
