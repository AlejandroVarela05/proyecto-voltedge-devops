"""
services/auth_service.py - VoltEdge

Servicio de autenticación que maneja:
- Generación y verificación de tokens JWT
- Hashing y verificación de contraseñas con Argon2
- Extracción de datos del token
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# ==================== CONFIGURACIÓN ====================

SECRET_KEY = "voltedge_secret_key_change_in_production_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token válido por 1 hora

# Contexto de Argon2 (mejor que bcrypt, sin límite de 72 bytes)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ==================== HASHING DE CONTRASEÑAS ====================

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando Argon2.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    # Truncar a 72 bytes por seguridad (aunque Argon2 no tiene este límite)
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado
        
    Returns:
        True si coincide, False en caso contrario
    """
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.verify(password_truncated, hashed_password)
    except Exception:
        return False


# ==================== TOKENS JWT ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT firmado.
    
    Args:
        data: Datos a incluir en el payload (típicamente {"sub": email})
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodifica un token JWT y extrae el email del usuario.
    
    Args:
        token: Token JWT
        
    Returns:
        Email del usuario si el token es válido, None si no lo es
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
        
        return email
    
    except JWTError:
        return None