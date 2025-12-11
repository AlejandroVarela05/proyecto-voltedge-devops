"""
schemas/user_schemas.py - VoltEdge

Esquemas Pydantic para gestión de usuarios.
"""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


# ==================== SCHEMAS DE USUARIO ====================

class UserRead(BaseModel):
    """Schema para leer un usuario"""
    id: UUID = Field(..., description="ID único del usuario")
    name: str = Field(..., description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    user_type: str = Field(..., description="Tipo: individual, empresa o admin")
    saldo: float = Field(..., description="Saldo disponible en €")
    tarifa_kwh: float = Field(..., description="Tarifa aplicada en €/kWh")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "María López",
                    "email": "maria@voltedge.com",
                    "user_type": "individual",
                    "saldo": 85.50,
                    "tarifa_kwh": 0.30
                }
            ]
        }
    }


class RecargaSaldo(BaseModel):
    """Schema para recargar saldo"""
    cantidad: float = Field(..., gt=0, description="Cantidad a recargar en €")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cantidad": 50.0
                }
            ]
        }
    }


class RecargaSaldoResponse(BaseModel):
    """Schema de respuesta tras recargar saldo"""
    user_id: UUID = Field(..., description="ID del usuario")
    saldo_anterior: float = Field(..., description="Saldo antes de la recarga")
    cantidad_recargada: float = Field(..., description="Cantidad recargada")
    saldo_nuevo: float = Field(..., description="Saldo después de la recarga")
    mensaje: str = Field(..., description="Mensaje de confirmación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "saldo_anterior": 35.50,
                    "cantidad_recargada": 50.0,
                    "saldo_nuevo": 85.50,
                    "mensaje": "Saldo recargado exitosamente"
                }
            ]
        }
    }