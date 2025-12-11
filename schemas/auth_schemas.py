"""
schemas/auth_schemas.py - VoltEdge

Esquemas Pydantic para autenticación y autorización.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


# ==================== SCHEMAS DE REGISTRO ====================

class UsuarioRegistro(BaseModel):
    """Schema para registrar un nuevo usuario"""
    name: str = Field(..., min_length=1, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    user_type: str = Field(default="individual", description="Tipo: 'individual', 'empresa' o 'admin'")
    saldo_inicial: float = Field(default=50.0, ge=0, description="Saldo inicial en €")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "María López",
                    "email": "maria@voltedge.com",
                    "password": "password123",
                    "user_type": "individual",
                    "saldo_inicial": 100.0
                }
            ]
        }
    }


class UsuarioRegistroResponse(BaseModel):
    """Schema de respuesta tras registrar un usuario"""
    id: UUID = Field(..., description="ID único del usuario")
    name: str = Field(..., description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    user_type: str = Field(..., description="Tipo de usuario")
    saldo: float = Field(..., description="Saldo actual en €")
    mensaje: str = Field(..., description="Mensaje de confirmación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "María López",
                    "email": "maria@voltedge.com",
                    "user_type": "individual",
                    "saldo": 100.0,
                    "mensaje": "Usuario registrado exitosamente"
                }
            ]
        }
    }


# ==================== SCHEMAS DE TOKEN ====================

class Token(BaseModel):
    """Schema para devolver el token JWT tras login"""
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    }


class TokenData(BaseModel):
    """Schema para datos extraídos del token"""
    email: Optional[str] = None


# ==================== SCHEMAS DE USUARIO AUTENTICADO ====================

class UsuarioAutenticado(BaseModel):
    """Schema del usuario autenticado actual"""
    id: UUID = Field(..., description="ID del usuario")
    name: str = Field(..., description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    user_type: str = Field(..., description="Tipo de usuario")
    saldo: float = Field(..., description="Saldo actual en €")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "María López",
                    "email": "maria@voltedge.com",
                    "user_type": "individual",
                    "saldo": 85.50
                }
            ]
        }
    }