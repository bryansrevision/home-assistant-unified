"""
Detailed HACS Status Check
Checks for HACS integration, entities, and configuration
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


async def detailed_hacs_check():
    """Perform detailed HACS installation check."""
    
    print("\n" + "="*70)
    print("🔍 DETAILED HACS STATUS CHECK")
    print("="*70 + "\n")
    
    config = MCPConfig.from_env()
    
    async with HomeAssistantMCPClient(config) as client:
        print(f"✅ Connected to http://{config.host}:{config.port}\n")
        
        # Get all entities
        states = await client.get_all_states()
        
        # Check for HACS entities (various patterns)
        hacs_patterns = ['hacs', 'sensor.hacs', 'update.hacs', 'binary_sensor.hacs']
        found_entities = []
        
        for entity in states:
            entity_id = entity.get('entity_id', '').lower()
            for pattern in hacs_patterns:
                if pattern in entity_id:
                    found_entities.append(entity)
                    break
        
        print("📊 Entity Search Results:")
        print("-" * 70)
        
        if found_entities:
            print(f"✅ Found {len(found_entities)} HACS-related entities:\n")
            for entity in found_entities:
                print(f"   🔹 {entity['entity_id']}")
                print(f"      State: {entity.get('state', 'N/A')}")
                if entity.get('attributes'):
                    attrs = entity['attributes']
                    if 'friendly_name' in attrs:
                        print(f"      Name: {attrs['friendly_name']}")
                print()
        else:
            print("❌ No HACS entities found\n")
        
        # Check for any entities with 'custom_component' in attributes
        print("\n📦 Checking for Custom Components:")
        print("-" * 70)
        
        custom_component_entities = []
        for entity in states:
            attrs = entity.get('attributes', {})
            if isinstance(attrs, dict):
                # Check if entity source mentions custom_components
                if any('custom_component' in str(v).lower() for v in attrs.values()):
                    custom_component_entities.append(entity)
        
        if custom_component_entities:
            print(f"✅ Found {len(custom_component_entities)} custom component entities\n")
        else:
            print("ℹ️  No custom component indicator found in entity attributes\n")
        
        # Domain breakdown
        print("\n📋 All Entity Domains:")
        print("-" * 70)
        domains = {}
        for entity in states:
            domain = entity.get('entity_id', '').split('.')[0]
            domains[domain] = domains.get(domain, 0) + 1
        
        for domain in sorted(domains.keys()):
            print(f"   {domain}: {domains[domain]}")
        
        print("\n" + "="*70)
        print("💡 TROUBLESHOOTING TIPS:")
        print("="*70)
        
        if not found_entities:
            print("""
1. **Check HACS is in sidebar:**
   - Look for HACS icon in Home Assistant left sidebar
   - If not there, HACS may not be fully initialized yet

2. **Check Integration was added:**
   - Settings → Devices & Services
   - Look for "HACS" integration
   - If missing, re-add: + Add Integration → Search HACS

3. **Check Home Assistant Logs:**
   - Settings → System → Logs
   - Filter by "hacs" to see any errors

4. **Wait for Initialization:**
   - HACS can take 2-5 minutes after first setup
   - Check back in a few minutes

5. **Verify Files Exist:**
   - Use Terminal & SSH add-on
   - Run: ls -la /config/custom_components/hacs/
   - Should see manifest.json, __init__.py, etc.

6. **Try Restarting Again:**
   - Settings → System → Restart
   - Sometimes HACS needs a second restart
            """)
        else:
            print("""
✅ HACS appears to be working!

Next Steps:
1. Click HACS in the sidebar
2. Browse Integrations and Frontend cards
3. Install recommended:
   - Frontend: button-card, card-mod, mini-media-player
   - Integration: Alexa Media Player (if using Alexa)
            """)
        
        print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(detailed_hacs_check())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
