from .charger import Charger

class Station:
    def __init__(self, id, name, location):
        self.id = id
        self.name = name
        self.location = location
        self.chargers = []

    def add_charger(self, charger):
        """Agrega un cargador a la estación"""
        self.chargers.append(charger)

    def get_available_chargers(self):
        """Devuelve una lista de cargadores disponibles"""
        return [c for c in self.chargers if c.status == "available"]

    def reserve_charger(self):
        """Reserva el primer cargador disponible, si existe"""
        disponible = self.get_available_chargers()
        if disponible:
            charger = disponible[0]
            charger.status = "ocupado"
            return charger
        return None
    