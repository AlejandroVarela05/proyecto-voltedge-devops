"""
schemas/station_schemas.py - VoltEdge

Esquemas Pydantic para estaciones de carga.
"""

from pydantic import BaseModel, Field
from typing import List


# ==================== SCHEMAS DE ESTACIÓN ====================

class StationCreate(BaseModel):
    """Schema para crear una estación"""
    id: int = Field(..., gt=0, description="ID único de la estación")
    name: str = Field(..., min_length=1, description="Nombre de la estación")
    location: str = Field(..., min_length=1, description="Ubicación de la estación")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Estación Centro Vigo",
                    "location": "Calle Príncipe 25, Vigo"
                }
            ]
        }
    }


class ChargerInfo(BaseModel):
    """Schema para información de cargador dentro de estación"""
    id: int = Field(..., description="ID del cargador")
    type: str = Field(..., description="Tipo de cargador")
    status: str = Field(..., description="Estado del cargador")


class StationRead(BaseModel):
    """Schema para leer una estación"""
    id: int = Field(..., description="ID de la estación")
    name: str = Field(..., description="Nombre de la estación")
    location: str = Field(..., description="Ubicación")
    total_chargers: int = Field(..., description="Total de cargadores")
    disponibles: int = Field(..., description="Cargadores disponibles")
    chargers: List[ChargerInfo] = Field(default=[], description="Lista de cargadores")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Estación Centro Vigo",
                    "location": "Calle Príncipe 25, Vigo",
                    "total_chargers": 4,
                    "disponibles": 2,
                    "chargers": [
                        {"id": 101, "type": "rápido", "status": "disponible"},
                        {"id": 102, "type": "normal", "status": "ocupado"}
                    ]
                }
            ]
        }
    }


class StationDisponibilidad(BaseModel):
    """Schema para disponibilidad de una estación"""
    station_id: int = Field(..., description="ID de la estación")
    station_name: str = Field(..., description="Nombre de la estación")
    total_chargers: int = Field(..., description="Total de cargadores")
    disponibles: int = Field(..., description="Cargadores disponibles")
    ocupados: int = Field(..., description="Cargadores ocupados")
    porcentaje_disponibilidad: float = Field(..., description="% de disponibilidad")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "station_id": 1,
                    "station_name": "Estación Centro Vigo",
                    "total_chargers": 4,
                    "disponibles": 2,
                    "ocupados": 2,
                    "porcentaje_disponibilidad": 50.0
                }
            ]
        }
    }


class StationConsumo(BaseModel):
    """Schema para reporte de consumo de una estación"""
    station_id: int = Field(..., description="ID de la estación")
    station_name: str = Field(..., description="Nombre de la estación")
    total_sesiones: int = Field(..., description="Total de sesiones")
    sesiones_activas: int = Field(..., description="Sesiones activas ahora")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "station_id": 1,
                    "station_name": "Estación Centro Vigo",
                    "total_sesiones": 156,
                    "sesiones_activas": 2
                }
            ]
        }
    }