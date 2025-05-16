from database import db, app as flask_app
from modules.vehicle_management import Vehicle
from modules.dispatch import Route
from modules.monitoring import TrackingData

with flask_app.app_context():
    print("=== Проверка данных ===")
    vehicles = Vehicle.query.all()
    print(f"ТС: {len(vehicles)}")
    for v in vehicles:
        print(f"  ID: {v.id}, Рег. номер: {v.registration_number}, Тип: {v.vehicle_type}")
    routes = Route.query.all()
    print(f"Маршруты: {len(routes)}")
    for r in routes:
        print(f"  ID: {r.id}, Откуда: {r.start_location} ({r.start_lat}, {r.start_lon}) -> Куда: {r.end_location} ({r.end_lat}, {r.end_lon})")
    tracks = TrackingData.query.all()
    print(f"Треков мониторинга: {len(tracks)}")
    for t in tracks[:5]:
        print(f"  ТС: {t.vehicle_id}, Маршрут: {t.route_id}, Коорд: {t.latitude}, {t.longitude}, Время: {t.timestamp}")
    if not vehicles:
        print("ВНИМАНИЕ: Нет ТС в базе!")
    if not routes:
        print("ВНИМАНИЕ: Нет маршрутов в базе!")
    if not tracks:
        print("ВНИМАНИЕ: Нет треков мониторинга! Сгенерируйте треки через интерфейс.")