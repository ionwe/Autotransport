from datetime import datetime, timedelta
from sqlalchemy import func
from database import db
from modules.vehicle_management import Vehicle, FuelRecord, MaintenanceRecord
from modules.dispatch import Task
from modules.monitoring import FuelConsumption

class Analytics:
    @staticmethod
    def calculate_transportation_cost(vehicle_id, start_date, end_date):
        """Расчет себестоимости перевозок для конкретного ТС"""
        fuel_cost = db.session.query(func.sum(FuelRecord.cost)).filter(
            FuelRecord.vehicle_id == vehicle_id,
            FuelRecord.date.between(start_date, end_date)
        ).scalar() or 0

        maintenance_cost = db.session.query(func.sum(MaintenanceRecord.cost)).filter(
            MaintenanceRecord.vehicle_id == vehicle_id,
            MaintenanceRecord.date.between(start_date, end_date)
        ).scalar() or 0

        return {
            'fuel_cost': fuel_cost,
            'maintenance_cost': maintenance_cost,
            'total_cost': fuel_cost + maintenance_cost
        }

    @staticmethod
    def analyze_vehicle_efficiency(vehicle_id, start_date, end_date):
        """Анализ эффективности использования ТС"""
        tasks = Task.query.filter(
            Task.vehicle_id == vehicle_id,
            Task.start_time.between(start_date, end_date)
        ).all()

        total_distance = sum(task.route.distance for task in tasks)
        total_time = sum(task.route.estimated_time for task in tasks)

        fuel_consumption = FuelConsumption.query.filter(
            FuelConsumption.vehicle_id == vehicle_id,
            FuelConsumption.timestamp.between(start_date, end_date)
        ).all()

        avg_consumption = (
            sum(fc.consumption_rate for fc in fuel_consumption) / len(fuel_consumption)
            if fuel_consumption else 0
        )

        return {
            'total_distance': total_distance,
            'total_time': total_time,
            'average_fuel_consumption': avg_consumption,
            'tasks_completed': len(tasks)
        }

    @staticmethod
    def generate_regulatory_report(report_type, start_date, end_date):
        """Формирование регламентных отчетов"""
        if report_type == 'fuel':
            return db.session.query(
                Vehicle.registration_number,
                func.sum(FuelRecord.amount).label('total_fuel'),
                func.sum(FuelRecord.cost).label('total_cost')
            ).join(FuelRecord, Vehicle.id == FuelRecord.vehicle_id).filter(
                FuelRecord.date.between(start_date, end_date)
            ).group_by(Vehicle.registration_number).all()

        elif report_type == 'maintenance':
            return db.session.query(
                Vehicle.registration_number,
                func.count(MaintenanceRecord.id).label('maintenance_count'),
                func.sum(MaintenanceRecord.cost).label('total_cost')
            ).join(MaintenanceRecord).filter(
                MaintenanceRecord.date.between(start_date, end_date)
            ).group_by(Vehicle.registration_number).all()

    @staticmethod
    def predict_maintenance_needs(vehicle_id):
        """Прогнозный анализ потребностей в обслуживании"""
        last_maintenance = MaintenanceRecord.query.filter(
            MaintenanceRecord.vehicle_id == vehicle_id
        ).order_by(MaintenanceRecord.date.desc()).first()

        if not last_maintenance:
            return None

        maintenance_dates = db.session.query(MaintenanceRecord.date).filter(
            MaintenanceRecord.vehicle_id == vehicle_id
        ).order_by(MaintenanceRecord.date).all()

        if len(maintenance_dates) < 2:
            return None


        intervals = []
        for i in range(1, len(maintenance_dates)):
            interval = (maintenance_dates[i][0] - maintenance_dates[i - 1][0]).days
            intervals.append(interval)

        avg_interval = sum(intervals) / len(intervals)

        next_maintenance = last_maintenance.date + timedelta(days=avg_interval)
        return {
            'last_maintenance': last_maintenance.date,
            'predicted_next_maintenance': next_maintenance,
            'days_until_maintenance': (next_maintenance - datetime.now()).days
        } 