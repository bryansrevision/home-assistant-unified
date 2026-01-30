"""Core automation engine for HOME-AI-AUTOMATION."""

import json
import logging
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from home_automation.ai.intelligence import AIIntelligence
from home_automation.core.config import Config
from home_automation.core.database import DatabaseManager
from home_automation.devices.device_manager import DeviceManager
from home_automation.integrations.home_assistant import HomeAssistantClient
from home_automation.integrations.ai_providers import MultiAIProvider
from home_automation.integrations.remote_control import RemoteControlManager, RemoteDevice, DeviceType
from home_automation.integrations.mobile_device import MobileDeviceManager, MobileDevice, ConnectionMethod
from home_automation.integrations.proxmox import ProxmoxVEClient

logger = logging.getLogger(__name__)


class AutomationEngine:
    """Main automation engine that coordinates all home automation activities."""

    def __init__(self, config: Config, db_manager: DatabaseManager):
        """Initialize the automation engine."""
        self.config = config
        self.db_manager = db_manager
        self.device_manager = DeviceManager(config, db_manager)
        self.ai_intelligence = AIIntelligence(config)
        self.running = False
        self.engine_thread = None

        # Initialize Home Assistant client
        self.ha_client: Optional[HomeAssistantClient] = None
        if config.HOME_ASSISTANT_TOKEN:
            try:
                self.ha_client = HomeAssistantClient(
                    url=config.HOME_ASSISTANT_URL,
                    token=config.HOME_ASSISTANT_TOKEN,
                    verify_ssl=config.HOME_ASSISTANT_VERIFY_SSL
                )
                logger.info("Home Assistant client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Home Assistant client: {e}")

        # Initialize Proxmox VE client
        self.proxmox_client: Optional[ProxmoxVEClient] = None
        if config.PROXMOX_HOST:
            try:
                self.proxmox_client = ProxmoxVEClient(
                    host=config.PROXMOX_HOST,
                    port=config.PROXMOX_PORT,
                    verify_ssl=config.PROXMOX_VERIFY_SSL,
                    username=config.PROXMOX_USERNAME if config.PROXMOX_USERNAME else None,
                    password=config.PROXMOX_PASSWORD if config.PROXMOX_PASSWORD else None,
                    token_id=config.PROXMOX_TOKEN_ID if config.PROXMOX_TOKEN_ID else None,
                    token_secret=config.PROXMOX_TOKEN_SECRET if config.PROXMOX_TOKEN_SECRET else None
                )
                # Authenticate if using username/password
                if config.PROXMOX_USERNAME and config.PROXMOX_PASSWORD:
                    self.proxmox_client.authenticate()
                logger.info("Proxmox VE client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Proxmox VE client: {e}")

        # Initialize Multi-AI provider
        self.multi_ai_provider: Optional[MultiAIProvider] = None
        try:
            api_keys = {
                "openai": config.OPENAI_API_KEY,
                "gemini": config.GEMINI_API_KEY,
                "grok": config.GROK_API_KEY
            }
            fallback_providers = [p.strip() for p in config.AI_FALLBACK_PROVIDERS.split(",") if p.strip()]
            
            self.multi_ai_provider = MultiAIProvider(
                primary_provider=config.AI_PROVIDER,
                fallback_providers=fallback_providers,
                api_keys=api_keys,
                model=config.AI_MODEL,
                temperature=config.AI_TEMPERATURE,
                max_tokens=config.AI_MAX_TOKENS
            )
            logger.info("Multi-AI provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Multi-AI provider: {e}")

        # Initialize Remote Control Manager
        self.remote_manager = RemoteControlManager(home_assistant_client=self.ha_client)
        self._load_tv_devices()

        # Initialize Mobile Device Manager
        self.mobile_manager = MobileDeviceManager()
        self._load_mobile_devices()

        logger.info("Automation engine initialized")

    def start(self) -> None:
        """Start the automation engine."""
        if self.running:
            logger.warning("Automation engine is already running")
            return

        self.running = True
        self.engine_thread = threading.Thread(target=self._run_engine, daemon=True)
        self.engine_thread.start()

        # Start device manager
        self.device_manager.start()

        logger.info("Automation engine started")

    def stop(self) -> None:
        """Stop the automation engine."""
        self.running = False

        if self.device_manager:
            self.device_manager.stop()

        if self.engine_thread and self.engine_thread.is_alive():
            self.engine_thread.join(timeout=5)

        logger.info("Automation engine stopped")

    def shutdown(self) -> None:
        """Shutdown the automation engine."""
        self.stop()

    def _run_engine(self) -> None:
        """Main engine loop."""
        logger.info("Automation engine main loop started")

        while self.running:
            try:
                # Check for automation rules
                self._process_automation_rules()

                # Process AI commands
                self._process_ai_commands()

                # Update device statuses
                self._update_device_statuses()

                # Sleep for a bit
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error in automation engine loop: {e}")
                time.sleep(10)

    def _process_automation_rules(self) -> None:
        """Process automation rules."""
        # Placeholder for automation rule processing
        pass

    def _process_ai_commands(self) -> None:
        """Process AI commands."""
        # Placeholder for AI command processing
        pass

    def _update_device_statuses(self) -> None:
        """Update device statuses."""
        # Get all devices and check their status
        devices = self.db_manager.get_devices()
        for device in devices:
            # Update last seen if device is online
            if device["status"] == "online":
                self.db_manager.update_device_status(device["id"], "online")

    def _load_tv_devices(self) -> None:
        """Load TV/remote devices from configuration."""
        try:
            config_path = Path(self.config.TV_DEVICES_CONFIG)
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)
                    for device_config in data.get("tv_devices", []):
                        device = RemoteDevice(
                            name=device_config["name"],
                            device_type=DeviceType(device_config["type"]),
                            ip_address=device_config["ip_address"],
                            port=device_config.get("port", 8080),
                            mac_address=device_config.get("mac_address"),
                            entity_id=device_config.get("entity_id"),
                            description=device_config.get("description", "")
                        )
                        self.remote_manager.add_device(device)
                logger.info(f"Loaded {len(data.get('tv_devices', []))} TV devices")
        except Exception as e:
            logger.error(f"Failed to load TV devices: {e}")

    def _load_mobile_devices(self) -> None:
        """Load mobile devices from configuration."""
        try:
            config_path = Path("config/mobile_devices.json")
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)
                    for device_config in data.get("mobile_devices", []):
                        device = MobileDevice(
                            name=device_config["name"],
                            device_id=device_config["device_id"],
                            ip_address=device_config.get("ip_address"),
                            port=device_config.get("port", 8080),
                            connection_method=ConnectionMethod(device_config.get("connection_method", "wireless")),
                            description=device_config.get("description", "")
                        )
                        self.mobile_manager.add_device(device)
                logger.info(f"Loaded {len(data.get('mobile_devices', []))} mobile devices")
        except Exception as e:
            logger.error(f"Failed to load mobile devices: {e}")

    def execute_command(self, command: str) -> dict[str, Any]:
        """Execute a natural language command using AI."""
        try:
            # Use AI to interpret the command
            interpretation = self.ai_intelligence.interpret_command(command)

            if not interpretation:
                return {"success": False, "message": "Could not understand command"}

            # Execute the interpreted command
            result = self._execute_interpreted_command(interpretation)

            return {
                "success": True,
                "command": command,
                "interpretation": interpretation,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return {"success": False, "message": str(e)}

    def _execute_interpreted_command(self, interpretation: dict[str, Any]) -> dict[str, Any]:
        """Execute an interpreted command."""
        action = interpretation.get("action")
        target = interpretation.get("target")
        parameters = interpretation.get("parameters", {})

        if action == "turn_on":
            return self.device_manager.turn_on_device(target)
        elif action == "turn_off":
            return self.device_manager.turn_off_device(target)
        elif action == "set_temperature":
            temperature = parameters.get("temperature")
            return self.device_manager.set_temperature(target, temperature)
        elif action == "get_status":
            return self.device_manager.get_device_status(target)
        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    def get_system_status(self) -> dict[str, Any]:
        """Get overall system status."""
        devices = self.db_manager.get_devices()

        online_devices = sum(1 for d in devices if d["status"] == "online")
        total_devices = len(devices)

        return {
            "engine_running": self.running,
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": total_devices - online_devices,
            "last_update": datetime.now(UTC).isoformat(),
            "devices": devices
        }
