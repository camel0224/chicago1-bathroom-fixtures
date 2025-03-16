import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
from scraper import FergusonScraper

# Page setup
st.set_page_config(
    page_title="Chicago Bathroom Fixtures - Kohler & TOTO",
    page_icon="🚽",
    layout="wide"
)

# Custom CSS with improved styling
st.markdown("""
    <style>
    .product-card {
        border: 1px solid #ddd;
        padding: 20px;
        margin: 10px;
        border-radius: 8px;
        text-align: center;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .product-image {
        max-width: 250px;
        height: 250px;
        object-fit: contain;
        margin-bottom: 15px;
    }
    .product-title {
        font-size: 1.2em;
        font-weight: bold;
        margin: 10px 0;
        color: #1a237e;
    }
    .product-brand {
        color: #1e88e5;
        font-weight: bold;
        font-size: 1.1em;
        margin: 5px 0;
    }
    .product-price {
        color: #2c3e50;
        font-size: 1.3em;
        font-weight: bold;
        margin: 10px 0;
    }
    .product-description {
        font-size: 0.9em;
        color: #666;
        margin: 10px 0;
        text-align: left;
    }
    .product-specs {
        font-size: 0.85em;
        text-align: left;
        margin: 10px 0;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 4px;
    }
    .view-button {
        background-color: #1E88E5;
        color: white;
        padding: 10px 20px;
        border-radius: 4px;
        text-decoration: none;
        margin-top: 15px;
        display: inline-block;
        transition: background-color 0.2s;
    }
    .view-button:hover {
        background-color: #1565C0;
    }
    .category-badge {
        background: #e3f2fd;
        color: #1565C0;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_ferguson_products():
    """Fetch and cache products from Ferguson"""
    try:
        scraper = FergusonScraper()
        return scraper.scrape_brand_products()
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []

@st.cache_data
def load_cached_products():
    """Load products from cached JSON file"""
    try:
        with open('ferguson_products.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return fetch_ferguson_products()

def filter_products(products, category, price_range, brand, search_query):
    """Filter products based on user selections"""
    filtered = products.copy()
    
    # Apply category filter
    if category != "All Categories":
        filtered = [p for p in filtered if category.lower() in p['category'].lower()]
    
    # Apply price filter
    filtered = [p for p in filtered if p['price'] and price_range[0] <= p['price'] <= price_range[1]]
    
    # Apply brand filter
    if brand != "All Brands":
        filtered = [p for p in filtered if brand.upper() == p['brand']]
    
    # Apply search filter
    if search_query:
        filtered = [p for p in filtered if search_query.lower() in p['name'].lower() or 
                   search_query.lower() in p['description'].lower()]
    
    return filtered

def main():
    # Header
    st.title("Chicago Bathroom Fixtures")
    st.subheader("Premium Kohler & TOTO Products")

    # Initialize session state for products
    if 'products' not in st.session_state:
        st.session_state.products = load_cached_products()

    # Sidebar filters
    with st.sidebar:
        st.header("Product Filters")
        
        # Brand filter
        brand = st.selectbox(
            "Select Brand",
            ["All Brands", "KOHLER", "TOTO"]
        )
        
        # Category filter
        all_categories = ["All Categories"] + sorted(list(set(
            [p['category'] for p in st.session_state.products if p['category']]
        )))
        category = st.selectbox("Choose Category", all_categories)
        
        # Price range
        all_prices = [p['price'] for p in st.session_state.products if p['price']]
        min_price = min(all_prices) if all_prices else 0
        max_price = max(all_prices) if all_prices else 5000
        price_range = st.slider(
            "Price Range ($)",
            min_price, max_price, (min_price, max_price)
        )
        
        # Refresh data button
        if st.button("↻ Refresh Products"):
            st.session_state.products = fetch_ferguson_products()
            st.rerun()

    # Search bar
    search = st.text_input("🔍 Search products...", 
                          placeholder="Search by name or description...")

    # Filter products
    filtered_products = filter_products(
        st.session_state.products,
        category,
        price_range,
        brand,
        search
    )

    # Display products in grid
    if not filtered_products:
        st.info("No products found matching your criteria.")
    else:
        st.write(f"Showing {len(filtered_products)} products")
        
        # Create columns for the grid
        cols = st.columns(3)
        
        # Display products in grid
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <img src="{product['image_url']}" class="product-image" 
                         onerror="this.src='https://via.placeholder.com/250x250?text=No+Image'">
                    <div class="product-brand">{product['brand']}</div>
                    <div class="product-title">{product['name']}</div>
                    <div class="category-badge">{product['category']}</div>
                    <div class="product-price">${product['price']:.2f}</div>
                    <div class="product-description">{product['description'][:150]}...</div>
                    <div class="product-specs">
                        <strong>Specifications:</strong><br>
                        {"<br>".join(f"• {k}: {v}" for k, v in product.get('specifications', {}).items())}
                    </div>
                    <a href="{product['product_url']}" target="_blank" class="view-button">
                        View on Ferguson
                    </a>
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("© 2024 Chicago Bathroom Fixtures | Authorized Dealer for Kohler & TOTO")
    st.markdown("Last updated: " + time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
