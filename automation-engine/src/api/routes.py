"""API routes for HOME-AI-AUTOMATION."""

import logging

from flask import Flask, render_template, request
from flask_cors import CORS
from flask_restful import Api, Resource

from home_automation.core.automation_engine import AutomationEngine
from home_automation.api.integration_routes import (
    HomeAssistantConnection,
    HomeAssistantStates,
    HomeAssistantControl,
    RemoteDeviceList,
    RemoteDeviceControl,
    MobileDeviceList,
    MobileDeviceConnection,
    MobileNotification,
    AIProviderStatus,
    ProxmoxConnection,
    ProxmoxNodes,
    ProxmoxResources,
    ProxmoxVMControl,
    ProxmoxContainerControl,
    WebhookHandler,
)

logger = logging.getLogger(__name__)


def rate_limit(limit_string: str):
    """Decorator for rate limiting."""
    def decorator(f):
        # This will be applied by the limiter in the route setup
        f._rate_limit = limit_string
        return f
    return decorator


class HealthCheck(Resource):
    """Health check endpoint."""

    def get(self):
        """Get health status."""
        return {"status": "healthy", "service": "HOME-AI-AUTOMATION"}


class SystemStatus(Resource):
    """System status endpoint."""

    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine

    def get(self):
        """Get system status."""
        return self.automation_engine.get_system_status()


class DeviceList(Resource):
    """Device list endpoint."""

    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine

    def get(self):
        """Get all devices."""
        devices = self.automation_engine.device_manager.get_all_devices()
        return {"devices": devices}


class DeviceControl(Resource):
    """Device control endpoint."""

    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine

    def post(self, device_name):
        """Control a device."""
        data = request.get_json() or {}
        action = data.get("action")
        parameters = data.get("parameters", {})

        if action == "turn_on":
            result = self.automation_engine.device_manager.turn_on_device(device_name)
        elif action == "turn_off":
            result = self.automation_engine.device_manager.turn_off_device(device_name)
        elif action == "set_temperature":
            temperature = parameters.get("temperature")
            if temperature is None:
                return {"success": False, "message": "Temperature parameter required"}, 400
            result = self.automation_engine.device_manager.set_temperature(device_name, temperature)
        else:
            return {"success": False, "message": f"Unknown action: {action}"}, 400

        return result

    def get(self, device_name):
        """Get device status."""
        result = self.automation_engine.device_manager.get_device_status(device_name)
        return result


class CommandExecutor(Resource):
    """Natural language command executor."""

    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine

    def post(self):
        """Execute a natural language command."""
        # Apply rate limiting for command execution
        data = request.get_json() or {}
        command = data.get("command")

        if not command:
            return {"success": False, "message": "Command is required"}, 400

        # Validate command length
        if len(command) > 500:
            return {"success": False, "message": "Command too long (max 500 characters)"}, 400

        result = self.automation_engine.execute_command(command)

        # Generate AI response
        if result.get("success"):
            response_text = self.automation_engine.ai_intelligence.generate_response(result)
            result["response"] = response_text

        return result


class SensorData(Resource):
    """Sensor data endpoint."""

    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine

    def get(self, device_id):
        """Get sensor data for a device."""
        try:
            device_id = int(device_id)
            data = self.automation_engine.db_manager.get_recent_sensor_data(device_id)

            # Get AI analysis
            analysis = self.automation_engine.ai_intelligence.analyze_sensor_data(data)

            return {
                "device_id": device_id,
                "sensor_data": data,
                "analysis": analysis
            }
        except ValueError:
            return {"success": False, "message": "Invalid device ID"}, 400

    def post(self, device_id):
        """Add sensor data."""
        try:
            device_id = int(device_id)
            data = request.get_json() or {}

            sensor_type = data.get("sensor_type")
            value = data.get("value")
            unit = data.get("unit")

            if sensor_type is None or value is None:
                return {"success": False, "message": "sensor_type and value are required"}, 400

            self.automation_engine.db_manager.add_sensor_data(device_id, sensor_type, value, unit)

            return {"success": True, "message": "Sensor data added"}

        except ValueError:
            return {"success": False, "message": "Invalid device ID"}, 400


def create_api_routes(app: Flask, automation_engine: AutomationEngine) -> None:
    """Create API routes."""
    # Enable CORS
    CORS(app)

    # Create API
    api = Api(app)

    # Get limiter if available
    limiter = getattr(app, 'limiter', None)

    # Add routes
    api.add_resource(HealthCheck, "/api/health")
    api.add_resource(
        SystemStatus, "/api/status",
        resource_class_kwargs={"automation_engine": automation_engine}
    )
    api.add_resource(
        DeviceList, "/api/devices",
        resource_class_kwargs={"automation_engine": automation_engine}
    )
    api.add_resource(
        DeviceControl, "/api/devices/<string:device_name>",
        resource_class_kwargs={"automation_engine": automation_engine}
    )

    # Apply rate limiting to command endpoint
    command_resource = api.add_resource(
        CommandExecutor, "/api/command",
        resource_class_kwargs={"automation_engine": automation_engine}
    )
    if limiter:
        limiter.limit("10 per minute")(CommandExecutor.post)

    api.add_resource(
        SensorData, "/api/sensors/<string:device_id>",
        resource_class_kwargs={"automation_engine": automation_engine}
    )

    # Home Assistant integration routes
    if automation_engine.ha_client:
        api.add_resource(
            HomeAssistantConnection, "/api/homeassistant/connection",
            resource_class_kwargs={"ha_client": automation_engine.ha_client}
        )
        api.add_resource(
            HomeAssistantStates, "/api/homeassistant/states",
            resource_class_kwargs={"ha_client": automation_engine.ha_client}
        )
        api.add_resource(
            HomeAssistantControl, "/api/homeassistant/control/<string:entity_id>",
            resource_class_kwargs={"ha_client": automation_engine.ha_client}
        )

    # Remote control routes
    api.add_resource(
        RemoteDeviceList, "/api/remote/devices",
        resource_class_kwargs={"remote_manager": automation_engine.remote_manager}
    )
    api.add_resource(
        RemoteDeviceControl, "/api/remote/control/<string:device_name>",
        resource_class_kwargs={"remote_manager": automation_engine.remote_manager}
    )

    # Mobile device routes
    api.add_resource(
        MobileDeviceList, "/api/mobile/devices",
        resource_class_kwargs={"mobile_manager": automation_engine.mobile_manager}
    )
    api.add_resource(
        MobileDeviceConnection, "/api/mobile/connection/<string:device_id>",
        resource_class_kwargs={"mobile_manager": automation_engine.mobile_manager}
    )
    api.add_resource(
        MobileNotification, "/api/mobile/notify/<string:device_id>",
        resource_class_kwargs={"mobile_manager": automation_engine.mobile_manager}
    )

    # AI provider status route
    if automation_engine.multi_ai_provider:
        api.add_resource(
            AIProviderStatus, "/api/ai/status",
            resource_class_kwargs={"multi_ai_provider": automation_engine.multi_ai_provider}
        )

    # Proxmox VE routes
    if automation_engine.proxmox_client:
        api.add_resource(
            ProxmoxConnection, "/api/proxmox/connection",
            resource_class_kwargs={"proxmox_client": automation_engine.proxmox_client}
        )
        api.add_resource(
            ProxmoxNodes, "/api/proxmox/nodes",
            resource_class_kwargs={"proxmox_client": automation_engine.proxmox_client}
        )
        api.add_resource(
            ProxmoxResources, "/api/proxmox/resources",
            resource_class_kwargs={"proxmox_client": automation_engine.proxmox_client}
        )
        api.add_resource(
            ProxmoxVMControl, "/api/proxmox/vm/<int:vmid>",
            resource_class_kwargs={
                "proxmox_client": automation_engine.proxmox_client,
                "default_node": automation_engine.config.PROXMOX_NODE
            }
        )
        api.add_resource(
            ProxmoxContainerControl, "/api/proxmox/container/<int:vmid>",
            resource_class_kwargs={
                "proxmox_client": automation_engine.proxmox_client,
                "default_node": automation_engine.config.PROXMOX_NODE
            }
        )

    # Webhook handler
    api.add_resource(
        WebhookHandler, "/api/webhook/<string:webhook_id>",
        resource_class_kwargs={
            "automation_engine": automation_engine,
            "webhook_secret": automation_engine.config.WEBHOOK_SECRET
        }
    )

    # Web interface routes
    @app.route("/")
    def index():
        """Main dashboard."""
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        """Dashboard page."""
        return render_template("dashboard.html")

    @app.route("/remote")
    def remote_control():
        """Remote control page."""
        return render_template("remote_control.html")

    @app.route("/mobile")
    def mobile_setup():
        """Mobile device setup page."""
        return render_template("mobile_setup.html")

    logger.info("API routes created successfully")
