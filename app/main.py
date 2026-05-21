import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import products, cart, orders, auth

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce API",
    version="1.0.0",
    description="E-Commerce Backend API for E.Shop"
)

# CORS configuration for production and development
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://*.onrender.com",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(auth.router)

@app.get("/")
def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Welcome to E-Commerce API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for Render
    """
    return {"status": "healthy"}

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)