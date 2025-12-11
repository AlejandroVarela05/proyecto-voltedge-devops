"""
main.py - VoltEdge API REST COMPLETA

API REST completa para el sistema VoltEdge con autenticación JWT.
Incluye gestión de usuarios, estaciones, cargadores, sesiones y mantenimientos.
"""

from __future__ import annotations
from typing import List
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

# Servicios
from services.service import ChargingService
from services.auth_service import (
    create_access_token, 
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Schemas
from schemas.auth_schemas import (
    UsuarioRegistro, 
    UsuarioRegistroResponse, 
    Token, 
    UsuarioAutenticado
)
from schemas.user_schemas import UserRead, RecargaSaldo, RecargaSaldoResponse
from schemas.station_schemas import (
    StationCreate, 
    StationRead, 
    ChargerInfo,
    StationDisponibilidad,
    StationConsumo
)
from schemas.charger_schemas import ChargerCreate, ChargerRead, IniciarCargaRequest
from schemas.session_schemas import SessionCreate, SessionRead, CerrarSessionRequest
from schemas.maintenance_schemas import (
    MaintenanceCreate, 
    MaintenanceRead,
    CompletarMaintenanceRequest
)

# ==================== CONFIGURACIÓN ====================

app = FastAPI(
    title="VoltEdge API",
    description="API REST para gestión de sistema de carga de vehículos eléctricos",
    version="1.0.0"
)

voltedge_service = ChargingService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# ==================== DEPENDENCIAS ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UsuarioAutenticado:
    """
    Dependencia que extrae y valida el usuario actual desde el token JWT.
    """
    email = decode_access_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = voltedge_service.get_user_by_email(email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UsuarioAutenticado(
        id=user.id,
        name=user.name,
        email=user.email,
        user_type=user.user_type,
        saldo=user.saldo
    )


async def get_current_admin(current_user: UsuarioAutenticado = Depends(get_current_user)) -> UsuarioAutenticado:
    """
    Dependencia que verifica que el usuario actual es administrador.
    """
    user = voltedge_service.get_user_by_id(current_user.id)
    
    if not user or not user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador para realizar esta acción"
        )
    
    return current_user


# ==================== ENDPOINT RAÍZ ====================

@app.get("/", tags=["General"])
def root():
    """Endpoint raíz de la API"""
    return {
        "message": "⚡ VoltEdge API - Sistema de Carga de Vehículos Eléctricos",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==================== AUTENTICACIÓN ====================

@app.post("/auth/registro", response_model=UsuarioRegistroResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticación"])
def registrar_usuario(datos: UsuarioRegistro) -> UsuarioRegistroResponse:
    """
    Registra un nuevo usuario en el sistema.
    
    - Verifica que el email no esté duplicado
    - Hashea la contraseña con Argon2
    - Asigna saldo inicial
    """
    try:
        user = voltedge_service.register_user(
            name=datos.name,
            email=datos.email,
            password=datos.password,
            user_type=datos.user_type,
            saldo_inicial=datos.saldo_inicial
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
    return UsuarioRegistroResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        user_type=user.user_type,
        saldo=user.saldo,
        mensaje="Usuario registrado exitosamente"
    )


@app.post("/auth/token", response_model=Token, tags=["Autenticación"])
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Endpoint de login. Devuelve un token JWT válido por 1 hora.
    
    - username: Email del usuario
    - password: Contraseña
    """
    user = voltedge_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/auth/me", response_model=UsuarioAutenticado, tags=["Autenticación"])
def obtener_usuario_actual(current_user: UsuarioAutenticado = Depends(get_current_user)) -> UsuarioAutenticado:
    """
    Obtiene la información del usuario autenticado actualmente.
    """
    return current_user


# ==================== USUARIOS ====================

@app.get("/users", response_model=List[UserRead], tags=["Usuarios"], dependencies=[Depends(get_current_admin)])
def listar_usuarios() -> List[UserRead]:
    """
    Lista todos los usuarios del sistema.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    users = list(voltedge_service.users.values())
    
    return [
        UserRead(
            id=u.id,
            name=u.name,
            email=u.email,
            user_type=u.user_type,
            saldo=u.saldo,
            tarifa_kwh=u.get_tarifa()
        )
        for u in users
    ]


@app.get("/users/{user_id}", response_model=UserRead, tags=["Usuarios"])
def obtener_usuario(user_id: UUID, current_user: UsuarioAutenticado = Depends(get_current_user)) -> UserRead:
    """
    Obtiene información de un usuario específico.
    
    **Requiere:** Autenticación (solo puede ver su propia info o admin puede ver cualquiera)
    """
    user = voltedge_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Solo admin o el propio usuario pueden ver la info
    if user.id != current_user.id and not voltedge_service.get_user_by_id(current_user.id).is_admin():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver este usuario")
    
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        user_type=user.user_type,
        saldo=user.saldo,
        tarifa_kwh=user.get_tarifa()
    )


@app.post("/users/{user_id}/recargar-saldo", response_model=RecargaSaldoResponse, tags=["Usuarios"])
def recargar_saldo(
    user_id: UUID, 
    recarga: RecargaSaldo, 
    current_user: UsuarioAutenticado = Depends(get_current_user)
) -> RecargaSaldoResponse:
    """
    Recarga saldo a un usuario.
    
    **Requiere:** Autenticación (solo puede recargar su propio saldo)
    """
    # Solo puede recargar su propio saldo
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes recargar tu propio saldo")
    
    user = voltedge_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    saldo_anterior = user.saldo
    
    if not voltedge_service.recargar_saldo_usuario(user_id, recarga.cantidad):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al recargar saldo")
    
    return RecargaSaldoResponse(
        user_id=user_id,
        saldo_anterior=saldo_anterior,
        cantidad_recargada=recarga.cantidad,
        saldo_nuevo=user.saldo,
        mensaje="Saldo recargado exitosamente"
    )


@app.get("/users/{user_id}/historial", response_model=List[SessionRead], tags=["Usuarios"])
def obtener_historial_sesiones(
    user_id: UUID, 
    current_user: UsuarioAutenticado = Depends(get_current_user)
) -> List[SessionRead]:
    """
    Obtiene el historial de sesiones de carga de un usuario.
    
    **Requiere:** Autenticación (solo puede ver su propio historial o admin)
    """
    # Solo puede ver su propio historial o admin
    if user_id != current_user.id and not voltedge_service.get_user_by_id(current_user.id).is_admin():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver este historial")
    
    sessions = voltedge_service.get_user_sessions_history(user_id)
    
    resultado = []
    for s in sessions:
        duracion = s.get_duration()
        kwh = duracion * 0.5
        tarifa = s.user.get_tarifa()
        coste = kwh * tarifa
        
        resultado.append(SessionRead(
            user_id=s.user.id,
            user_name=s.user.name,
            charger_id=s.charger.id,
            start_time=s.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=s.end_time.strftime("%Y-%m-%d %H:%M:%S") if s.end_time else None,
            duration_minutes=duracion,
            kwh_consumidos=kwh,
            coste=coste,
            activa=s.end_time is None
        ))
    
    return resultado


# ==================== ESTACIONES ====================

@app.post("/stations", response_model=StationRead, status_code=status.HTTP_201_CREATED, tags=["Estaciones"], dependencies=[Depends(get_current_admin)])
def crear_estacion(station: StationCreate) -> StationRead:
    """
    Crea una nueva estación de carga.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    created_station = voltedge_service.create_station(station.id, station.name, station.location)
    
    return StationRead(
        id=created_station.id,
        name=created_station.name,
        location=created_station.location,
        total_chargers=len(created_station.chargers),
        disponibles=len(created_station.get_available_chargers()),
        chargers=[
            ChargerInfo(id=c.id, type=c.type, status=c.status)
            for c in created_station.chargers
        ]
    )


@app.get("/stations", response_model=List[StationRead], tags=["Estaciones"])
def listar_estaciones() -> List[StationRead]:
    """
    Lista todas las estaciones de carga disponibles.
    
    **No requiere autenticación** (información pública)
    """
    stations = voltedge_service.list_stations()
    
    return [
        StationRead(
            id=s.id,
            name=s.name,
            location=s.location,
            total_chargers=len(s.chargers),
            disponibles=len(s.get_available_chargers()),
            chargers=[
                ChargerInfo(id=c.id, type=c.type, status=c.status)
                for c in s.chargers
            ]
        )
        for s in stations
    ]


@app.get("/stations/{station_id}", response_model=StationRead, tags=["Estaciones"])
def obtener_estacion(station_id: int) -> StationRead:
    """
    Obtiene información de una estación específica.
    
    **No requiere autenticación** (información pública)
    """
    station = voltedge_service.get_station(station_id)
    
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estación no encontrada")
    
    return StationRead(
        id=station.id,
        name=station.name,
        location=station.location,
        total_chargers=len(station.chargers),
        disponibles=len(station.get_available_chargers()),
        chargers=[
            ChargerInfo(id=c.id, type=c.type, status=c.status)
            for c in station.chargers
        ]
    )


@app.delete("/stations/{station_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Estaciones"], dependencies=[Depends(get_current_admin)])
def eliminar_estacion(station_id: int):
    """
    Elimina una estación de carga.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    if not voltedge_service.delete_station(station_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estación no encontrada")


@app.get("/stations/{station_id}/disponibilidad", response_model=StationDisponibilidad, tags=["Estaciones"])
def obtener_disponibilidad_estacion(station_id: int) -> StationDisponibilidad:
    """
    Obtiene la disponibilidad en tiempo real de una estación.
    
    **No requiere autenticación** (información pública)
    """
    data = voltedge_service.get_station_disponibilidad(station_id)
    
    if "error" in data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["error"])
    
    return StationDisponibilidad(**data)


@app.get("/stations/{station_id}/reporte-consumo", response_model=StationConsumo, tags=["Estaciones"], dependencies=[Depends(get_current_admin)])
def obtener_reporte_consumo(station_id: int) -> StationConsumo:
    """
    Genera un reporte de consumo de una estación.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    data = voltedge_service.get_station_consumo(station_id)
    
    if "error" in data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["error"])
    
    return StationConsumo(**data)


# ==================== CARGADORES ====================

@app.post("/stations/{station_id}/chargers", response_model=ChargerRead, status_code=status.HTTP_201_CREATED, tags=["Cargadores"], dependencies=[Depends(get_current_admin)])
def añadir_cargador(station_id: int, charger: ChargerCreate) -> ChargerRead:
    """
    Añade un nuevo cargador a una estación.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    created_charger = voltedge_service.add_charger_to_station(station_id, charger.charger_id, charger.charger_type)
    
    if not created_charger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estación no encontrada")
    
    return ChargerRead(
        id=created_charger.id,
        type=created_charger.type,
        status=created_charger.status
    )


@app.get("/chargers", response_model=List[ChargerRead], tags=["Cargadores"])
def listar_cargadores() -> List[ChargerRead]:
    """
    Lista todos los cargadores del sistema.
    
    **No requiere autenticación** (información pública)
    """
    chargers = voltedge_service.list_chargers()
    
    return [
        ChargerRead(id=c.id, type=c.type, status=c.status)
        for c in chargers
    ]


@app.get("/chargers/{charger_id}", response_model=ChargerRead, tags=["Cargadores"])
def obtener_cargador(charger_id: int) -> ChargerRead:
    """
    Obtiene información de un cargador específico.
    
    **No requiere autenticación** (información pública)
    """
    charger = voltedge_service.get_charger(charger_id)
    
    if not charger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargador no encontrado")
    
    return ChargerRead(id=charger.id, type=charger.type, status=charger.status)


# ==================== SESIONES ====================

@app.post("/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED, tags=["Sesiones"])
def crear_sesion(session_data: SessionCreate, current_user: UsuarioAutenticado = Depends(get_current_user)) -> SessionRead:
    """
    Inicia una nueva sesión de carga.
    
    **Requiere:** Autenticación (usuario debe ser el que inicia)
    """
    # Solo puede iniciar sesión para sí mismo
    if session_data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes iniciar sesiones para ti mismo")
    
    session = voltedge_service.start_charging(session_data.user_id, session_data.station_id)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo iniciar la sesión. Verifica disponibilidad.")
    
    duracion = session.get_duration()
    kwh = duracion * 0.5
    tarifa = session.user.get_tarifa()
    coste = kwh * tarifa
    
    return SessionRead(
        user_id=session.user.id,
        user_name=session.user.name,
        charger_id=session.charger.id,
        start_time=session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=None,
        duration_minutes=duracion,
        kwh_consumidos=kwh,
        coste=coste,
        activa=True
    )


@app.post("/sessions/cerrar", response_model=SessionRead, tags=["Sesiones"])
def cerrar_sesion(close_data: CerrarSessionRequest, current_user: UsuarioAutenticado = Depends(get_current_user)) -> SessionRead:
    """
    Finaliza una sesión de carga activa.
    
    **Requiere:** Autenticación (usuario debe ser el que cierra)
    """
    # Solo puede cerrar su propia sesión
    if close_data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes cerrar tu propia sesión")
    
    user = voltedge_service.get_user_by_id(close_data.user_id)
    
    if not user or not user.active_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No tienes ninguna sesión activa")
    
    session = user.active_session
    voltedge_service.end_charging(close_data.user_id)
    
    duracion = session.get_duration()
    kwh = duracion * 0.5
    tarifa = user.get_tarifa()
    coste = kwh * tarifa
    
    return SessionRead(
        user_id=user.id,
        user_name=user.name,
        charger_id=session.charger.id,
        start_time=session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else None,
        duration_minutes=duracion,
        kwh_consumidos=kwh,
        coste=coste,
        activa=False
    )


# ==================== MANTENIMIENTOS ====================

@app.post("/maintenance", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED, tags=["Mantenimiento"], dependencies=[Depends(get_current_admin)])
def programar_mantenimiento(maintenance_data: MaintenanceCreate) -> MaintenanceRead:
    """
    Programa un mantenimiento (preventivo o correctivo).
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    if maintenance_data.tipo == "preventivo":
        if not maintenance_data.frecuencia:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La frecuencia es obligatoria para mantenimientos preventivos")
        
        maintenance = voltedge_service.programar_mantenimiento_preventivo(
            id_mantenimiento=maintenance_data.id_mantenimiento,
            station_id=maintenance_data.station_id,
            fecha=maintenance_data.fecha,
            tecnico=maintenance_data.tecnico,
            frecuencia=maintenance_data.frecuencia
        )
    
    elif maintenance_data.tipo == "correctivo":
        if not maintenance_data.descripcion_fallo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La descripción del fallo es obligatoria para mantenimientos correctivos")
        
        maintenance = voltedge_service.programar_mantenimiento_correctivo(
            id_mantenimiento=maintenance_data.id_mantenimiento,
            station_id=maintenance_data.station_id,
            fecha=maintenance_data.fecha,
            tecnico=maintenance_data.tecnico,
            descripcion_fallo=maintenance_data.descripcion_fallo
        )
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de mantenimiento inválido. Usa 'preventivo' o 'correctivo'")
    
    return MaintenanceRead(
        id_mantenimiento=maintenance.id_mantenimiento,
        station_id=maintenance.estacion_id,
        fecha=maintenance.fecha.strftime("%Y-%m-%d"),
        tecnico=maintenance.tecnico,
        tipo=maintenance.tipo,
        estado=maintenance.estado,
        notas=maintenance.notas,
        frecuencia=getattr(maintenance, 'frecuencia', None),
        descripcion_fallo=getattr(maintenance, 'descripcion_fallo', None)
    )


@app.get("/maintenance", response_model=List[MaintenanceRead], tags=["Mantenimiento"], dependencies=[Depends(get_current_admin)])
def listar_mantenimientos(station_id: int = None) -> List[MaintenanceRead]:
    """
    Lista todos los mantenimientos o filtra por estación.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    maintenances = voltedge_service.listar_mantenimientos(station_id)
    
    return [
        MaintenanceRead(
            id_mantenimiento=m.id_mantenimiento,
            station_id=m.estacion_id,
            fecha=m.fecha.strftime("%Y-%m-%d") if hasattr(m.fecha, 'strftime') else str(m.fecha),
            tecnico=m.tecnico,
            tipo=m.tipo,
            estado=m.estado,
            notas=m.notas,
            frecuencia=getattr(m, 'frecuencia', None),
            descripcion_fallo=getattr(m, 'descripcion_fallo', None)
        )
        for m in maintenances
    ]


@app.post("/maintenance/{id_mantenimiento}/iniciar", response_model=MaintenanceRead, tags=["Mantenimiento"], dependencies=[Depends(get_current_admin)])
def iniciar_mantenimiento(id_mantenimiento: int) -> MaintenanceRead:
    """
    Marca un mantenimiento como "en proceso".
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    maintenance = voltedge_service.iniciar_mantenimiento(id_mantenimiento)
    
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mantenimiento no encontrado")
    
    return MaintenanceRead(
        id_mantenimiento=maintenance.id_mantenimiento,
        station_id=maintenance.estacion_id,
        fecha=maintenance.fecha.strftime("%Y-%m-%d"),
        tecnico=maintenance.tecnico,
        tipo=maintenance.tipo,
        estado=maintenance.estado,
        notas=maintenance.notas,
        frecuencia=getattr(maintenance, 'frecuencia', None),
        descripcion_fallo=getattr(maintenance, 'descripcion_fallo', None)
    )


@app.post("/maintenance/{id_mantenimiento}/completar", response_model=MaintenanceRead, tags=["Mantenimiento"], dependencies=[Depends(get_current_admin)])
def completar_mantenimiento(id_mantenimiento: int, completion_data: CompletarMaintenanceRequest) -> MaintenanceRead:
    """
    Marca un mantenimiento como completado.
    
    **Requiere:** Autenticación + Permisos de Admin
    """
    maintenance = voltedge_service.completar_mantenimiento(id_mantenimiento, completion_data.notas)
    
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mantenimiento no encontrado")
    
    return MaintenanceRead(
        id_mantenimiento=maintenance.id_mantenimiento,
        station_id=maintenance.estacion_id,
        fecha=maintenance.fecha.strftime("%Y-%m-%d"),
        tecnico=maintenance.tecnico,
        tipo=maintenance.tipo,
        estado=maintenance.estado,
        notas=maintenance.notas,
        frecuencia=getattr(maintenance, 'frecuencia', None),
        descripcion_fallo=getattr(maintenance, 'descripcion_fallo', None)
    )


# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)