from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models, schemas
from app.database import get_db
from app.email_service import generate_verification_code, send_verification_email
from app.auth_utils import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ============ REGISTER NEW USER ============
@router.post("/register", response_model=schemas.MessageResponse)
def register(
    user_data: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    - Sends verification code to email
    """
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_email:
        if not existing_email.is_email_verified:
            db.delete(existing_email)
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if phone already exists (if provided)
    if user_data.phone:
        existing_phone = db.query(models.User).filter(models.User.phone == user_data.phone).first()
        if existing_phone:
            if not existing_phone.is_email_verified:
                db.delete(existing_phone)
                db.commit()
            else:
                raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Generate verification code
    email_code = generate_verification_code()
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    db_user = models.User(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        password_hash=hashed_password,
        is_active=False,
        is_email_verified=False,
        is_phone_verified=True,
        email_verification_code=email_code,
        email_verification_expires=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    background_tasks.add_task(send_verification_email, user_data.email, email_code)
    
    print(f"\n{'='*60}")
    print(f"✅ User registered: {user_data.email}")
    print(f"📧 Verification code sent to: {user_data.email}")
    print(f"🔐 Code: {email_code}")
    print(f"{'='*60}\n")
    
    return schemas.MessageResponse(
        message=f"Registration successful! Verification code sent to {user_data.email}",
        success=True,
        data={"email": user_data.email, "requires_verification": True}
    )


# ============ VERIFY EMAIL ============
@router.post("/verify-email", response_model=schemas.LoginResponse)
def verify_email(
    email: str = Query(..., description="User email address"),
    code: str = Query(..., description="6-digit verification code"),
    db: Session = Depends(get_db)
):
    """Verify user's email with 6-digit code"""
    
    print(f"🔍 Verifying email: {email}, code: {code}")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    if user.email_verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    if user.email_verification_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification code has expired")
    
    user.is_email_verified = True
    user.is_active = True
    user.email_verification_code = None
    user.email_verification_expires = None
    
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    
    print(f"✅ Email verified: {user.email}")
    
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )


# ============ RESEND EMAIL VERIFICATION CODE ============
@router.post("/resend-email-code", response_model=schemas.MessageResponse)
def resend_email_code(
    email: str = Query(..., description="User email address"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Resend verification code to user's email"""
    
    print(f"📧 Resending code to: {email}")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    new_code = generate_verification_code()
    user.email_verification_code = new_code
    user.email_verification_expires = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    background_tasks.add_task(send_verification_email, user.email, new_code)
    
    print(f"📧 Resent code to: {user.email} -> {new_code}")
    
    return schemas.MessageResponse(
        message=f"New verification code sent to {user.email}",
        success=True
    )


# ============ LOGIN ============
@router.post("/login", response_model=schemas.LoginResponse)
def login(
    login_data: schemas.UserLogin, 
    db: Session = Depends(get_db)
):
    """Login user with email or phone"""
    
    user = None
    if login_data.email:
        user = db.query(models.User).filter(models.User.email == login_data.email).first()
    elif login_data.phone:
        user = db.query(models.User).filter(models.User.phone == login_data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
        )
    
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email before logging in",
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    print(f"🔑 User logged in: {user.email}")
    
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )


# ============ GET CURRENT USER INFO ============
@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


# ============ UPDATE USER PROFILE ============
@router.put("/me", response_model=schemas.UserResponse)
def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information"""
    
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    
    if user_update.phone:
        existing = db.query(models.User).filter(
            models.User.phone == user_update.phone,
            models.User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already in use")
        current_user.phone = user_update.phone
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ============ CHANGE PASSWORD ============
@router.post("/change-password", response_model=schemas.MessageResponse)
def change_password(
    old_password: str,
    new_password: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's password"""
    
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return schemas.MessageResponse(
        message="Password changed successfully",
        success=True
    )


# ============ DELETE ACCOUNT ============
@router.delete("/me", response_model=schemas.MessageResponse)
def delete_account(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account"""
    
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.query(models.Order).filter(models.Order.user_id == current_user.id).delete()
    db.delete(current_user)
    db.commit()
    
    return schemas.MessageResponse(
        message="Account deleted successfully",
        success=True
    )