import datetime

class Session:
    def __init__(self, user, charger):
        self.user = user
        self.charger = charger
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def end(self):
        """Finaliza la sesión guardando la hora de término"""
        self.end_time = datetime.datetime.now()

    def get_duration(self):
        """Devuelve la duración en minutos"""
        if self.end_time:
            return (self.end_time - self.start_time).seconds // 60
        else:
            return (datetime.datetime.now() - self.start_time).seconds // 60