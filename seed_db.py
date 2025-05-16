from database import db, app
from modules.vehicle_management import Vehicle, MaintenanceRecord, SparePart, FuelRecord, OwnershipHistory
from modules.dispatch import Driver, Route, Task, WorkHours, TaskStatus
from modules.monitoring import TrackingData, GPSData, FuelConsumption, DrivingStyle, Violation
from datetime import datetime, timedelta
import random

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
 
        vehicles = [
            Vehicle(registration_number=f"A{1000+i}BC77", brand="ГАЗ", model=f"330{i}", year=2010+i, technical_specs="2.7 л, бензин", current_status="В эксплуатации", vehicle_type=("легковой" if i%3==0 else ("автобус" if i%3==1 else "грузовой")), created_at=datetime.now()-timedelta(days=10*i), updated_at=datetime.now()-timedelta(days=5*i))
            for i in range(5)
        ]
        db.session.add_all(vehicles)
    
        drivers = [
            Driver(name=f"Водитель {i+1}", license_number=f"77AA{i+1:04d}", license_expiry=datetime.now()+timedelta(days=365*random.randint(1,5)), contact_info=f"+7 900 000 00{10+i}", status="Активен")
            for i in range(5)
        ]
        db.session.add_all(drivers)
        db.session.flush()
    
        route_coords = [
            ("Москва", "Тула", (55.7558, 37.6176, 54.1931, 37.6177)),
            ("Санкт-Петербург", "Казань", (59.9343, 30.3351, 55.7963, 49.1088)),
            ("Новосибирск", "Екатеринбург", (55.0084, 82.9357, 56.8389, 60.6057)),
            ("Нижний Новгород", "Воронеж", (56.2965, 43.9361, 51.6615, 39.2003)),
            ("Самара", "Ростов-на-Дону", (53.1959, 50.1008, 47.2357, 39.7015)),
        ]
        routes = [
            Route(vehicle_id=vehicles[i%5].id, driver_id=drivers[i%5].id, start_location=rc[0], end_location=rc[1], distance=180+100*i, estimated_time=120+30*i, status="Завершён", created_at=datetime.now()-timedelta(days=i), updated_at=datetime.now()-timedelta(days=i-1),
                  start_lat=rc[2][0], start_lon=rc[2][1], end_lat=rc[2][2], end_lon=rc[2][3])
            for i, rc in enumerate(route_coords)
        ]
        db.session.add_all(routes)
    
        maints = [
            MaintenanceRecord(vehicle_id=vehicles[i%5].id, maintenance_type="Плановое ТО", description="Замена масла", cost=3500+100*i, date=datetime.now()-timedelta(days=30*i), next_maintenance_date=datetime.now()+timedelta(days=180-30*i), parts_used="Масло, фильтр", created_at=datetime.now()-timedelta(days=30*i))
            for i in range(5)
        ]
        db.session.add_all(maints)
       
        parts = [
            SparePart(name="Масляный фильтр", part_number=f"FILT{i}", quantity=10-i, min_quantity=2, cost=500+50*i, supplier="Поставщик А", last_order_date=datetime.now()-timedelta(days=10*i))
            for i in range(5)
        ]
        db.session.add_all(parts)
    
        fuels = [
            FuelRecord(vehicle_id=vehicles[i%5].id, fuel_type="АИ-92", amount=40+5*i, cost=2500+100*i, date=datetime.now()-timedelta(days=5*i), mileage=10000+500*i)
            for i in range(5)
        ]
        db.session.add_all(fuels)
      
        owners = [
            OwnershipHistory(vehicle_id=vehicles[i%5].id, owner_name=f"Компания {i+1}", start_date=datetime.now()-timedelta(days=365*(i+1)), end_date=datetime.now()-timedelta(days=365*i), documents="Договор.pdf")
            for i in range(5)
        ]
        db.session.add_all(owners)
      
        tracks = [
            TrackingData(vehicle_id=vehicles[i%5].id, route_id=routes[i%5].id, latitude=55.7+0.01*i, longitude=37.6+0.01*i, speed=60+2*i, fuel_level=50-2*i, timestamp=datetime.now()-timedelta(hours=i), additional_data="")
            for i in range(5)
        ]
        db.session.add_all(tracks)
        # GPSData
        gps = [
            GPSData(vehicle_id=vehicles[i%5].id, timestamp=datetime.now()-timedelta(hours=i), latitude=55.7+0.01*i, longitude=37.6+0.01*i, speed=60+2*i, heading=90.0+5*i)
            for i in range(5)
        ]
        db.session.add_all(gps)
        # FuelConsumption
        fuel_cons = [
            FuelConsumption(vehicle_id=vehicles[i%5].id, timestamp=datetime.now()-timedelta(days=i), consumption_rate=10.5+0.5*i, current_level=40-2*i)
            for i in range(5)
        ]
        db.session.add_all(fuel_cons)
        # DrivingStyle
        driving = [
            DrivingStyle(vehicle_id=vehicles[i%5].id, driver_id=drivers[i%5].id, timestamp=datetime.now()-timedelta(days=i), acceleration_score=80-2*i, braking_score=85-2*i, cornering_score=90-2*i, overall_score=88-2*i)
            for i in range(5)
        ]
        db.session.add_all(driving)
        # Violations
        violations = [
            Violation(vehicle_id=vehicles[i%5].id, driver_id=drivers[i%5].id, timestamp=datetime.now()-timedelta(days=i), violation_type="Превышение скорости", details={"speed": 100+5*i}, location="Москва")
            for i in range(3)
        ]
        db.session.add_all(violations)
        # Tasks
        tasks = [
            Task(driver_id=drivers[i%5].id, route_id=routes[i%5].id, vehicle_id=vehicles[i%5].id, status=TaskStatus.PENDING, start_time=datetime.now()-timedelta(days=i), end_time=datetime.now()-timedelta(days=i-1), notes=f"Задача {i+1}")
            for i in range(5)
        ]
        db.session.add_all(tasks)
        # WorkHours
        work_hours = [
            WorkHours(driver_id=drivers[i%5].id, date=datetime.now()-timedelta(days=i), start_time=datetime.now()-timedelta(days=i, hours=8), end_time=datetime.now()-timedelta(days=i, hours=0), total_hours=8.0)
            for i in range(5)
        ]
        db.session.add_all(work_hours)
        db.session.commit()
        print("База успешно заполнена тестовыми данными!")

if __name__ == '__main__':
    seed() 