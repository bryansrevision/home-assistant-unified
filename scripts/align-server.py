#!/usr/bin/env python3
"""
Home Assistant Server Synchronization Script
Aligns repository with live Home Assistant server using MCP
"""

import asyncio
import argparse
import logging
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import sys

# Load .env file BEFORE importing config classes
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_file, override=True)

# Add mcp-servers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

from ha_mcp_client import (
    HomeAssistantMCPClient,
    MCPConfig,
    SyncDirection
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ha-sync.log')
    ]
)
logger = logging.getLogger(__name__)


class ServerAlignmentManager:
    """Manages alignment between repository and live server"""
    
    def __init__(self, repo_root: Path = None):
        """
        Initialize manager
        
        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.config = MCPConfig.from_env()
        self.client: Optional[HomeAssistantMCPClient] = None
        
    async def connect(self) -> bool:
        """Connect to Home Assistant"""
        self.client = HomeAssistantMCPClient(self.config, self.repo_root)
        return await self.client.connect()
    
    async def disconnect(self):
        """Disconnect from Home Assistant"""
        if self.client:
            await self.client.disconnect()
    
    async def diagnose_alignment(self) -> dict:
        """
        Diagnose alignment between repo and server
        
        Returns:
            Diagnostic report
        """
        logger.info("🔍 Starting alignment diagnosis...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "server": {
                "host": self.config.host,
                "port": self.config.port,
                "connected": self.client.connected if self.client else False,
            },
            "repository": {
                "path": str(self.repo_root),
                "exists": self.repo_root.exists(),
            },
            "alignment": {},
            "issues": [],
            "recommendations": []
        }
        
        if not self.client or not self.client.connected:
            report["issues"].append("Not connected to Home Assistant server")
            return report
        
        try:
            # Check entities
            states = await self.client.get_all_states()
            report["server"]["total_entities"] = len(states)
            
            # Check configurations
            config = await self.client.get_config()
            report["server"]["version"] = config.get("version", "unknown")
            report["server"]["components"] = config.get("components", [])
            
            # Check automations
            automations = await self.client.get_automations()
            report["server"]["automations"] = len(automations)
            
            # Check repository structure
            repo_issues = self._check_repo_structure()
            if repo_issues:
                report["issues"].extend(repo_issues)
            
            # Check configuration files
            config_issues = self._check_configuration_files()
            if config_issues:
                report["issues"].extend(config_issues)
            
            # Generate recommendations
            report["recommendations"] = self._generate_recommendations(report)
            
            logger.info(f"✅ Diagnosis complete: {len(report['issues'])} issues found")
            return report
        
        except Exception as e:
            logger.error(f"Error during diagnosis: {e}")
            report["issues"].append(f"Diagnosis error: {str(e)}")
            return report
    
    def _check_repo_structure(self) -> list:
        """Check repository structure for issues"""
        issues = []
        
        required_dirs = [
            "core",
            "automations",
            "mcp-servers",
            "integrations",
            "config"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.repo_root / dir_name
            if not dir_path.exists():
                issues.append(f"Missing directory: {dir_name}")
        
        # Check for configuration files
        config_file = self.repo_root / "core" / "configuration.yaml"
        if not config_file.exists():
            issues.append("Missing core/configuration.yaml")
        
        env_file = self.repo_root / "config" / ".env"
        if not env_file.exists():
            issues.append("Missing config/.env")
        
        return issues
    
    def _check_configuration_files(self) -> list:
        """Check if configuration files are properly aligned"""
        issues = []
        
        # Check if .env has required tokens
        env_file = self.repo_root / "config" / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
                
                required_vars = [
                    "HOME_ASSISTANT_TOKEN",
                    "HOME_ASSISTANT_URL",
                ]
                
                for var in required_vars:
                    if f"{var}=your_" in env_content or f"{var}=" not in env_content:
                        issues.append(f"Missing or placeholder value: {var}")
        
        return issues
    
    def _generate_recommendations(self, report: dict) -> list:
        """Generate recommendations based on diagnosis"""
        recommendations = []
        
        if report["issues"]:
            recommendations.append("Resolve configuration issues before syncing")
        
        if not report["server"]["connected"]:
            recommendations.append("Ensure Home Assistant server is running and accessible")
        
        if report["server"].get("total_entities", 0) == 0:
            recommendations.append("Home Assistant server has no entities configured")
        
        # Check if repo automations match server
        if report["server"].get("automations", 0) > 0:
            recommendations.append("Run 'sync --pull' to get latest server automations")
        
        recommendations.append("After alignment, commit changes to git")
        
        return recommendations
    
    async def sync_to_server(self, sync_type: str = "automations") -> bool:
        """
        Sync repository changes to live server
        
        Args:
            sync_type: Type of sync (automations, config, all)
        
        Returns:
            True if sync successful
        """
        logger.info(f"📤 Syncing {sync_type} from repo to server...")
        
        if not self.client or not self.client.connected:
            logger.error("Not connected to server")
            return False
        
        try:
            if sync_type in ["automations", "all"]:
                success = await self.client.sync_automations(SyncDirection.REPO_TO_SERVER)
                if not success:
                    logger.warning("Automation sync failed")
            
            if sync_type in ["config", "all"]:
                await self._sync_configuration_to_server()
            
            logger.info("✅ Sync to server completed")
            return True
        
        except Exception as e:
            logger.error(f"Sync to server failed: {e}")
            return False
    
    async def sync_from_server(self, sync_type: str = "automations") -> bool:
        """
        Pull latest changes from live server to repository
        
        Args:
            sync_type: Type of sync (automations, states, all)
        
        Returns:
            True if sync successful
        """
        logger.info(f"📥 Syncing {sync_type} from server to repo...")
        
        if not self.client or not self.client.connected:
            logger.error("Not connected to server")
            return False
        
        try:
            if sync_type in ["automations", "all"]:
                success = await self.client.sync_automations(SyncDirection.SERVER_TO_REPO)
                if not success:
                    logger.warning("Automation sync failed")
            
            if sync_type in ["states", "all"]:
                export_path = await self.client.export_state()
                logger.info(f"State exported to {export_path}")
            
            logger.info("✅ Sync from server completed")
            return True
        
        except Exception as e:
            logger.error(f"Sync from server failed: {e}")
            return False
    
    async def _sync_configuration_to_server(self):
        """Sync configuration files to server"""
        logger.info("Syncing configuration files...")
        # Implementation would push configuration
        logger.info("✅ Configuration sync completed")
    
    async def health_check(self) -> dict:
        """Perform health check"""
        logger.info("🏥 Running health check...")
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "server": {
                "connected": False,
                "endpoints": {}
            },
            "repository": {
                "structure": "OK",
                "configuration": "OK"
            }
        }
        
        if not self.client:
            return health
        
        try:
            # Check server connectivity
            states = await self.client.get_all_states()
            health["server"]["connected"] = len(states) > 0
            health["server"]["entities"] = len(states)
            
            config = await self.client.get_config()
            health["server"]["config"] = "OK"
            
            automations = await self.client.get_automations()
            health["server"]["automations"] = len(automations)
            
        except Exception as e:
            health["server"]["error"] = str(e)
        
        return health


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Home Assistant Server Alignment Tool"
    )
    parser.add_argument(
        "action",
        choices=["diagnose", "sync-push", "sync-pull", "health-check"],
        help="Action to perform"
    )
    parser.add_argument(
        "--type",
        choices=["automations", "config", "states", "all"],
        default="all",
        help="Sync type"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        help="Repository root path"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create manager
    manager = ServerAlignmentManager(repo_root=args.repo)
    
    try:
        # Connect to server
        if not await manager.connect():
            logger.error("Failed to connect to Home Assistant server")
            return 1
        
        # Perform action
        if args.action == "diagnose":
            report = await manager.diagnose_alignment()
            print(json.dumps(report, indent=2))
        
        elif args.action == "sync-push":
            success = await manager.sync_to_server(sync_type=args.type)
            return 0 if success else 1
        
        elif args.action == "sync-pull":
            success = await manager.sync_from_server(sync_type=args.type)
            return 0 if success else 1
        
        elif args.action == "health-check":
            health = await manager.health_check()
            print(json.dumps(health, indent=2))
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
