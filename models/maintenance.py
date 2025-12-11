from datetime import datetime

class Maintenance:
    def __init__(self, id_mantenimiento, fecha, tecnico, tipo):
        """
        fecha: string ISO 'YYYY-MM-DD' o datetime
        tipo: 'preventivo' | 'correctivo'
        """
        self.id_mantenimiento = id_mantenimiento
        if isinstance(fecha, str):
            try:
                self.fecha = datetime.fromisoformat(fecha)
            except ValueError:
                self.fecha = datetime.now()
        else:
            self.fecha = fecha
        self.tecnico = tecnico
        self.tipo = tipo  # "preventivo" o "correctivo"
        self.estado = "programado"  # programado / en_proceso / completado
        self.estacion_id = None
        self.notas = ""

    def asignar_estacion(self, station_id):
        self.estacion_id = station_id

    def programar(self):
        self.estado = "programado"
        return f"Mantenimiento {self.id_mantenimiento} programado para {self.fecha.date()} en estación {self.estacion_id}"

    def iniciar(self):
        self.estado = "en_proceso"
        return f"Mantenimiento {self.id_mantenimiento} iniciado por {self.tecnico}"

    def marcar_completado(self, notas=""):
        self.estado = "completado"
        self.notas = notas
        return f"Mantenimiento {self.id_mantenimiento} completado. Notas: {self.notas}"

    def __str__(self):
        fecha = self.fecha.date() if hasattr(self.fecha, "date") else self.fecha
        return f"[{self.id_mantenimiento}] {self.tipo} - estación:{self.estacion_id} - {fecha} - {self.tecnico} - {self.estado}"


class PreventiveMaintenance(Maintenance):
    def __init__(self, id_mantenimiento, fecha, tecnico, frecuencia):
        super().__init__(id_mantenimiento, fecha, tecnico, tipo="preventivo")
        self.frecuencia = frecuencia  # p.ej. "mensual", "trimestral"


class CorrectiveMaintenance(Maintenance):
    def __init__(self, id_mantenimiento, fecha, tecnico, descripcion_fallo):
        super().__init__(id_mantenimiento, fecha, tecnico, tipo="correctivo")
        self.descripcion_fallo = descripcion_fallo