import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import db


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    license_number = Column(String)
    license_expiry = Column(DateTime)
    contact_info = Column(String)
    status = Column(String)

    tasks = relationship('Task', backref='driver')
    work_hours = relationship('WorkHours', backref='driver')

    def __repr__(self):
        return f'<Driver {self.name}>'


class Route(db.Model):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer)
    driver_id = Column(Integer)
    start_location = Column(String)
    end_location = Column(String)
    distance = Column(Float)
    estimated_time = Column(Float)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    start_lat = Column(Float)
    start_lon = Column(Float)
    end_lat = Column(Float)
    end_lon = Column(Float)

    tasks = relationship('Task', backref='route')

    def __repr__(self):
        return f'<Route {self.id}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    notes = Column(String(500))

    def __repr__(self):
        return f'<Task {self.id} for driver {self.driver_id}>'


class WorkHours(db.Model):
    __tablename__ = 'work_hours'

    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    total_hours = Column(Float)

    def __repr__(self):
        return f'<WorkHours {self.date} for driver {self.driver_id}>' 