from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class VerifyCode(BaseModel):
    code: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr

class VerifyPhoneRequest(BaseModel):
    phone: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Product Schemas
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = "Uncategorized"
    color: Optional[str] = "Black"
    material: Optional[str] = "Cotton"
    size: Optional[str] = "M"
    stock: Optional[int] = 0
    rating: Optional[float] = 0.0
    reviews_count: Optional[int] = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    stock: Optional[int] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Cart Schemas
class CartItemBase(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int = 1
    image: Optional[str] = None
    size: Optional[str] = "M"

class CartItemCreate(CartItemBase):
    session_id: Optional[str] = "default_session"
    user_id: Optional[int] = None

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: int
    session_id: str
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[CartItemBase]

class Order(OrderBase):
    id: int
    user_id: Optional[int] = None
    total_amount: float
    status: str
    items: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response Schemas
class MessageResponse(BaseModel):
    message: str
    success: bool
    data: Optional[dict] = None
    # Add these to your existing schemas.py

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class VerifyEmailRequest(BaseModel):
    email: EmailStr

class VerifyPhoneRequest(BaseModel):
    phone: str

class VerifyCode(BaseModel):
    code: str