"""Device manager for HOME-AI-AUTOMATION."""

import json
import logging
import threading
from datetime import UTC
from pathlib import Path
from typing import Any

from home_automation.core.config import Config
from home_automation.core.database import DatabaseManager

logger = logging.getLogger(__name__)


class Device:
    """Base device class."""

    def __init__(self, device_id: int, name: str, device_type: str, location: str):
        """Initialize device."""
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.location = location
        self.status = "offline"
        self.properties = {}

    def turn_on(self) -> dict[str, Any]:
        """Turn on the device."""
        self.status = "online"
        return {"success": True, "status": self.status}

    def turn_off(self) -> dict[str, Any]:
        """Turn off the device."""
        self.status = "offline"
        return {"success": True, "status": self.status}

    def get_status(self) -> dict[str, Any]:
        """Get device status."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "type": self.device_type,
            "location": self.location,
            "status": self.status,
            "properties": self.properties
        }


class SmartLight(Device):
    """Smart light device."""

    def __init__(self, device_id: int, name: str, location: str):
        """Initialize smart light."""
        super().__init__(device_id, name, "light", location)
        self.properties = {
            "brightness": 100,
            "color": "#FFFFFF",
            "dimmable": True
        }

    def set_brightness(self, brightness: int) -> dict[str, Any]:
        """Set light brightness."""
        if 0 <= brightness <= 100:
            self.properties["brightness"] = brightness
            return {"success": True, "brightness": brightness}
        return {"success": False, "message": "Brightness must be between 0 and 100"}

    def set_color(self, color: str) -> dict[str, Any]:
        """Set light color."""
        self.properties["color"] = color
        return {"success": True, "color": color}


class SmartThermostat(Device):
    """Smart thermostat device."""

    def __init__(self, device_id: int, name: str, location: str):
        """Initialize smart thermostat."""
        super().__init__(device_id, name, "thermostat", location)
        self.properties = {
            "target_temperature": 22.0,
            "current_temperature": 22.0,
            "mode": "auto",
            "heating": False,
            "cooling": False
        }

    def set_temperature(self, temperature: float) -> dict[str, Any]:
        """Set target temperature."""
        if 10 <= temperature <= 35:
            self.properties["target_temperature"] = temperature
            return {"success": True, "target_temperature": temperature}
        return {"success": False, "message": "Temperature must be between 10 and 35 degrees"}

    def set_mode(self, mode: str) -> dict[str, Any]:
        """Set thermostat mode."""
        valid_modes = ["heat", "cool", "auto", "off"]
        if mode in valid_modes:
            self.properties["mode"] = mode
            return {"success": True, "mode": mode}
        return {"success": False, "message": f"Mode must be one of: {valid_modes}"}


class SmartSensor(Device):
    """Smart sensor device."""

    def __init__(self, device_id: int, name: str, location: str, sensor_type: str):
        """Initialize smart sensor."""
        super().__init__(device_id, name, "sensor", location)
        self.sensor_type = sensor_type
        self.properties = {
            "sensor_type": sensor_type,
            "value": 0.0,
            "unit": self._get_default_unit(sensor_type),
            "last_reading": None
        }

    def _get_default_unit(self, sensor_type: str) -> str:
        """Get default unit for sensor type."""
        units = {
            "temperature": "°C",
            "humidity": "%",
            "pressure": "hPa",
            "light": "lux",
            "motion": "boolean",
            "door": "boolean"
        }
        return units.get(sensor_type, "")

    def update_reading(self, value: float) -> dict[str, Any]:
        """Update sensor reading."""
        from datetime import datetime
        self.properties["value"] = value
        self.properties["last_reading"] = datetime.now(UTC).isoformat()
        return {"success": True, "value": value, "timestamp": self.properties["last_reading"]}


class DeviceManager:
    """Manager for all home automation devices."""

    def __init__(self, config: Config, db_manager: DatabaseManager):
        """Initialize device manager."""
        self.config = config
        self.db_manager = db_manager
        self.devices = {}
        self.running = False
        self.manager_thread = None

        # Load device configuration
        self._load_device_config()

        logger.info("Device manager initialized")

    def _load_device_config(self) -> None:
        """Load device configuration from file."""
        config_path = Path(self.config.DEVICES_CONFIG_PATH)

        if config_path.exists():
            try:
                with open(config_path) as f:
                    device_config = json.load(f)

                for device_info in device_config.get("devices", []):
                    self._create_device_from_config(device_info)

                logger.info(f"Loaded {len(self.devices)} devices from configuration")

            except Exception as e:
                logger.error(f"Failed to load device configuration: {e}")
        else:
            # Create default configuration
            self._create_default_devices()
            self._save_device_config()

    def _create_device_from_config(self, device_info: dict[str, Any]) -> None:
        """Create a device from configuration."""
        device_type = device_info.get("type")
        name = device_info.get("name")
        location = device_info.get("location")

        # Add to database if not exists
        device_id = self.db_manager.add_device(name, device_type, location, device_info)

        # Create device object
        if device_type == "light":
            device = SmartLight(device_id, name, location)
        elif device_type == "thermostat":
            device = SmartThermostat(device_id, name, location)
        elif device_type == "sensor":
            sensor_type = device_info.get("sensor_type", "temperature")
            device = SmartSensor(device_id, name, location, sensor_type)
        else:
            device = Device(device_id, name, device_type, location)

        self.devices[name.lower()] = device

    def _create_default_devices(self) -> None:
        """Create default devices."""
        default_devices = [
            {"name": "Living Room Light", "type": "light", "location": "Living Room"},
            {"name": "Bedroom Light", "type": "light", "location": "Bedroom"},
            {"name": "Main Thermostat", "type": "thermostat", "location": "Living Room"},
            {"name": "Temperature Sensor", "type": "sensor", "location": "Living Room", "sensor_type": "temperature"},
            {"name": "Humidity Sensor", "type": "sensor", "location": "Living Room", "sensor_type": "humidity"},
        ]

        for device_info in default_devices:
            self._create_device_from_config(device_info)

    def _save_device_config(self) -> None:
        """Save device configuration to file."""
        config_path = Path(self.config.DEVICES_CONFIG_PATH)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        device_config = {
            "devices": [
                {
                    "name": device.name,
                    "type": device.device_type,
                    "location": device.location,
                    **({"sensor_type": device.sensor_type} if hasattr(device, "sensor_type") else {})
                }
                for device in self.devices.values()
            ]
        }

        try:
            with open(config_path, 'w') as f:
                json.dump(device_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save device configuration: {e}")

    def start(self) -> None:
        """Start device manager."""
        self.running = True
        self.manager_thread = threading.Thread(target=self._run_manager, daemon=True)
        self.manager_thread.start()
        logger.info("Device manager started")

    def stop(self) -> None:
        """Stop device manager."""
        self.running = False
        if self.manager_thread and self.manager_thread.is_alive():
            self.manager_thread.join(timeout=5)
        logger.info("Device manager stopped")

    def _run_manager(self) -> None:
        """Main manager loop."""
        import time
        while self.running:
            try:
                # Update device statuses in database
                for device in self.devices.values():
                    self.db_manager.update_device_status(device.device_id, device.status)

                time.sleep(30)  # Update every 30 seconds

            except Exception as e:
                logger.error(f"Error in device manager loop: {e}")
                time.sleep(60)

    def get_device(self, name: str) -> Device | None:
        """Get device by name."""
        return self.devices.get(name.lower())

    def turn_on_device(self, name: str) -> dict[str, Any]:
        """Turn on a device."""
        device = self.get_device(name)
        if device:
            return device.turn_on()
        return {"success": False, "message": f"Device '{name}' not found"}

    def turn_off_device(self, name: str) -> dict[str, Any]:
        """Turn off a device."""
        device = self.get_device(name)
        if device:
            return device.turn_off()
        return {"success": False, "message": f"Device '{name}' not found"}

    def set_temperature(self, name: str, temperature: float) -> dict[str, Any]:
        """Set temperature for a thermostat."""
        device = self.get_device(name)
        if device and isinstance(device, SmartThermostat):
            return device.set_temperature(temperature)
        elif device:
            return {"success": False, "message": f"Device '{name}' is not a thermostat"}
        return {"success": False, "message": f"Device '{name}' not found"}

    def get_device_status(self, name: str) -> dict[str, Any]:
        """Get device status."""
        device = self.get_device(name)
        if device:
            return {"success": True, **device.get_status()}
        return {"success": False, "message": f"Device '{name}' not found"}

    def get_all_devices(self) -> list[dict[str, Any]]:
        """Get all devices."""
        return [device.get_status() for device in self.devices.values()]
