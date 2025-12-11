class Charger:
    def __init__(self, id, type, status="available"):
        self.id = id
        self.type = type
        self.status = status  # disponible / ocupado / mantenimiento

    def start_charge(self):
        if self.status == "disponible":
            self.status = "ocupado"
            print(f"Cargador {self.id} iniciado.")
        else:
            print(f"Cargador {self.id} no está disponible.")

    def stop_charge(self):
        if self.status == "ocupado":
            self.status = "disponible"
            print(f"Cargador {self.id} liberado.")
        else:
            print(f"Cargador {self.id} no estaba ocupado.")