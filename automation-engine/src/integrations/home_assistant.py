"""Home Assistant integration for HOME-AI-AUTOMATION."""

import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant API."""

    def __init__(
        self,
        url: str,
        token: str,
        verify_ssl: bool = False,
        timeout: int = 10
    ):
        """Initialize Home Assistant client.

        Args:
            url: Home Assistant URL (e.g., http://192.168.1.134:8123)
            token: Long-lived access token
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip('/')
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Home Assistant.

        Returns:
            Dict with connection status and info
        """
        try:
            response = self.session.get(
                f"{self.url}/api/",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully connected to Home Assistant: {data.get('message', 'OK')}")
            return {
                "success": True,
                "message": "Connected to Home Assistant",
                "data": data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Home Assistant: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }

    def get_states(self) -> List[Dict[str, Any]]:
        """Get all entity states from Home Assistant.

        Returns:
            List of entity states
        """
        try:
            response = self.session.get(
                f"{self.url}/api/states",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get states: {e}")
            return []

    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get state of a specific entity.

        Args:
            entity_id: Entity ID (e.g., light.living_room)

        Returns:
            Entity state or None if not found
        """
        try:
            response = self.session.get(
                f"{self.url}/api/states/{entity_id}",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get state for {entity_id}: {e}")
            return None

    def call_service(
        self,
        domain: str,
        service: str,
        service_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a Home Assistant service.

        Args:
            domain: Service domain (e.g., light, switch)
            service: Service name (e.g., turn_on, turn_off)
            service_data: Optional service data

        Returns:
            Response from service call
        """
        try:
            response = self.session.post(
                f"{self.url}/api/services/{domain}/{service}",
                headers=self.headers,
                json=service_data or {},
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Successfully called service {domain}.{service}")
            return {
                "success": True,
                "message": f"Service {domain}.{service} called successfully",
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call service {domain}.{service}: {e}")
            return {
                "success": False,
                "message": f"Service call failed: {str(e)}",
                "error": str(e)
            }

    def turn_on(self, entity_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Turn on an entity.

        Args:
            entity_id: Entity ID to turn on
            **kwargs: Additional service data (brightness, color, etc.)

        Returns:
            Response from service call
        """
        domain = entity_id.split('.')[0]
        service_data = {"entity_id": entity_id, **kwargs}
        return self.call_service(domain, "turn_on", service_data)

    def turn_off(self, entity_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Turn off an entity.

        Args:
            entity_id: Entity ID to turn off
            **kwargs: Additional service data

        Returns:
            Response from service call
        """
        domain = entity_id.split('.')[0]
        service_data = {"entity_id": entity_id, **kwargs}
        return self.call_service(domain, "turn_off", service_data)

    def toggle(self, entity_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Toggle an entity.

        Args:
            entity_id: Entity ID to toggle
            **kwargs: Additional service data

        Returns:
            Response from service call
        """
        domain = entity_id.split('.')[0]
        service_data = {"entity_id": entity_id, **kwargs}
        return self.call_service(domain, "toggle", service_data)

    def set_temperature(self, entity_id: str, temperature: float) -> Dict[str, Any]:
        """Set temperature for a climate entity.

        Args:
            entity_id: Climate entity ID
            temperature: Target temperature

        Returns:
            Response from service call
        """
        service_data = {
            "entity_id": entity_id,
            "temperature": temperature
        }
        return self.call_service("climate", "set_temperature", service_data)

    def get_services(self) -> Dict[str, Any]:
        """Get all available services.

        Returns:
            Dictionary of available services
        """
        try:
            response = self.session.get(
                f"{self.url}/api/services",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get services: {e}")
            return {}

    def get_config(self) -> Dict[str, Any]:
        """Get Home Assistant configuration.

        Returns:
            Configuration dictionary
        """
        try:
            response = self.session.get(
                f"{self.url}/api/config",
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get config: {e}")
            return {}
