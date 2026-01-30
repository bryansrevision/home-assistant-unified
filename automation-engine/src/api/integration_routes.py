"""Additional API routes for new integrations."""

import logging

from flask_restful import Resource
from flask import request

logger = logging.getLogger(__name__)


class HomeAssistantConnection(Resource):
    """Home Assistant connection endpoint."""

    def __init__(self, ha_client):
        self.ha_client = ha_client

    def get(self):
        """Test Home Assistant connection."""
        if not self.ha_client:
            return {"success": False, "message": "Home Assistant client not configured"}, 503
        
        return self.ha_client.test_connection()


class HomeAssistantStates(Resource):
    """Home Assistant states endpoint."""

    def __init__(self, ha_client):
        self.ha_client = ha_client

    def get(self):
        """Get all entity states from Home Assistant."""
        if not self.ha_client:
            return {"success": False, "message": "Home Assistant client not configured"}, 503
        
        states = self.ha_client.get_states()
        return {"success": True, "states": states}


class HomeAssistantControl(Resource):
    """Home Assistant entity control endpoint."""

    def __init__(self, ha_client):
        self.ha_client = ha_client

    def post(self, entity_id):
        """Control a Home Assistant entity."""
        if not self.ha_client:
            return {"success": False, "message": "Home Assistant client not configured"}, 503
        
        data = request.get_json() or {}
        action = data.get("action")
        
        if action == "turn_on":
            return self.ha_client.turn_on(entity_id, **data.get("parameters", {}))
        elif action == "turn_off":
            return self.ha_client.turn_off(entity_id, **data.get("parameters", {}))
        elif action == "toggle":
            return self.ha_client.toggle(entity_id, **data.get("parameters", {}))
        else:
            return {"success": False, "message": f"Unknown action: {action}"}, 400

    def get(self, entity_id):
        """Get state of a Home Assistant entity."""
        if not self.ha_client:
            return {"success": False, "message": "Home Assistant client not configured"}, 503
        
        state = self.ha_client.get_state(entity_id)
        if state:
            return {"success": True, "state": state}
        else:
            return {"success": False, "message": "Entity not found"}, 404


class RemoteDeviceList(Resource):
    """Remote device list endpoint."""

    def __init__(self, remote_manager):
        self.remote_manager = remote_manager

    def get(self):
        """Get all remote controllable devices."""
        devices = self.remote_manager.get_all_devices()
        return {"success": True, "devices": devices}


class RemoteDeviceControl(Resource):
    """Remote device control endpoint."""

    def __init__(self, remote_manager):
        self.remote_manager = remote_manager

    def post(self, device_name):
        """Send command to remote device."""
        data = request.get_json() or {}
        command = data.get("command")
        
        if not command:
            return {"success": False, "message": "Command is required"}, 400
        
        result = self.remote_manager.send_command(device_name, command)
        return result

    def get(self, device_name):
        """Get remote device status."""
        result = self.remote_manager.get_device_status(device_name)
        return result


class MobileDeviceList(Resource):
    """Mobile device list endpoint."""

    def __init__(self, mobile_manager):
        self.mobile_manager = mobile_manager

    def get(self):
        """Get all mobile devices."""
        devices = self.mobile_manager.get_all_devices()
        return {"success": True, "devices": devices}


class MobileDeviceConnection(Resource):
    """Mobile device connection endpoint."""

    def __init__(self, mobile_manager):
        self.mobile_manager = mobile_manager

    def post(self, device_id):
        """Test connection to mobile device."""
        result = self.mobile_manager.test_connection(device_id)
        return result

    def get(self, device_id):
        """Get mobile device info."""
        result = self.mobile_manager.get_device_info(device_id)
        return result


class MobileNotification(Resource):
    """Mobile notification endpoint."""

    def __init__(self, mobile_manager):
        self.mobile_manager = mobile_manager

    def post(self, device_id):
        """Send notification to mobile device."""
        data = request.get_json() or {}
        title = data.get("title", "")
        message = data.get("message", "")
        
        if not title or not message:
            return {"success": False, "message": "Title and message are required"}, 400
        
        result = self.mobile_manager.send_notification(device_id, title, message)
        return result


class AIProviderStatus(Resource):
    """AI provider status endpoint."""

    def __init__(self, multi_ai_provider):
        self.multi_ai_provider = multi_ai_provider

    def get(self):
        """Get status of all AI providers."""
        if not self.multi_ai_provider:
            return {"success": False, "message": "Multi-AI provider not configured"}, 503
        
        connections = self.multi_ai_provider.test_connections()
        providers = self.multi_ai_provider.get_available_providers()
        
        return {
            "success": True,
            "available_providers": providers,
            "connection_status": connections
        }


class ProxmoxConnection(Resource):
    """Proxmox VE connection endpoint."""

    def __init__(self, proxmox_client):
        self.proxmox_client = proxmox_client

    def get(self):
        """Test Proxmox VE connection."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        return self.proxmox_client.test_connection()


class ProxmoxNodes(Resource):
    """Proxmox VE nodes endpoint."""

    def __init__(self, proxmox_client):
        self.proxmox_client = proxmox_client

    def get(self):
        """Get all nodes in the cluster."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        nodes = self.proxmox_client.get_nodes()
        return {"success": True, "nodes": nodes}


class ProxmoxResources(Resource):
    """Proxmox VE resources endpoint."""

    def __init__(self, proxmox_client):
        self.proxmox_client = proxmox_client

    def get(self):
        """Get all cluster resources."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        resources = self.proxmox_client.get_cluster_resources()
        return {"success": True, "resources": resources}


class ProxmoxVMControl(Resource):
    """Proxmox VE VM control endpoint."""

    def __init__(self, proxmox_client, default_node):
        self.proxmox_client = proxmox_client
        self.default_node = default_node

    def post(self, vmid):
        """Control a VM (start/stop/restart)."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        data = request.get_json() or {}
        action = data.get("action")
        node = data.get("node", self.default_node)
        
        if not node:
            return {"success": False, "message": "Node parameter required"}, 400
        
        if action == "start":
            return self.proxmox_client.start_vm(node, int(vmid))
        elif action == "stop":
            return self.proxmox_client.stop_vm(node, int(vmid))
        elif action == "restart":
            return self.proxmox_client.restart_vm(node, int(vmid))
        else:
            return {"success": False, "message": f"Unknown action: {action}"}, 400

    def get(self, vmid):
        """Get VM status."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        node = request.args.get("node", self.default_node)
        if not node:
            return {"success": False, "message": "Node parameter required"}, 400
        
        status = self.proxmox_client.get_vm_status(node, int(vmid))
        if status:
            return {"success": True, "status": status}
        else:
            return {"success": False, "message": "VM not found"}, 404


class ProxmoxContainerControl(Resource):
    """Proxmox VE container control endpoint."""

    def __init__(self, proxmox_client, default_node):
        self.proxmox_client = proxmox_client
        self.default_node = default_node

    def post(self, vmid):
        """Control a container (start/stop)."""
        if not self.proxmox_client:
            return {"success": False, "message": "Proxmox VE client not configured"}, 503
        
        data = request.get_json() or {}
        action = data.get("action")
        node = data.get("node", self.default_node)
        
        if not node:
            return {"success": False, "message": "Node parameter required"}, 400
        
        if action == "start":
            return self.proxmox_client.start_container(node, int(vmid))
        elif action == "stop":
            return self.proxmox_client.stop_container(node, int(vmid))
        else:
            return {"success": False, "message": f"Unknown action: {action}"}, 400


class WebhookHandler(Resource):
    """Webhook handler for Home Assistant and external services."""

    def __init__(self, automation_engine, webhook_secret):
        self.automation_engine = automation_engine
        self.webhook_secret = webhook_secret

    def post(self, webhook_id):
        """Handle webhook POST request."""
        data = request.get_json() or {}
        
        # Validate webhook if secret is configured
        if self.webhook_secret:
            provided_secret = request.headers.get("X-Webhook-Secret")
            if provided_secret != self.webhook_secret:
                logger.warning(f"Webhook authentication failed for {webhook_id}")
                return {"success": False, "message": "Unauthorized"}, 401
        
        logger.info(f"Received webhook: {webhook_id}")
        logger.debug(f"Webhook data: {data}")
        
        # Process webhook data
        # This can be extended to trigger automations, send notifications, etc.
        
        return {
            "success": True,
            "message": f"Webhook {webhook_id} received",
            "webhook_id": webhook_id
        }
