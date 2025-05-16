from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from database import db


class GPSData(db.Model):
    __tablename__ = 'gps_data'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float)
    heading = Column(Float)

    def __repr__(self):
        return f'<GPSData {self.timestamp} for vehicle {self.vehicle_id}>'


class FuelConsumption(db.Model):
    __tablename__ = 'fuel_consumption'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    consumption_rate = Column(Float, nullable=False)  
    current_level = Column(Float, nullable=False)  

    def __repr__(self):
        return f'<FuelConsumption {self.timestamp} for vehicle {self.vehicle_id}>'


class DrivingStyle(db.Model):
    __tablename__ = 'driving_style'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    acceleration_score = Column(Float)  
    braking_score = Column(Float)  
    cornering_score = Column(Float)  
    overall_score = Column(Float)  

    def __repr__(self):
        return f'<DrivingStyle {self.timestamp} for driver {self.driver_id}>'


class Violation(db.Model):
    __tablename__ = 'violations'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    violation_type = Column(String(50), nullable=False)
    details = Column(JSON)
    location = Column(String(200))

    def __repr__(self):
        return f'<Violation {self.violation_type} for driver {self.driver_id}>'


class TrackingData(db.Model):
    __tablename__ = 'tracking_data'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer)
    route_id = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    fuel_level = Column(Float)
    timestamp = Column(DateTime)
    additional_data = Column(String) 