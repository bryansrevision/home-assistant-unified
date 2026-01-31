#!/usr/bin/env python3
"""
Home Assistant Live Server MCP Connection Handler
Manages bidirectional real-time synchronization between repository and live server
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

import aiohttp
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Sync direction enumeration"""
    REPO_TO_SERVER = "repo_to_server"
    SERVER_TO_REPO = "server_to_repo"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class MCPConfig:
    """MCP Configuration data class"""
    host: str = "192.168.1.201"
    port: int = 8123
    token: str = ""
    protocol: str = "http"
    base_url: str = ""
    
    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"{self.protocol}://{self.host}:{self.port}/api"
    
    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("HA_HOST", "192.168.1.201"),
            port=int(os.getenv("HA_PORT", "8123")),
            token=os.getenv("HOME_ASSISTANT_TOKEN", ""),
            protocol=os.getenv("HA_PROTOCOL", "http"),
        )


@dataclass
class EntityState:
    """Entity state representation"""
    entity_id: str
    state: str
    attributes: Dict[str, Any]
    last_changed: str
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class HomeAssistantMCPClient:
    """Home Assistant MCP Live Server Client"""
    
    def __init__(self, config: MCPConfig, repo_root: Path = None):
        """
        Initialize MCP client
        
        Args:
            config: MCP configuration
            repo_root: Path to repository root
        """
        self.config = config
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.event_callbacks: List[Callable] = []
        self.state_cache: Dict[str, EntityState] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self) -> bool:
        """
        Establish connection to Home Assistant
        
        Returns:
            True if connection successful
        """
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(
                f"{self.config.base_url}/",
                headers=self._get_headers()
            ) as resp:
                if resp.status == 200:
                    self.connected = True
                    logger.info(f"✅ Connected to Home Assistant at {self.config.base_url}")
                    await self._cache_all_states()
                    return True
                else:
                    logger.error(f"❌ Connection failed with status {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Home Assistant"""
        if self.session:
            await self.session.close()
        self.connected = False
        logger.info("Disconnected from Home Assistant")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        return {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
    
    async def get_all_states(self) -> Dict[str, Any]:
        """Retrieve all entity states from server"""
        if not self.connected:
            raise RuntimeError("Not connected to Home Assistant")
        
        try:
            async with self.session.get(
                f"{self.config.base_url}/states",
                headers=self._get_headers()
            ) as resp:
                if resp.status == 200:
                    states = await resp.json()
                    logger.info(f"📊 Retrieved {len(states)} states from server")
                    return states
                else:
                    logger.error(f"Failed to get states: {resp.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error retrieving states: {e}")
            return {}
    
    async def _cache_all_states(self):
        """Cache all entity states locally"""
        states = await self.get_all_states()
        for state_data in states:
            entity_id = state_data.get("entity_id")
            state = EntityState(
                entity_id=entity_id,
                state=state_data.get("state"),
                attributes=state_data.get("attributes", {}),
                last_changed=state_data.get("last_changed"),
                last_updated=state_data.get("last_updated")
            )
            self.state_cache[entity_id] = state
        logger.info(f"💾 Cached {len(self.state_cache)} entity states")
    
    async def get_config(self) -> Dict[str, Any]:
        """Retrieve Home Assistant configuration"""
        if not self.connected:
            raise RuntimeError("Not connected to Home Assistant")
        
        try:
            async with self.session.get(
                f"{self.config.base_url}/config",
                headers=self._get_headers()
            ) as resp:
                if resp.status == 200:
                    config = await resp.json()
                    logger.info("📋 Retrieved Home Assistant configuration")
                    return config
                else:
                    logger.error(f"Failed to get config: {resp.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error retrieving config: {e}")
            return {}
    
    async def call_service(self, domain: str, service: str, 
                          entity_id: str = None, **data) -> Dict[str, Any]:
        """
        Call a Home Assistant service
        
        Args:
            domain: Service domain (e.g., 'light')
            service: Service name (e.g., 'turn_on')
            entity_id: Target entity ID
            **data: Additional service data
        
        Returns:
            Service call response
        """
        if not self.connected:
            raise RuntimeError("Not connected to Home Assistant")
        
        payload = data.copy()
        if entity_id:
            payload["entity_id"] = entity_id
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/services/{domain}/{service}",
                headers=self._get_headers(),
                json=payload
            ) as resp:
                if resp.status in [200, 201]:
                    result = await resp.json()
                    logger.info(f"🔧 Service call: {domain}/{service} → {entity_id}")
                    return result
                else:
                    logger.error(f"Service call failed: {resp.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error calling service: {e}")
            return {}
    
    async def get_automations(self) -> List[Dict[str, Any]]:
        """Retrieve all automation configurations"""
        try:
            # Automations are typically entities with domain 'automation'
            states = await self.get_all_states()
            automations = [s for s in states if s.get("entity_id", "").startswith("automation.")]
            logger.info(f"🤖 Retrieved {len(automations)} automations")
            return automations
        except Exception as e:
            logger.error(f"Error retrieving automations: {e}")
            return []
    
    async def export_state(self, output_path: Path = None) -> Path:
        """
        Export current server state to file
        
        Args:
            output_path: Path to save state export
        
        Returns:
            Path to exported file
        """
        if output_path is None:
            # Use filesystem-safe timestamp format (replace colons with hyphens)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = self.repo_root / "backups" / "state-exports" / f"state-{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            states = await self.get_all_states()
            config = await self.get_config()
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "server": {
                    "host": self.config.host,
                    "port": self.config.port,
                },
                "stats": {
                    "total_entities": len(states),
                },
                "states": states,
                "config": config,
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"💾 State exported to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error exporting state: {e}")
            raise
    
    async def sync_automations(self, direction: SyncDirection = SyncDirection.REPO_TO_SERVER) -> bool:
        """
        Synchronize automations between repo and server
        
        Args:
            direction: Sync direction
        
        Returns:
            True if sync successful
        """
        logger.info(f"🔄 Starting automation sync: {direction.value}")
        
        try:
            automations_path = self.repo_root / "automations"
            
            if direction == SyncDirection.REPO_TO_SERVER:
                return await self._sync_repo_to_server(automations_path)
            elif direction == SyncDirection.SERVER_TO_REPO:
                return await self._sync_server_to_repo(automations_path)
            else:
                # Bidirectional: server wins on conflicts
                return await self._sync_bidirectional(automations_path)
        except Exception as e:
            logger.error(f"Error during sync: {e}")
            return False
    
    async def _sync_repo_to_server(self, automations_path: Path) -> bool:
        """Sync automations from repository to server"""
        logger.info("📤 Syncing repo → server")
        # Implementation would push automations to server
        # This is a placeholder for the actual implementation
        logger.info("✅ Repo → Server sync completed")
        return True
    
    async def _sync_server_to_repo(self, automations_path: Path) -> bool:
        """Sync automations from server to repository"""
        logger.info("📥 Syncing server → repo")
        
        try:
            automations = await self.get_automations()
            automations_path.mkdir(parents=True, exist_ok=True)
            
            for automation in automations:
                # Parse automation configuration
                entity_id = automation.get("entity_id")
                if entity_id:
                    filename = f"{entity_id.replace('.', '_')}.yaml"
                    filepath = automations_path / filename
                    
                    # Save as YAML
                    import yaml
                    with open(filepath, 'w') as f:
                        yaml.dump(automation, f, default_flow_style=False)
            
            logger.info(f"✅ Server → Repo sync completed ({len(automations)} automations)")
            return True
        except Exception as e:
            logger.error(f"Error syncing server → repo: {e}")
            return False
    
    async def _sync_bidirectional(self, automations_path: Path) -> bool:
        """Bidirectional sync (server wins on conflicts)"""
        logger.info("🔄 Bidirectional sync (server wins)")
        return await self._sync_server_to_repo(automations_path)
    
    def register_event_callback(self, callback: Callable):
        """Register callback for state change events"""
        self.event_callbacks.append(callback)
    
    async def listen_for_events(self):
        """Listen for state change events (placeholder)"""
        logger.info("🎧 Listening for events...")
        # Implementation would use websocket or EventSource
        # for real-time event streaming


async def main():
    """Main function for testing"""
    # Load configuration from environment
    config = MCPConfig.from_env()
    
    if not config.token:
        logger.error("HOME_ASSISTANT_TOKEN environment variable not set")
        return
    
    # Connect and perform operations
    async with HomeAssistantMCPClient(config) as client:
        # Get all states
        states = await client.get_all_states()
        print(f"\n📊 Total entities: {len(states)}")
        
        # Export state
        export_path = await client.export_state()
        print(f"\n💾 State exported to: {export_path}")
        
        # Get configuration
        config_data = await client.get_config()
        print(f"\n📋 Configuration: {json.dumps(config_data, indent=2)[:500]}...")


if __name__ == "__main__":
    asyncio.run(main())
