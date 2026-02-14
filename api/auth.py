"""
JWT Authentication Module
"""
from datetime import datetime, timedelta
from typing import Optional
import yaml
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()


def load_api_config():
    """Load API configuration"""
    with open('config/api.yaml', 'r') as f:
        return yaml.safe_load(f)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    config = load_api_config()
    jwt_config = config['jwt']
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=jwt_config['access_token_expire_minutes'])
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        jwt_config['secret_key'],
        algorithm=jwt_config['algorithm']
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    config = load_api_config()
    jwt_config = config['jwt']
    
    try:
        payload = jwt.decode(
            token,
            jwt_config['secret_key'],
            algorithms=[jwt_config['algorithm']]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate user with username and password
    
    Args:
        username: Username
        password: Plain password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    config = load_api_config()
    users = config.get('users', [])
    
    for user in users:
        if user['username'] == username:
            # In production, passwords should be hashed
            # For demo, we're comparing plain passwords
            if user['password'] == password:
                return {
                    "username": user['username'],
                    "email": user.get('email', '')
                }
    
    return None
