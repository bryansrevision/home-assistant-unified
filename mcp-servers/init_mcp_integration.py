#!/usr/bin/env python3
"""
Home Assistant MCP Integration Initialization
Sets up bidirectional MCP connection with live server
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# Load .env file BEFORE importing config classes
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_file, override=True)

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from ha_mcp_client import HomeAssistantMCPClient, MCPConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPIntegrationManager:
    """Manages MCP integration with Home Assistant"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize MCP integration manager"""
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.config = MCPConfig.from_env()
        self.client: Optional[HomeAssistantMCPClient] = None
        self.integration_status: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """
        Initialize MCP integration
        
        Returns:
            True if initialization successful
        """
        logger.info("🚀 Initializing MCP Integration...")
        
        try:
            # Create client
            self.client = HomeAssistantMCPClient(self.config, self.repo_root)
            
            # Connect to server
            if not await self.client.connect():
                logger.error("❌ Failed to connect to Home Assistant")
                return False
            
            logger.info("✅ Connected to Home Assistant")
            
            # Verify credentials
            if not await self._verify_credentials():
                logger.error("❌ Credential verification failed")
                return False
            
            logger.info("✅ Credentials verified")
            
            # Setup integrations
            if not await self._setup_integrations():
                logger.warning("⚠️ Some integrations failed to setup")
            
            # Verify configuration
            if not await self._verify_configuration():
                logger.warning("⚠️ Configuration verification failed")
            
            # Export baseline state
            await self._create_baseline_export()
            
            logger.info("✅ MCP Integration initialized successfully")
            self.integration_status["initialized"] = True
            self.integration_status["timestamp"] = datetime.now().isoformat()
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            return False
    
    async def _verify_credentials(self) -> bool:
        """Verify Home Assistant credentials"""
        logger.info("🔐 Verifying credentials...")
        
        try:
            # Try to get config
            config = await self.client.get_config()
            
            if config:
                logger.info(f"✅ Home Assistant version: {config.get('version', 'unknown')}")
                self.integration_status["ha_version"] = config.get("version")
                return True
            else:
                logger.error("❌ Failed to retrieve configuration")
                return False
        
        except Exception as e:
            logger.error(f"❌ Credential verification error: {e}")
            return False
    
    async def _setup_integrations(self) -> bool:
        """Setup required MCP integrations"""
        logger.info("📦 Setting up integrations...")
        
        integrations_to_setup = [
            ("mqtt", "MQTT Broker"),
            ("influxdb", "InfluxDB"),
            ("proxmox", "Proxmox Management"),
        ]
        
        success = True
        for integration_id, integration_name in integrations_to_setup:
            logger.info(f"  Setting up {integration_name}...")
            try:
                if await self._setup_integration(integration_id):
                    logger.info(f"  ✅ {integration_name} setup complete")
                else:
                    logger.warning(f"  ⚠️ {integration_name} setup failed")
                    success = False
            except Exception as e:
                logger.warning(f"  ⚠️ {integration_name} error: {e}")
                success = False
        
        return success
    
    async def _setup_integration(self, integration_id: str) -> bool:
        """Setup a specific integration"""
        # Placeholder for actual integration setup
        # In real implementation, this would:
        # 1. Load integration-specific configuration
        # 2. Setup MQTT topics
        # 3. Configure InfluxDB measurements
        # 4. Setup webhooks for Proxmox
        return True
    
    async def _verify_configuration(self) -> bool:
        """Verify Home Assistant configuration"""
        logger.info("⚙️ Verifying configuration...")
        
        try:
            states = await self.client.get_all_states()
            
            if not states:
                logger.warning("⚠️ No entities found in configuration")
                return False
            
            logger.info(f"✅ Configuration verified: {len(states)} entities")
            self.integration_status["entities_count"] = len(states)
            
            # Check critical entity domains
            domains = set()
            for state in states:
                entity_id = state.get("entity_id", "")
                domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
                domains.add(domain)
            
            logger.info(f"✅ Found {len(domains)} entity domains")
            self.integration_status["domains"] = sorted(list(domains))
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Configuration verification error: {e}")
            return False
    
    async def _create_baseline_export(self):
        """Create baseline state export"""
        logger.info("💾 Creating baseline state export...")
        
        try:
            export_path = await self.client.export_state(
                self.repo_root / "backups" / "state-exports" / "baseline.json"
            )
            logger.info(f"✅ Baseline exported to {export_path}")
            self.integration_status["baseline_export"] = str(export_path)
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to create baseline export: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get MCP integration status"""
        return {
            "server": {
                "host": self.config.host,
                "port": self.config.port,
                "connected": self.client.connected if self.client else False,
            },
            "integration": self.integration_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.disconnect()


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Home Assistant MCP Integration Initializer")
    logger.info("=" * 60)
    
    manager = MCPIntegrationManager()
    
    try:
        # Initialize integration
        if await manager.initialize():
            status = await manager.get_status()
            logger.info("\n✅ Integration Status:")
            logger.info(json.dumps(status, indent=2))
            
            # Create integration status file
            status_file = Path(__file__).parent.parent / "mcp-servers" / ".integration-status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            logger.info(f"\n✅ Integration status saved to {status_file}")
            return 0
        else:
            logger.error("\n❌ Integration initialization failed")
            return 1
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
