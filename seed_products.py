import requests
import json

API_URL = "http://localhost:8000/api"

def seed_products():
    products = [
        {
            "name": "Nike Air Max",
            "price": 79.99,
            "description": "Comfortable running shoes with air cushion",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400",
            "category": "shoes",
            "color": "Black",
            "material": "Plastic",
            "size": "9",
            "stock": 25,
            "rating": 4.7,
            "reviews_count": 128
        },
        {
            "name": "Adidas Running Shoes",
            "price": 69.99,
            "description": "Lightweight running shoes for daily exercise",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400",
            "category": "shoes",
            "color": "White",
            "material": "Plastic",
            "size": "10",
            "stock": 30,
            "rating": 4.5,
            "reviews_count": 95
        },
        {
            "name": "Nike Sport T-Shirt",
            "price": 24.99,
            "description": "Cotton sport t-shirt for gym and running",
            "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=400",
            "category": "Clothes",
            "color": "Black",
            "material": "Cotton",
            "size": "L",
            "stock": 50,
            "rating": 4.5,
            "reviews_count": 200
        },
        {
            "name": "Denim Jacket",
            "price": 89.99,
            "description": "Classic blue denim jacket for casual wear",
            "image": "https://images.unsplash.com/photo-1521223895411-9d86f4fce1d2?q=80&w=400",
            "category": "Clothes",
            "color": "Blue",
            "material": "Cotton",
            "size": "XL",
            "stock": 30,
            "rating": 4.6,
            "reviews_count": 150
        },
        {
            "name": "Gaming Keyboard Pro",
            "price": 129.99,
            "description": "Mechanical keyboard with RGB lighting",
            "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?q=80&w=400",
            "category": "Gaming",
            "color": "Black",
            "material": "Metal",
            "size": "One Size",
            "stock": 20,
            "rating": 4.8,
            "reviews_count": 300
        },
        {
            "name": "Wireless Earbuds",
            "price": 89.99,
            "description": "True wireless earbuds with charging case",
            "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?q=80&w=400",
            "category": "Audio",
            "color": "White",
            "material": "Plastic",
            "size": "One Size",
            "stock": 45,
            "rating": 4.4,
            "reviews_count": 234
        },
        {
            "name": "Sony WH-1000XM5",
            "price": 399.99,
            "description": "Premium noise cancelling headphones",
            "image": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?q=80&w=400",
            "category": "Audio",
            "color": "Silver",
            "material": "Leather",
            "size": "One Size",
            "stock": 20,
            "rating": 4.9,
            "reviews_count": 342
        },
        {
            "name": "Leather Wallet",
            "price": 49.99,
            "description": "Genuine leather wallet with multiple pockets",
            "image": "https://images.unsplash.com/photo-1627123424574-724758594e93?q=80&w=400",
            "category": "Accessories",
            "color": "Brown",
            "material": "Leather",
            "size": "One Size",
            "stock": 60,
            "rating": 4.5,
            "reviews_count": 123
        },
        {
            "name": "Gold Necklace",
            "price": 199.99,
            "description": "Elegant gold-plated necklace",
            "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?q=80&w=400",
            "category": "Accessories",
            "color": "Gold",
            "material": "Metal",
            "size": "One Size",
            "stock": 10,
            "rating": 4.8,
            "reviews_count": 56
        }
    ]
    
    print("=" * 50)
    print("Seeding products...")
    print("=" * 50)
    
    success_count = 0
    for product in products:
        try:
            response = requests.post(f"{API_URL}/products", json=product)
            if response.status_code == 201:
                print(f"✅ Added: {product['name']} (Size: {product['size']}) - ${product['price']}")
                success_count += 1
            else:
                print(f"❌ Failed: {product['name']}")
        except Exception as e:
            print(f"❌ Error: {product['name']} - {str(e)}")
    
    print("=" * 50)
    print(f"✅ Successfully added {success_count}/{len(products)} products!")
    print("=" * 50)

if __name__ == "__main__":
    seed_products()