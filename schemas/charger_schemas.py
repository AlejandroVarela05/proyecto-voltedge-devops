"""
schemas/charger_schemas.py - VoltEdge

Esquemas Pydantic para cargadores.
"""

from pydantic import BaseModel, Field


# ==================== SCHEMAS DE CARGADOR ====================

class ChargerCreate(BaseModel):
    """Schema para crear un cargador"""
    charger_id: int = Field(..., gt=0, description="ID único del cargador")
    charger_type: str = Field(..., description="Tipo: 'rápido' o 'normal'")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "charger_id": 101,
                    "charger_type": "rápido"
                }
            ]
        }
    }


class ChargerRead(BaseModel):
    """Schema para leer un cargador"""
    id: int = Field(..., description="ID del cargador")
    type: str = Field(..., description="Tipo de cargador")
    status: str = Field(..., description="Estado: disponible/ocupado/mantenimiento")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 101,
                    "type": "rápido",
                    "status": "disponible"
                }
            ]
        }
    }


class IniciarCargaRequest(BaseModel):
    """Schema para iniciar sesión de carga"""
    user_id: str = Field(..., description="ID del usuario (UUID)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }