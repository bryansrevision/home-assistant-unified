"""Database management for HOME-AI-AUTOMATION."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)
Base = declarative_base()


class Device(Base):
    """Device model."""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(20), default="offline")
    last_seen = Column(DateTime, default=lambda: datetime.now(UTC))
    properties = Column(Text)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))


class AutomationRule(Base):
    """Automation rule model."""
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False)
    trigger_conditions = Column(Text)  # JSON string
    actions = Column(Text)  # JSON string
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    last_executed = Column(DateTime)


class SensorData(Base):
    """Sensor data model."""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, nullable=False)
    sensor_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))


class DatabaseManager:
    """Database manager for HOME-AI-AUTOMATION."""

    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.database_url = database_url
        self.engine = None
        self.session_maker = None

    def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            # Create database directory if using SQLite
            if self.database_url.startswith("sqlite:"):
                db_path = self.database_url.replace("sqlite:///", "")
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)

            # Create engine
            self.engine = create_engine(self.database_url)
            self.session_maker = sessionmaker(bind=self.engine)

            # Create tables
            Base.metadata.create_all(self.engine)

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session."""
        if not self.session_maker:
            raise RuntimeError("Database not initialized")
        return self.session_maker()

    def add_device(self, name: str, device_type: str, location: str, properties: dict[str, Any] = None) -> int:
        """Add a new device."""
        with self.get_session() as session:
            device = Device(
                name=name,
                device_type=device_type,
                location=location,
                properties=str(properties or {})
            )
            session.add(device)
            session.commit()
            session.refresh(device)
            return device.id

    def get_devices(self) -> list[dict[str, Any]]:
        """Get all devices."""
        with self.get_session() as session:
            devices = session.query(Device).all()
            return [
                {
                    "id": d.id,
                    "name": d.name,
                    "device_type": d.device_type,
                    "location": d.location,
                    "status": d.status,
                    "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                    "properties": d.properties,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in devices
            ]

    def update_device_status(self, device_id: int, status: str) -> None:
        """Update device status."""
        with self.get_session() as session:
            device = session.query(Device).filter(Device.id == device_id).first()
            if device:
                device.status = status
                device.last_seen = datetime.now(UTC)
                session.commit()

    def add_sensor_data(self, device_id: int, sensor_type: str, value: float, unit: str = None) -> None:
        """Add sensor data."""
        with self.get_session() as session:
            sensor_data = SensorData(
                device_id=device_id,
                sensor_type=sensor_type,
                value=value,
                unit=unit
            )
            session.add(sensor_data)
            session.commit()

    def get_recent_sensor_data(self, device_id: int, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent sensor data for a device."""
        with self.get_session() as session:
            data = session.query(SensorData).filter(
                SensorData.device_id == device_id
            ).order_by(SensorData.timestamp.desc()).limit(limit).all()

            return [
                {
                    "id": d.id,
                    "sensor_type": d.sensor_type,
                    "value": d.value,
                    "unit": d.unit,
                    "timestamp": d.timestamp.isoformat() if d.timestamp else None
                }
                for d in data
            ]
