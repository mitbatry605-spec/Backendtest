import requests
import json

API_URL = "http://localhost:8000/api"

def add_product():
    product_data = {
        "name": "Nike Air Max Shoes",
        "price": 79.99,
        "description": "Comfortable running shoes with air cushion technology",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400",
        "category": "shoes",
        "color": "Black",
        "material": "Plastic",
        "size": "9",
        "stock": 25,
        "rating": 4.7,
        "reviews_count": 128
    }
    
    try:
        response = requests.post(f"{API_URL}/products", json=product_data)
        if response.status_code == 201:
            print("✅ Product added successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    add_product()