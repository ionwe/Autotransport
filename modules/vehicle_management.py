from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from database import db


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    registration_number = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    technical_specs = Column(String)
    current_status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    vehicle_type = Column(String(32))  

class FuelRecord(db.Model):
    __tablename__ = 'fuel_records'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, nullable=False)
    fuel_type = Column(String)
    amount = Column(Float)
    cost = Column(Float)
    date = Column(DateTime)
    mileage = Column(Float)


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, nullable=False)
    maintenance_type = Column(String)
    description = Column(String)
    cost = Column(Float)
    date = Column(DateTime)
    next_maintenance_date = Column(Date)
    parts_used = Column(String)
    created_at = Column(DateTime)


class SparePart(db.Model):
    __tablename__ = 'spare_parts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    part_number = Column(String)
    quantity = Column(Integer)
    min_quantity = Column(Integer)
    cost = Column(Float)
    supplier = Column(String)
    last_order_date = Column(Date)


class OwnershipHistory(db.Model):
    __tablename__ = 'vehicle_ownership'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, nullable=False)
    owner_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    documents = Column(String)

    def __repr__(self):
        return f'<OwnershipHistory {self.owner_name} for {self.vehicle_id}>' 