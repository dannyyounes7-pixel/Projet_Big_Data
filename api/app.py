"""
FastAPI Application - IAR Platform API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import yaml

from api.auth import authenticate_user, create_access_token, get_current_user
from api.schemas import LoginRequest, TokenResponse
from api.routes import communes, departements, stats


# Load API configuration
with open('config/api.yaml', 'r') as f:
    config = yaml.safe_load(f)

docs_config = config.get('docs', {})

# Create FastAPI app
app = FastAPI(
    title=docs_config.get('title', 'IAR Platform API'),
    description=docs_config.get('description', 'API pour consulter l\'Indice d\'Attractivité Rationnelle'),
    version=docs_config.get('version', '1.0.0'),
    contact=docs_config.get('contact', {})
)

# CORS middleware
cors_config = config.get('cors', {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get('allow_origins', ["*"]),
    allow_credentials=cors_config.get('allow_credentials', True),
    allow_methods=cors_config.get('allow_methods', ["*"]),
    allow_headers=cors_config.get('allow_headers', ["*"]),
)


# Authentication endpoint
@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(login_request: LoginRequest):
    """
    Authenticate user and return JWT token
    
    Use the token in subsequent requests with header:
    Authorization: Bearer <token>
    """
    user = authenticate_user(login_request.username, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    jwt_config = config['jwt']
    access_token_expires = timedelta(minutes=jwt_config['access_token_expire_minutes'])
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IAR Platform API",
        "version": "1.0.0"
    }


# Protected test endpoint
@app.get("/me", tags=["Authentication"])
def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    return current_user


# Include routers
app.include_router(communes.router)
app.include_router(departements.router)
app.include_router(stats.router)


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """API root endpoint"""
    return {
        "message": "Bienvenue sur l'API IAR Platform",
        "documentation": "/docs",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth/login",
            "communes": "/communes",
            "departements": "/departements",
            "statistics": "/stats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    server_config = config.get('server', {})
    uvicorn.run(
        "api.app:app",
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8000),
        reload=server_config.get('reload', True)
    )
