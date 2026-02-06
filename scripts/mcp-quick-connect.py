#!/usr/bin/env python3
"""
Quick MCP interaction script for Home Assistant
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "mcp-servers"))

from ha_mcp_client import HomeAssistantMCPClient, MCPConfig
from dotenv import load_dotenv

# Load environment
load_dotenv(repo_root / "config" / ".env")

async def main():
    """Connect and interact with Home Assistant via MCP"""
    config = MCPConfig.from_env()
    
    async with HomeAssistantMCPClient(config) as client:
        print("✅ Connected to Home Assistant via MCP")
        print(f"📍 Server: {config.host}:{config.port}\n")
        
        # Get all states
        states = await client.get_all_states()
        print(f"📊 Total Entities: {len(states)}")
        
        # Show entity domains
        domains = set(s.get('entity_id', '').split('.')[0] for s in states if '.' in s.get('entity_id', ''))
        print(f"🏷️  Domains: {', '.join(sorted(domains))}\n")
        
        # Get config
        config_data = await client.get_config()
        print(f"🏠 Home Assistant Version: {config_data.get('version')}")
        print(f"📍 Location: {config_data.get('location_name')}")
        print(f"⏰ Timezone: {config_data.get('time_zone')}\n")
        
        # List some entities by domain
        print("🔌 Sample Entities:")
        for domain in ['light', 'switch', 'sensor', 'automation'][:4]:
            domain_entities = [s for s in states if s.get('entity_id', '').startswith(f"{domain}.")]
            if domain_entities:
                print(f"  {domain}: {len(domain_entities)} entities")
                # Show first 3
                for entity in domain_entities[:3]:
                    state = entity.get('state', 'unknown')
                    name = entity.get('attributes', {}).get('friendly_name', entity.get('entity_id'))
                    print(f"    - {name}: {state}")
        
        print("\n✅ MCP Session Complete")

if __name__ == "__main__":
    asyncio.run(main())
