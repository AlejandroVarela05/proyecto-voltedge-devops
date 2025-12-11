"""
main_demo.py - VoltEdge

Este es tu main.py original, ahora renombrado a main_demo.py
para que puedas ejecutarlo como demostración sin interferir con la API.

Para ejecutar la demo:
    python main_demo.py
"""

from services.service import ChargingService

def main():
    print("=== VOLTEDGE - Sistema de Carga de Vehículos Eléctricos ===\n")

    service = ChargingService()

    # Crear estación
    station = service.create_station(1, "Estación Central", "Vigo")

    # prueba de mantenimiento
    print("\n--- Prueba de Mantenimientos ---")
    service = ChargingService()  # si no lo tienes aún, usa el objeto service que ya hayas creado

    # crear estación para el ejemplo
    station = service.create_station(2, "Estación Norte", "Vigo Norte")
    service.add_charger_to_station(2, 201, "normal")

    # programar preventivo
    m1 = service.programar_mantenimiento_preventivo(
        id_mantenimiento=5001,
        station_id=2,
        fecha="2025-11-20",
        tecnico="Técnico Ana",
        frecuencia="mensual"
    )

    # programar correctivo
    m2 = service.programar_mantenimiento_correctivo(
        id_mantenimiento=5002,
        station_id=2,
        fecha="2025-11-21",
        tecnico="Técnico Luis",
        descripcion_fallo="Fallo en conector tipo 2"
    )

    # listar
    print("\nMantenimientos registrados:")
    for m in service.listar_mantenimientos(station_id=2):
        print(m)

    # iniciar y completar uno
    service.iniciar_mantenimiento(5002)
    service.completar_mantenimiento(5002, notas="Reemplazado conector, pruebas OK")

    # Añadir cargadores
    service.add_charger_to_station(1, 101, "rápido")
    service.add_charger_to_station(1, 102, "normal")

    # NOTA: El método register_user ahora requiere password
    # Para esta demo, usamos una contraseña simple
    print("\n--- Registrando usuarios con contraseñas ---")
    user1 = service.register_user("Yésica", "yesica@example.com", "password123", "individual", 100.0)
    user2 = service.register_user("María", "maria@example.com", "password456", "individual", 100.0)

    # Usuario inicia carga
    print("\nIniciando sesión de carga:")
    service.start_charging(user1.id, station.id)

    # Intentar iniciar con otro usuario (si quedan cargadores)
    service.start_charging(user2.id, station.id)

    # Finalizar la primera sesión
    print("\nFinalizando sesión:")
    service.end_charging(user1.id)

    print("\nSimulación completada.")

if __name__ == "__main__":
    main()