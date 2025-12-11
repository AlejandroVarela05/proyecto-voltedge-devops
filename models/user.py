"""
models/user.py - VoltEdge

Clase User actualizada para incluir autenticación con contraseña hasheada.
"""

from uuid import uuid4, UUID
from typing import Optional
from .session import Session


class User:
    """
    Clase base de usuario del sistema VoltEdge.
    
    Atributos:
        id (UUID): Identificador único del usuario
        name (str): Nombre del usuario
        email (str): Email del usuario (usado como username para login)
        password_hash (str): Contraseña hasheada con Argon2
        user_type (str): Tipo de usuario ('individual' o 'empresa')
        active_session (Session): Sesión de carga activa (si existe)
        saldo (float): Saldo disponible en la cuenta
    """
    
    def __init__(
        self, 
        name: str, 
        email: str, 
        password_hash: str,
        user_type: str = "individual",
        id: Optional[UUID] = None,
        saldo: float = 0.0
    ):
        self.id: UUID = id if id else uuid4()
        self.name: str = name
        self.email: str = email
        self.password_hash: str = password_hash
        self.user_type: str = user_type  # "individual" o "empresa"
        self.active_session: Optional[Session] = None
        self.saldo: float = saldo
        self.sessions_history: list[Session] = []

    def is_admin(self) -> bool:
        """Indica si el usuario es administrador"""
        return self.user_type == "admin"

    def get_tarifa(self) -> float:
        """
        Devuelve la tarifa por kWh según el tipo de usuario.
        - Individual: 0.30€/kWh
        - Empresa: 0.25€/kWh (5€ de descuento)
        """
        if self.user_type == "empresa":
            return 0.25
        return 0.30

    def recargar_saldo(self, cantidad: float) -> bool:
        """Añade saldo a la cuenta del usuario"""
        if cantidad <= 0:
            return False
        self.saldo += cantidad
        return True

    def tiene_saldo_suficiente(self, cantidad: float) -> bool:
        """Verifica si el usuario tiene saldo suficiente"""
        return self.saldo >= cantidad

    def descontar_saldo(self, cantidad: float) -> bool:
        """Descuenta saldo de la cuenta"""
        if not self.tiene_saldo_suficiente(cantidad):
            return False
        self.saldo -= cantidad
        return True

    def start_session(self, charger):
        """Inicia una sesión si el cargador está disponible"""
        if charger.status == "disponible" or charger.status == "available":
            charger.start_charge()
            self.active_session = Session(self, charger)
            print(f"{self.name} comenzó una sesión en el cargador {charger.id}")
            return self.active_session
        else:
            print(f"El cargador {charger.id} no está disponible.")
            return None

    def end_session(self):
        """Finaliza la sesión activa"""
        if self.active_session:
            self.active_session.end()
            
            # Calcular y cobrar
            duracion_minutos = self.active_session.get_duration()
            kwh_consumidos = duracion_minutos * 0.5  # Simulación: 0.5 kWh/min
            tarifa = self.get_tarifa()
            coste = kwh_consumidos * tarifa
            
            if self.descontar_saldo(coste):
                print(f"✅ Cobrado: {coste:.2f}€ ({kwh_consumidos:.2f} kWh a {tarifa}€/kWh)")
            else:
                print(f"⚠️ Saldo insuficiente. Coste: {coste:.2f}€, Saldo: {self.saldo:.2f}€")
            
            # Guardar en historial
            self.sessions_history.append(self.active_session)
            
            self.active_session.charger.stop_charge()
            print(f"{self.name} terminó su sesión.")
            self.active_session = None
        else:
            print(f"{self.name} no tiene ninguna sesión activa.")

    def get_historial_sesiones(self) -> list[Session]:
        """Devuelve el historial de sesiones del usuario"""
        return self.sessions_history

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name}, email={self.email}, type={self.user_type}, saldo={self.saldo:.2f}€)"

    def __eq__(self, other: object) -> bool:
        """Compara usuarios por ID"""
        if isinstance(other, User):
            return self.id == other.id
        return False