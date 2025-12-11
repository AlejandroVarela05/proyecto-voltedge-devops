"""
schemas/session_schemas.py - VoltEdge

Esquemas Pydantic para sesiones de carga.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ==================== SCHEMAS DE SESIÓN ====================

class SessionCreate(BaseModel):
    """Schema para crear una sesión de carga"""
    user_id: UUID = Field(..., description="ID del usuario")
    station_id: int = Field(..., gt=0, description="ID de la estación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "station_id": 1
                }
            ]
        }
    }


class SessionRead(BaseModel):
    """Schema para leer una sesión"""
    user_id: UUID = Field(..., description="ID del usuario")
    user_name: str = Field(..., description="Nombre del usuario")
    charger_id: int = Field(..., description="ID del cargador usado")
    start_time: str = Field(..., description="Hora de inicio")
    end_time: Optional[str] = Field(None, description="Hora de fin (si terminó)")
    duration_minutes: int = Field(..., description="Duración en minutos")
    kwh_consumidos: float = Field(..., description="kWh consumidos")
    coste: float = Field(..., description="Coste total en €")
    activa: bool = Field(..., description="Sesión activa o finalizada")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_name": "María López",
                    "charger_id": 101,
                    "start_time": "2024-12-11 10:30:00",
                    "end_time": "2024-12-11 11:15:00",
                    "duration_minutes": 45,
                    "kwh_consumidos": 22.5,
                    "coste": 6.75,
                    "activa": False
                }
            ]
        }
    }


class CerrarSessionRequest(BaseModel):
    """Schema para cerrar una sesión"""
    user_id: UUID = Field(..., description="ID del usuario")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }