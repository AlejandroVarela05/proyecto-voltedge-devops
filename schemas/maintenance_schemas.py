"""
schemas/maintenance_schemas.py - VoltEdge

Esquemas Pydantic para mantenimientos.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ==================== SCHEMAS DE MANTENIMIENTO ====================

class MaintenanceCreate(BaseModel):
    """Schema para crear un mantenimiento"""
    id_mantenimiento: int = Field(..., gt=0, description="ID único del mantenimiento")
    station_id: int = Field(..., gt=0, description="ID de la estación")
    fecha: str = Field(..., description="Fecha del mantenimiento (YYYY-MM-DD)")
    tecnico: str = Field(..., min_length=1, description="Nombre del técnico")
    tipo: str = Field(..., description="Tipo: 'preventivo' o 'correctivo'")
    frecuencia: Optional[str] = Field(None, description="Frecuencia (solo preventivo)")
    descripcion_fallo: Optional[str] = Field(None, description="Descripción del fallo (solo correctivo)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_mantenimiento": 5001,
                    "station_id": 1,
                    "fecha": "2024-12-20",
                    "tecnico": "Técnico Ana",
                    "tipo": "preventivo",
                    "frecuencia": "mensual"
                }
            ]
        }
    }


class MaintenanceRead(BaseModel):
    """Schema para leer un mantenimiento"""
    id_mantenimiento: int = Field(..., description="ID del mantenimiento")
    station_id: int = Field(..., description="ID de la estación")
    fecha: str = Field(..., description="Fecha del mantenimiento")
    tecnico: str = Field(..., description="Técnico asignado")
    tipo: str = Field(..., description="Tipo de mantenimiento")
    estado: str = Field(..., description="Estado: programado/en_proceso/completado")
    notas: str = Field(..., description="Notas adicionales")
    frecuencia: Optional[str] = Field(None, description="Frecuencia (preventivo)")
    descripcion_fallo: Optional[str] = Field(None, description="Fallo (correctivo)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_mantenimiento": 5001,
                    "station_id": 1,
                    "fecha": "2024-12-20",
                    "tecnico": "Técnico Ana",
                    "tipo": "preventivo",
                    "estado": "programado",
                    "notas": "",
                    "frecuencia": "mensual",
                    "descripcion_fallo": None
                }
            ]
        }
    }


class CompletarMaintenanceRequest(BaseModel):
    """Schema para completar un mantenimiento"""
    notas: str = Field(default="", description="Notas del mantenimiento completado")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "notas": "Revisión completa. Todo OK. Próxima revisión en 3 meses."
                }
            ]
        }
    }