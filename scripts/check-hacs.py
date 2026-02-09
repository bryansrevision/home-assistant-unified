"""
Check HACS Installation Status

This script checks if HACS (Home Assistant Community Store) is installed
and provides installation guidance if not found.
"""

import asyncio
import sys
from pathlib import Path

# Add MCP client to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "mcp-servers"))

from ha_mcp_client import HomeAssistantMCPClient, MCPConfig
from dotenv import load_dotenv

# Load environment
load_dotenv(repo_root / "config" / ".env")


async def check_hacs_installation():
    """Check if HACS is installed on Home Assistant server."""
    
    print("\n🔍 Checking HACS Installation Status...")
    print("=" * 60)
    
    config = MCPConfig.from_env()
    
    async with HomeAssistantMCPClient(config) as client:
        print(f"✅ Connected to Home Assistant at http://{config.host}:{config.port}")
        
        # Get all entities
        states = await client.get_all_states()
        
        # Look for HACS-related entities
        hacs_entities = [
            s for s in states 
            if "hacs" in s.get("entity_id", "").lower() 
            or "hacs" in s.get("attributes", {}).get("friendly_name", "").lower()
        ]
        
        # Get Home Assistant info
        ha_config = await client.get_config()
        version = ha_config.get("version", "Unknown")
        
        print(f"📊 Home Assistant Version: {version}")
        print(f"📍 Total Entities: {len(states)}")
        print()
        
        # Check for HACS
        if hacs_entities:
            print("✅ HACS IS INSTALLED!")
            print(f"   Found {len(hacs_entities)} HACS-related entities:")
            for entity in hacs_entities[:5]:  # Show first 5
                print(f"   - {entity['entity_id']}")
            if len(hacs_entities) > 5:
                print(f"   ... and {len(hacs_entities) - 5} more")
            print()
            
            # Try to get HACS sensor info
            hacs_sensor = next(
                (e for e in hacs_entities if e["entity_id"].startswith("sensor.hacs")),
                None
            )
            if hacs_sensor:
                attrs = hacs_sensor.get("attributes", {})
                print("📦 HACS Information:")
                print(f"   Repositories: {attrs.get('repositories', 'N/A')}")
                print(f"   Pending Updates: {hacs_sensor.get('state', 'N/A')}")
                
        else:
            print("❌ HACS NOT FOUND")
            print()
            print("📋 Installation Instructions:")
            print("   1. See: docs/HACS-INSTALLATION-GUIDE.md")
            print("   2. Or run: Install-HACS.ps1 (PowerShell)")
            print("   3. Manual: https://hacs.xyz/docs/setup/download")
            print()
            print("Quick Install via SSH:")
            print("   ssh root@192.168.1.134")
            print("   cd /config")
            print("   wget -O - https://get.hacs.xyz | bash -")
            print("   Then restart Home Assistant")
        
        print()
        print("=" * 60)
        print("✅ Check complete")


if __name__ == "__main__":
    try:
        asyncio.run(check_hacs_installation())
    except KeyboardInterrupt:
        print("\n⚠️  Check cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
