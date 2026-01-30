"""Proxmox VE integration for HOME-AI-AUTOMATION."""

import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class ProxmoxVEClient:
    """Client for interacting with Proxmox VE API."""

    def __init__(
        self,
        host: str,
        port: int = 8006,
        verify_ssl: bool = False,
        timeout: int = 10,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token_id: Optional[str] = None,
        token_secret: Optional[str] = None
    ):
        """Initialize Proxmox VE client.

        Args:
            host: Proxmox VE host (IP or hostname)
            port: Proxmox VE port (default: 8006)
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            username: Username for password authentication (e.g., root@pam)
            password: Password for authentication
            token_id: API token ID for token authentication (e.g., root@pam!mytoken)
            token_secret: API token secret
        """
        self.base_url = f"https://{host}:{port}/api2/json"
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.username = username
        self.password = password
        self.token_id = token_id
        self.token_secret = token_secret
        self.ticket = None
        self.csrf_token = None
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication.

        Returns:
            Dictionary of headers
        """
        headers = {"Content-Type": "application/json"}
        
        if self.token_id and self.token_secret:
            # Token-based authentication
            headers["Authorization"] = f"PVEAPIToken={self.token_id}={self.token_secret}"
        elif self.ticket and self.csrf_token:
            # Ticket-based authentication
            headers["Cookie"] = f"PVEAuthCookie={self.ticket}"
            headers["CSRFPreventionToken"] = self.csrf_token
            
        return headers

    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Proxmox VE using username/password.

        Returns:
            Authentication result
        """
        if not self.username or not self.password:
            return {
                "success": False,
                "message": "Username and password required for authentication"
            }

        try:
            response = self.session.post(
                f"{self.base_url}/access/ticket",
                data={
                    "username": self.username,
                    "password": self.password
                },
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()["data"]
            
            self.ticket = data["ticket"]
            self.csrf_token = data["CSRFPreventionToken"]
            
            logger.info(f"Successfully authenticated with Proxmox VE as {self.username}")
            return {
                "success": True,
                "message": "Authentication successful"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Proxmox VE: {e}")
            return {
                "success": False,
                "message": f"Authentication failed: {str(e)}",
                "error": str(e)
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Proxmox VE.

        Returns:
            Connection test result
        """
        try:
            response = self.session.get(
                f"{self.base_url}/version",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()["data"]
            
            logger.info(f"Successfully connected to Proxmox VE version {data.get('version', 'unknown')}")
            return {
                "success": True,
                "message": "Connected to Proxmox VE",
                "version": data.get("version"),
                "release": data.get("release")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Proxmox VE: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "error": str(e)
            }

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get list of nodes in the cluster.

        Returns:
            List of node information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nodes",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get nodes: {e}")
            return []

    def get_vms(self, node: str) -> List[Dict[str, Any]]:
        """Get list of VMs on a node.

        Args:
            node: Node name

        Returns:
            List of VM information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nodes/{node}/qemu",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get VMs for node {node}: {e}")
            return []

    def get_containers(self, node: str) -> List[Dict[str, Any]]:
        """Get list of containers on a node.

        Args:
            node: Node name

        Returns:
            List of container information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nodes/{node}/lxc",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get containers for node {node}: {e}")
            return []

    def get_vm_status(self, node: str, vmid: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            VM status information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/current",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get VM status for {vmid} on {node}: {e}")
            return None

    def start_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Start a VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Operation result
        """
        try:
            response = self.session.post(
                f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/start",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Started VM {vmid} on node {node}")
            return {
                "success": True,
                "message": f"VM {vmid} start initiated",
                "data": response.json()["data"]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start VM {vmid}: {e}")
            return {
                "success": False,
                "message": f"Failed to start VM: {str(e)}",
                "error": str(e)
            }

    def stop_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Stop a VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Operation result
        """
        try:
            response = self.session.post(
                f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/stop",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Stopped VM {vmid} on node {node}")
            return {
                "success": True,
                "message": f"VM {vmid} stop initiated",
                "data": response.json()["data"]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to stop VM {vmid}: {e}")
            return {
                "success": False,
                "message": f"Failed to stop VM: {str(e)}",
                "error": str(e)
            }

    def restart_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Restart a VM.

        Args:
            node: Node name
            vmid: VM ID

        Returns:
            Operation result
        """
        try:
            response = self.session.post(
                f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/reboot",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Restarted VM {vmid} on node {node}")
            return {
                "success": True,
                "message": f"VM {vmid} restart initiated",
                "data": response.json()["data"]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to restart VM {vmid}: {e}")
            return {
                "success": False,
                "message": f"Failed to restart VM: {str(e)}",
                "error": str(e)
            }

    def start_container(self, node: str, vmid: int) -> Dict[str, Any]:
        """Start a container.

        Args:
            node: Node name
            vmid: Container ID

        Returns:
            Operation result
        """
        try:
            response = self.session.post(
                f"{self.base_url}/nodes/{node}/lxc/{vmid}/status/start",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Started container {vmid} on node {node}")
            return {
                "success": True,
                "message": f"Container {vmid} start initiated",
                "data": response.json()["data"]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start container {vmid}: {e}")
            return {
                "success": False,
                "message": f"Failed to start container: {str(e)}",
                "error": str(e)
            }

    def stop_container(self, node: str, vmid: int) -> Dict[str, Any]:
        """Stop a container.

        Args:
            node: Node name
            vmid: Container ID

        Returns:
            Operation result
        """
        try:
            response = self.session.post(
                f"{self.base_url}/nodes/{node}/lxc/{vmid}/status/stop",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Stopped container {vmid} on node {node}")
            return {
                "success": True,
                "message": f"Container {vmid} stop initiated",
                "data": response.json()["data"]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to stop container {vmid}: {e}")
            return {
                "success": False,
                "message": f"Failed to stop container: {str(e)}",
                "error": str(e)
            }

    def get_node_status(self, node: str) -> Optional[Dict[str, Any]]:
        """Get status of a node.

        Args:
            node: Node name

        Returns:
            Node status information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/nodes/{node}/status",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get node status for {node}: {e}")
            return None

    def get_cluster_resources(self) -> List[Dict[str, Any]]:
        """Get all cluster resources (nodes, VMs, containers).

        Returns:
            List of all cluster resources
        """
        try:
            response = self.session.get(
                f"{self.base_url}/cluster/resources",
                headers=self._get_headers(),
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get cluster resources: {e}")
            return []
