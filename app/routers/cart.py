# backend/app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.auth_utils import get_current_user_optional
from app import models

router = APIRouter(prefix="/api/cart", tags=["cart"])

def get_session_id(request: Request):
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        session_id = "default_session"
    return session_id


@router.get("/", response_model=List[schemas.CartItem])
def get_cart(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Get all items in cart"""
    session_id = get_session_id(request)
    user_id = current_user.id if current_user else None
    
    print(f"\n{'='*60}")
    print(f"🛒 GET /cart")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print(f"{'='*60}")
    
    items = crud.get_cart_items(db, session_id, user_id)
    
    # Print detailed info for each item
    if items:
        print(f"📦 Found {len(items)} items in cart:")
        for idx, item in enumerate(items, 1):
            print(f"   {idx}. Product: {item.name}")
            print(f"      Quantity: {item.quantity}")
            print(f"      Price: ${item.price}")
            print(f"      User ID: {item.user_id}")
            print(f"      Session ID: {item.session_id}")
    else:
        print("📦 Cart is empty")
    
    print(f"{'='*60}\n")
    return items


@router.post("/add", response_model=schemas.CartItem)
def add_to_cart(
    request: Request,
    cart_item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Add item to cart"""
    session_id = get_session_id(request)
    user_id = current_user.id if current_user else None
    
    print(f"\n{'='*60}")
    print(f"🛒 POST /cart/add")
    print(f"   Product: {cart_item.name}")
    print(f"   Quantity: {cart_item.quantity}")
    print(f"   Price: ${cart_item.price}")
    print(f"   Size: {cart_item.size}")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print(f"{'='*60}")
    
    cart_item.session_id = session_id
    cart_item.user_id = user_id
    
    result = crud.add_to_cart(db, cart_item)
    if not result:
        print("❌ Failed to add to cart")
        raise HTTPException(status_code=404, detail="Could not add to cart")
    
    print(f"✅ Successfully added to cart - New quantity: {result.quantity}")
    print(f"{'='*60}\n")
    
    return result


@router.put("/{cart_item_id}", response_model=schemas.CartItem)
def update_cart_item(
    cart_item_id: int,
    update_data: schemas.CartItemUpdate,
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    print(f"\n{'='*60}")
    print(f"🛒 PUT /cart/{cart_item_id}")
    print(f"   New Quantity: {update_data.quantity}")
    print(f"{'='*60}")
    
    result = crud.update_cart_item(db, cart_item_id, update_data.quantity)
    if result is None:
        print(f"❌ Cart item {cart_item_id} not found")
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    print(f"✅ Cart item updated - New quantity: {result.quantity}")
    print(f"{'='*60}\n")
    return result


@router.delete("/{cart_item_id}", response_model=schemas.MessageResponse)
def remove_from_cart(
    cart_item_id: int, 
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    print(f"\n{'='*60}")
    print(f"🛒 DELETE /cart/{cart_item_id}")
    print(f"{'='*60}")
    
    success = crud.remove_from_cart(db, cart_item_id)
    if not success:
        print(f"❌ Cart item {cart_item_id} not found")
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    print(f"✅ Cart item removed successfully")
    print(f"{'='*60}\n")
    return {"message": "Item removed from cart", "success": True}


@router.delete("/clear/all", response_model=schemas.MessageResponse)
def clear_cart(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    """Clear all items from cart"""
    session_id = get_session_id(request)
    user_id = current_user.id if current_user else None
    
    print(f"\n{'='*60}")
    print(f"🛒 DELETE /cart/clear/all")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print(f"{'='*60}")
    
    crud.clear_cart(db, session_id, user_id)
    print(f"✅ Cart cleared successfully")
    print(f"{'='*60}\n")
    return {"message": "Cart cleared successfully", "success": True}