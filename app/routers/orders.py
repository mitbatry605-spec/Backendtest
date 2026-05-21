# backend/app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db
import hashlib
import requests
import json
from datetime import datetime
import secrets

# ============= IMPORT AUTH =============
from app.auth_utils import get_current_user, get_current_user_optional
from app import models

router = APIRouter(prefix="/api/orders", tags=["orders"])

# ============= KHQR CONFIGURATION =============
KHQR_GATEWAY_URL = "https://khqr.cc/api/payment/request"
KHQR_PROFILE_ID = "Wwx7asWUubeQcTFexIyWHACCqLQO4i38"
KHQR_SECRET_KEY = "ySpLxTzmmdqovKmYjXPvsdGvoZDYhfTs"

def get_session_id(request: Request):
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        session_id = "default_session"
    return session_id

def generate_khqr_payment_url(transaction_id: str, amount: float, success_url: str, remark: str = "") -> str:
    amount_str = f"{amount:.2f}"
    raw_string = KHQR_SECRET_KEY + transaction_id + amount_str + success_url + remark
    payment_hash = hashlib.sha1(raw_string.encode('utf-8')).hexdigest()
    
    payment_url = (
        f"{KHQR_GATEWAY_URL}/{KHQR_PROFILE_ID}"
        f"?transaction_id={transaction_id}"
        f"&amount={amount_str}"
        f"&success_url={success_url}"
        f"&remark={remark}"
        f"&hash={payment_hash}"
    )
    return payment_url

# ============ CREATE ORDER ============
@router.post("/create", response_model=schemas.Order)
def create_order(
    request: Request,
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    session_id = get_session_id(request)
    
    # ✅ IMPORTANT: Get user_id from authenticated user
    user_id = None
    if current_user:
        user_id = current_user.id
        print(f"✅ Creating order for logged-in user: {current_user.email} (ID: {user_id})")
    else:
        print(f"⚠️ Creating order for guest user with session: {session_id}")
    
    print(f"📦 Creating order for session: {session_id}")
    print(f"   Customer: {order.customer_name}, Email: {order.customer_email}")
    
    # Pass user_id to crud function
    result = crud.create_order(db, order, session_id, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    return result

# ============ GET MY ORDERS (for logged-in user) ============
@router.get("/my-orders")
def get_my_orders(
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all orders for the currently logged-in user"""
    print(f"📋 Fetching orders for user: {current_user.email} (ID: {current_user.id})")
    
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()
    
    print(f"   Found {len(orders)} orders")
    
    # Convert items from JSON string to list for each order
    for order in orders:
        if order.items and isinstance(order.items, str):
            order.items = json.loads(order.items)
    
    return orders

# ============ GET ORDER BY ID (with user check) ============
@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get order by ID - only if user owns it or is admin"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Convert items from JSON string to list
    if order.items and isinstance(order.items, str):
        order.items = json.loads(order.items)
    
    # Check if user is authorized to view this order
    if current_user and hasattr(current_user, 'role') and current_user.role == "admin":
        return order
    
    if current_user and order.user_id == current_user.id:
        return order
    
    if not current_user and order.user_id is None:
        return order
    
    raise HTTPException(status_code=403, detail="Not authorized to view this order")

# ============ GET ALL ORDERS (Admin only) ============
@router.get("/", response_model=List[schemas.Order])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders - Admin only"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud.get_orders(db, skip=skip, limit=limit)

# ============ UPDATE ORDER STATUS ============
@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status - Admin only"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    db.refresh(order)
    
    return {"message": "Order status updated", "status": status}

# ============ CREATE KHQR PAYMENT FOR ORDER ============
@router.post("/{order_id}/khqr-payment")
async def create_khqr_payment(
    order_id: int,
    request: Request,
    current_user: models.User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if current_user and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    timestamp = int(datetime.now().timestamp())
    transaction_id = f"ORD_{order_id}_{timestamp}"
    success_url = "http://localhost:3000/payment-return"
    remark = f"Order_{order_id}"
    amount = round(order.total_amount, 2)
    
    payment_url = generate_khqr_payment_url(
        transaction_id=transaction_id,
        amount=amount,
        success_url=success_url,
        remark=remark
    )
    
    # Save transaction_id to order
    order.transaction_id = transaction_id
    db.commit()
    
    return {
        "payment_url": payment_url,
        "order_id": order_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": "USD"
    }

# ============ VERIFY PAYMENT ============
@router.post("/verify-payment")
async def verify_payment(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        body = await request.json()
        transaction_id = body.get("transaction_id")
        success_hash = body.get("success_hash")
        success_amount = body.get("success_amount")
        
        if not transaction_id:
            return {"verified": False, "message": "No transaction_id"}
        
        if success_hash and success_amount:
            expected_hash = hashlib.sha1(
                (KHQR_SECRET_KEY + transaction_id + str(success_amount) + "SUCCESS").encode('utf-8')
            ).hexdigest()
            
            if expected_hash == success_hash:
                try:
                    parts = transaction_id.split('_')
                    if len(parts) >= 2:
                        order_id = int(parts[1])
                        order = db.query(models.Order).filter(models.Order.id == order_id).first()
                        if order:
                            order.status = "paid"
                            db.commit()
                            return {
                                "verified": True,
                                "status": "paid",
                                "amount": success_amount,
                                "order_id": order.id,
                                "transaction_id": transaction_id
                            }
                except Exception as e:
                    print(f"Error parsing order_id: {e}")
        
        return {"verified": False, "status": "pending", "message": "Payment not verified"}
        
    except Exception as e:
        print(f"❌ Verify payment error: {e}")
        return {"verified": False, "message": str(e)}

# ============ WEBHOOK FOR KHQR CALLBACK ============
@router.post("/webhook")
async def khqr_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        body = await request.json()
        print(f"📨 Webhook received: {json.dumps(body, indent=2)}")
        
        transaction_id = body.get("transaction_id")
        amount = body.get("amount")
        status = body.get("status")
        received_hash = body.get("hash")
        
        if not transaction_id:
            return {"status": "error", "message": "No transaction_id"}
        
        expected_hash = hashlib.sha1(
            (KHQR_SECRET_KEY + transaction_id + str(amount) + status).encode('utf-8')
        ).hexdigest()
        
        if received_hash != expected_hash:
            print(f"❌ Invalid webhook hash")
            return {"status": "error", "message": "Invalid hash"}
        
        try:
            parts = transaction_id.split('_')
            if len(parts) >= 2:
                order_id = int(parts[1])
                order = crud.get_order(db, order_id)
                
                if order:
                    if status == "SUCCESS" or status == "success":
                        order.status = "paid"
                        db.commit()
                        print(f"✅ Order #{order.id} marked as PAID via webhook")
                        return {"status": "success", "message": "Order updated"}
                    else:
                        print(f"⚠️ Payment status: {status}")
                        return {"status": "pending", "message": f"Status: {status}"}
        except Exception as e:
            print(f"Error: {e}")
        
        return {"status": "error", "message": "Order not found"}
            
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}

# ============ GET ORDERS BY USER ID ============
@router.get("/user/{user_id}")
def get_orders_by_user(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get orders by user ID - Admin only or own user"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    orders = db.query(models.Order).filter(
        models.Order.user_id == user_id
    ).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert items from JSON string to list
    for order in orders:
        if order.items and isinstance(order.items, str):
            order.items = json.loads(order.items)
    
    return orders

# ============ CANCEL ORDER ============
@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot cancel order that is already processed")
    
    order.status = "cancelled"
    db.commit()
    
    return {"message": "Order cancelled successfully", "order_id": order_id}