from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import User, AuthToken
from schemas import UserResponse, UserCreate, UserUpdate, UserLogin, TokenResponse
from typing import List
from passlib.context import CryptContext
import secrets

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Verify token and return current user"""
    token = credentials.credentials
    
    auth_token = db.query(AuthToken).filter(AuthToken.token == token).first()
    if not auth_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == auth_token.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    return user

items = {
    1: "car",
    2: "bike",
    3: "boat",
    4: "plane"
}


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello Worlds"}


# ============================================================================
# ITEMS ENDPOINTS
# ============================================================================

@app.get("/items/{item_id}", tags=["Items"])
async def read_item(item_id: int):
    item_name = items.get(item_id, "Item not found")
    return {"item_id": item_id, "item_name": item_name}


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (no authentication required)"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=pwd_context.hash(user.password),
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get authentication token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    # Check if user already has a token
    existing_token = db.query(AuthToken).filter(AuthToken.user_id == user.id).first()
    
    if existing_token:
        # Return existing token
        return {
            "token": existing_token.token,
            "user_id": user.id,
            "message": "Login successful (existing token)"
        }
    
    # Generate a new secure random token
    token = secrets.token_urlsafe(32)
    
    # Save token to database
    auth_token = AuthToken(user_id=user.id, token=token)
    db.add(auth_token)
    db.commit()
    
    return {
        "token": token,
        "user_id": user.id,
        "message": "Login successful (new token created)"
    }


@app.post("/auth/logout", tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout and invalidate all tokens for current user"""
    # Delete all tokens for this user
    db.query(AuthToken).filter(AuthToken.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Logout successful - all tokens invalidated"}


# ============================================================================
# USER ENDPOINTS - CRUD OPERATIONS (Protected)
# ============================================================================

@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
async def create_user(
    user: UserCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user (requires authentication)"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=pwd_context.hash(user.password),
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
async def read_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (requires authentication)"""
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (requires authentication)"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user - only updates fields that are different (requires authentication)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump(exclude_unset=True)
    fields_to_update = {}
    
    # Handle email update with validation
    if "email" in update_data:
        if update_data["email"] != db_user.email:
            # Email is different - check if new email already exists
            existing_user = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            # New email is unique - add to update list
            fields_to_update["email"] = update_data["email"]
        # If email is the same, don't add it to update list
    
    # Handle password update with hashing
    if "password" in update_data:
        # Always update password if provided (can't compare hashed values)
        fields_to_update["hashed_password"] = pwd_context.hash(update_data["password"])
    
    # Check other fields and only update if different
    for field in ["first_name", "middle_name", "last_name", "is_active"]:
        if field in update_data:
            current_value = getattr(db_user, field)
            new_value = update_data[field]
            if current_value != new_value:
                # Value is different - add to update list
                fields_to_update[field] = new_value
    
    # Only commit if there are actual changes
    if fields_to_update:
        for field, value in fields_to_update.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        # No changes detected
        return db_user


@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user (requires authentication)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully", "user_id": user_id}


# ============================================================================
# DATABASE TESTING
# ============================================================================

@app.get("/test-db", tags=["Database"])
async def test_database():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            connection.commit()
        return {
            "status": "success",
            "message": "Database connection successful!",
            "database": "fastapisample"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
