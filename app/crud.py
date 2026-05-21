# backend/app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas
import json

# ============ PRODUCT CRUD ============
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None, color: str = None, material: str = None, size: str = None):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    if color:
        query = query.filter(models.Product.color == color)
    if material:
        query = query.filter(models.Product.material == material)
    if size:
        query = query.filter(models.Product.size == size)
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    db.delete(db_product)
    db.commit()
    return True


# ============ CART CRUD ============
def get_cart_items(db: Session, session_id: str = None, user_id: int = None):
    print(f"🔍 get_cart_items() called")
    print(f"   session_id: {session_id}")
    print(f"   user_id: {user_id}")
    
    query = db.query(models.CartItem)
    
    if user_id:
        items = query.filter(models.CartItem.user_id == user_id).all()
        print(f"   Found {len(items)} items for user_id {user_id}")
        
        if not items and session_id:
            session_items = query.filter(models.CartItem.session_id == session_id).all()
            if session_items:
                print(f"   🚚 Migrating {len(session_items)} items from session to user")
                for item in session_items:
                    item.user_id = user_id
                    item.session_id = None
                db.commit()
                return query.filter(models.CartItem.user_id == user_id).all()
        return items
    elif session_id:
        items = query.filter(models.CartItem.session_id == session_id).all()
        print(f"   Found {len(items)} items for session_id {session_id}")
        return items
    
    return []

def add_to_cart(db: Session, cart_item: schemas.CartItemCreate):
    print(f"🔍 add_to_cart() called")
    print(f"   Product ID: {cart_item.product_id}")
    print(f"   User ID: {cart_item.user_id}")
    print(f"   Session ID: {cart_item.session_id}")
    print(f"   Name: {cart_item.name}")
    print(f"   Price: {cart_item.price}")
    print(f"   Quantity: {cart_item.quantity}")
    
    query = db.query(models.CartItem).filter(
        models.CartItem.product_id == cart_item.product_id
    )
    
    if cart_item.user_id:
        query = query.filter(models.CartItem.user_id == cart_item.user_id)
        print(f"   Looking for existing item with user_id: {cart_item.user_id}")
    else:
        query = query.filter(models.CartItem.session_id == cart_item.session_id)
        print(f"   Looking for existing item with session_id: {cart_item.session_id}")
    
    existing = query.first()
    
    if existing:
        old_qty = existing.quantity
        existing.quantity += cart_item.quantity
        print(f"   ✅ FOUND! Updating quantity from {old_qty} to {existing.quantity}")
        db.commit()
        db.refresh(existing)
        return existing
    
    print(f"   ❌ NOT FOUND - Creating new cart item")
    db_cart_item = models.CartItem(**cart_item.model_dump())
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    print(f"   ✅ Created new cart item with ID: {db_cart_item.id}")
    return db_cart_item


def update_cart_item(db: Session, cart_item_id: int, quantity: int):
    print(f"🔍 update_cart_item() called - ID: {cart_item_id}, New Qty: {quantity}")
    
    db_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if not db_item:
        print(f"   ❌ Cart item {cart_item_id} not found")
        return None
    
    if quantity <= 0:
        print(f"   🗑️ Quantity <= 0, deleting item")
        db.delete(db_item)
        db.commit()
        return None
    
    old_qty = db_item.quantity
    db_item.quantity = quantity
    print(f"   ✅ Quantity updated - Old: {old_qty}, New: {quantity}")
    db.commit()
    db.refresh(db_item)
    return db_item


def remove_from_cart(db: Session, cart_item_id: int):
    print(f"🔍 remove_from_cart() called - ID: {cart_item_id}")
    
    db_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if not db_item:
        print(f"   ❌ Cart item {cart_item_id} not found")
        return False
    
    print(f"   🗑️ Removing item: {db_item.name}")
    db.delete(db_item)
    db.commit()
    print(f"   ✅ Item removed successfully")
    return True


def clear_cart(db: Session, session_id: str = None, user_id: int = None):
    print(f"🔍 clear_cart() called")
    print(f"   session_id: {session_id}")
    print(f"   user_id: {user_id}")
    
    items = get_cart_items(db, session_id, user_id)
    print(f"   Found {len(items)} items to delete")
    
    for item in items:
        print(f"   🗑️ Deleting: {item.name} (Qty: {item.quantity})")
        db.delete(item)
    
    db.commit()
    print(f"   ✅ Cart cleared successfully")
    return True


# ============ ORDER CRUD ============
def create_order(db: Session, order: schemas.OrderCreate, session_id: str = None, user_id: int = None):
    print(f"\n{'='*50}")
    print(f"📦 Creating order - Session ID: {session_id}, User ID: {user_id}")
    
    cart_items = get_cart_items(db, session_id, user_id)
    
    print(f"📦 Found {len(cart_items)} items in cart")
    for item in cart_items:
        print(f"   - {item.name}: {item.quantity} x ${item.price}")
    
    if not cart_items:
        print("❌ Cart is empty!")
        return None
    
    total = sum(item.price * item.quantity for item in cart_items)
    
    items_json = json.dumps([{
        "id": item.product_id, 
        "name": item.name, 
        "price": item.price, 
        "quantity": item.quantity, 
        "size": item.size
    } for item in cart_items])
    
    # ✅ IMPORTANT: Save user_id if provided (logged-in user)
    db_order = models.Order(
        user_id=user_id if user_id else None,  # This links order to user
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        total_amount=total,
        items=items_json,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    print(f"✅ Order created successfully!")
    print(f"   Order ID: {db_order.id}")
    print(f"   User ID: {db_order.user_id}")
    print(f"   Total: ${total}")
    print(f"{'='*50}\n")
    
    # Clear cart after order
    clear_cart(db, session_id, user_id)
    
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    query = db.query(models.Order)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int, user_id: int = None):
    query = db.query(models.Order).filter(models.Order.id == order_id)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.first()

def update_order_status(db: Session, order_id: int, status: str):
    order = get_order(db, order_id)
    if not order:
        return None
    order.status = status
    db.commit()
    db.refresh(order)
    return order