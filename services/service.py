"""
services/service.py - VoltEdge

Servicio principal actualizado para usar diccionarios y soportar autenticación.
"""

from typing import Dict, List, Optional
from uuid import UUID
from models.station import Station
from models.charger import Charger
from models.user import User
from models.session import Session
from models.maintenance import Maintenance, PreventiveMaintenance, CorrectiveMaintenance
from .auth_service import hash_password, verify_password


class ChargingService:
    def __init__(self):
        # Usar diccionarios para mejor rendimiento en búsquedas
        self.stations: Dict[int, Station] = {}
        self.chargers: Dict[int, Charger] = {}
        self.users: Dict[UUID, User] = {}
        self.sessions: Dict[UUID, Session] = {}
        self.maintenances: Dict[int, Maintenance] = {}

    # ==================== AUTENTICACIÓN ====================

    def register_user(
        self, 
        name: str, 
        email: str, 
        password: str, 
        user_type: str = "individual",
        saldo_inicial: float = 50.0
    ) -> User:
        """
        Registra un nuevo usuario con contraseña hasheada.
        
        Args:
            name: Nombre del usuario
            email: Email (único, usado como username)
            password: Contraseña en texto plano
            user_type: 'individual', 'empresa' o 'admin'
            saldo_inicial: Saldo inicial (por defecto 50€)
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si el email ya está registrado
        """
        # Verificar email duplicado
        if self.get_user_by_email(email):
            raise ValueError(f"El email {email} ya está registrado.")
        
        # Hashear contraseña
        password_hash = hash_password(password)
        
        # Crear usuario
        user = User(
            name=name, 
            email=email, 
            password_hash=password_hash, 
            user_type=user_type,
            saldo=saldo_inicial
        )
        
        self.users[user.id] = user
        print(f"Usuario '{name}' registrado ({user_type}) con saldo inicial {saldo_inicial}€")
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario verificando email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario si las credenciales son correctas, None si no
        """
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca un usuario por ID"""
        return self.users.get(user_id)

    # ==================== GESTIÓN DE ESTACIONES ====================

    def create_station(self, id: int, name: str, location: str) -> Station:
        """Crea una nueva estación de carga"""
        station = Station(id, name, location)
        self.stations[id] = station
        print(f"Estación '{name}' creada en {location}")
        return station

    def get_station(self, station_id: int) -> Optional[Station]:
        """Obtiene una estación por ID"""
        return self.stations.get(station_id)

    def list_stations(self) -> List[Station]:
        """Lista todas las estaciones"""
        return list(self.stations.values())

    def delete_station(self, station_id: int) -> bool:
        """Elimina una estación (solo admin)"""
        if station_id in self.stations:
            del self.stations[station_id]
            print(f"Estación {station_id} eliminada")
            return True
        return False

    # ==================== GESTIÓN DE CARGADORES ====================

    def add_charger_to_station(self, station_id: int, charger_id: int, charger_type: str) -> Optional[Charger]:
        """Añade un cargador a una estación"""
        station = self.get_station(station_id)
        if not station:
            print("Estación no encontrada.")
            return None
        
        charger = Charger(charger_id, charger_type)
        station.add_charger(charger)
        self.chargers[charger_id] = charger
        print(f"Cargador {charger_id} ({charger_type}) añadido a {station.name}")
        return charger

    def get_charger(self, charger_id: int) -> Optional[Charger]:
        """Obtiene un cargador por ID"""
        return self.chargers.get(charger_id)

    def list_chargers(self) -> List[Charger]:
        """Lista todos los cargadores"""
        return list(self.chargers.values())

    # ==================== GESTIÓN DE SESIONES ====================

    def start_charging(self, user_id: UUID, station_id: int) -> Optional[Session]:
        """Inicia una sesión de carga"""
        user = self.get_user_by_id(user_id)
        station = self.get_station(station_id)

        if not user:
            print("Usuario no encontrado.")
            return None
        
        if not station:
            print("Estación no encontrada.")
            return None

        available = station.get_available_chargers()
        if not available:
            print(f"No hay cargadores disponibles en {station.name}.")
            return None

        charger = available[0]
        session = user.start_session(charger)
        
        if session:
            self.sessions[session.user.id] = session
        
        return session

    def end_charging(self, user_id: UUID) -> bool:
        """Finaliza la sesión de carga de un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            print("Usuario no encontrado.")
            return False
        
        user.end_session()
        
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        return True

    def get_user_sessions_history(self, user_id: UUID) -> List[Session]:
        """Obtiene el historial de sesiones de un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        return user.get_historial_sesiones()

    # ==================== GESTIÓN DE SALDO ====================

    def recargar_saldo_usuario(self, user_id: UUID, cantidad: float) -> bool:
        """Recarga saldo a un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        return user.recargar_saldo(cantidad)

    # ==================== MANTENIMIENTO ====================

    def programar_mantenimiento_preventivo(
        self, 
        id_mantenimiento: int, 
        station_id: int, 
        fecha: str, 
        tecnico: str, 
        frecuencia: str
    ) -> PreventiveMaintenance:
        """Programa un mantenimiento preventivo"""
        m = PreventiveMaintenance(id_mantenimiento, fecha, tecnico, frecuencia)
        m.asignar_estacion(station_id)
        self.maintenances[id_mantenimiento] = m
        print(m.programar())
        return m

    def programar_mantenimiento_correctivo(
        self, 
        id_mantenimiento: int, 
        station_id: int, 
        fecha: str, 
        tecnico: str, 
        descripcion_fallo: str
    ) -> CorrectiveMaintenance:
        """Programa un mantenimiento correctivo"""
        m = CorrectiveMaintenance(id_mantenimiento, fecha, tecnico, descripcion_fallo)
        m.asignar_estacion(station_id)
        self.maintenances[id_mantenimiento] = m
        print(m.programar())
        return m

    def iniciar_mantenimiento(self, id_mantenimiento: int) -> Optional[Maintenance]:
        """Inicia un mantenimiento"""
        m = self.maintenances.get(id_mantenimiento)
        if not m:
            print("Mantenimiento no encontrado.")
            return None
        print(m.iniciar())
        return m

    def completar_mantenimiento(self, id_mantenimiento: int, notas: str = "") -> Optional[Maintenance]:
        """Completa un mantenimiento"""
        m = self.maintenances.get(id_mantenimiento)
        if not m:
            print("Mantenimiento no encontrado.")
            return None
        print(m.marcar_completado(notas))
        return m

    def listar_mantenimientos(self, station_id: Optional[int] = None) -> List[Maintenance]:
        """Lista mantenimientos, opcionalmente filtrados por estación"""
        if station_id:
            return [m for m in self.maintenances.values() if m.estacion_id == station_id]
        return list(self.maintenances.values())

    def get_mantenimiento(self, id_mantenimiento: int) -> Optional[Maintenance]:
        """Obtiene un mantenimiento por ID"""
        return self.maintenances.get(id_mantenimiento)

    # ==================== REPORTES Y ESTADÍSTICAS ====================

    def get_station_disponibilidad(self, station_id: int) -> dict:
        """Obtiene la disponibilidad de cargadores en una estación"""
        station = self.get_station(station_id)
        if not station:
            return {"error": "Estación no encontrada"}
        
        total = len(station.chargers)
        disponibles = len(station.get_available_chargers())
        ocupados = total - disponibles
        
        return {
            "station_id": station_id,
            "station_name": station.name,
            "total_chargers": total,
            "disponibles": disponibles,
            "ocupados": ocupados,
            "porcentaje_disponibilidad": (disponibles / total * 100) if total > 0 else 0
        }

    def get_station_consumo(self, station_id: int) -> dict:
        """Genera un reporte de consumo de una estación"""
        station = self.get_station(station_id)
        if not station:
            return {"error": "Estación no encontrada"}
        
        # Simular datos de consumo
        total_sesiones = len([s for s in self.sessions.values() if s.charger in station.chargers])
        
        return {
            "station_id": station_id,
            "station_name": station.name,
            "total_sesiones": total_sesiones,
            "sesiones_activas": len([c for c in station.chargers if c.status == "ocupado"])
        }