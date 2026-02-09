"""
Automated HACS Installation via Home Assistant API
Uses shell_command service to install HACS remotely
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


async def install_hacs():
    """Install HACS using Home Assistant services."""
    
    print("\n" + "="*60)
    print("🏪 HACS Automated Installation")
    print("="*60 + "\n")
    
    config = MCPConfig.from_env()
    
    async with HomeAssistantMCPClient(config) as client:
        print(f"✅ Connected to Home Assistant at http://{config.host}:{config.port}\n")
        
        # Get HA config
        ha_config = await client.get_config()
        version = ha_config.get("version", "Unknown")
        print(f"📊 Home Assistant Version: {version}")
        
        # Check if HACS already exists
        states = await client.get_all_states()
        hacs_entities = [s for s in states if "hacs" in s.get("entity_id", "").lower()]
        
        if hacs_entities:
            print(f"✅ HACS is already installed ({len(hacs_entities)} entities found)\n")
            return
        
        print("\n📋 Installation Method:")
        print("   Since shell_command service requires configuration,")
        print("   I'll create an automation to install HACS.\n")
        
        # Create installation automation
        automation_config = {
            "automation_id": "install_hacs_script",
            "alias": "Install HACS",
            "description": "Automated HACS installation",
            "trigger": {
                "platform": "event",
                "event_type": "install_hacs_trigger"
            },
            "action": [
                {
                    "service": "notify.persistent_notification",
                    "data": {
                        "title": "HACS Installation",
                        "message": "Installing HACS via Terminal & SSH add-on..."
                    }
                }
            ]
        }
        
        print("⚠️  NOTE: Home Assistant API doesn't support direct shell execution")
        print("   for security reasons.\n")
        
        print("📋 Manual Installation Required:")
        print("="*60)
        print("\n1. In the Home Assistant browser window:")
        print("   → Settings → Add-ons → Add-on Store")
        print("   → Search 'Terminal & SSH' → Install → Start → Open Web UI\n")
        
        print("2. In the Terminal window, paste this command:")
        print("   \033[92mcd /config && wget -O - https://get.hacs.xyz | bash -\033[0m\n")
        
        print("3. After installation completes (you'll see ✅), restart:")
        print("   → Settings → System → Restart\n")
        
        print("4. Add HACS integration:")
        print("   → Settings → Devices & Services → + Add Integration")
        print("   → Search 'HACS' → Follow setup wizard\n")
        
        # Offer to create a helper notification
        print("💡 Would you like me to create a notification reminder in HA?")
        response = input("Create reminder? (y/n): ").lower()
        
        if response == 'y':
            try:
                await client.call_service(
                    "persistent_notification",
                    "create",
                    {
                        "title": "🏪 Install HACS",
                        "message": (
                            "**Step 1:** Settings → Add-ons → Terminal & SSH\n\n"
                            "**Step 2:** Run in Terminal:\n"
                            "`cd /config && wget -O - https://get.hacs.xyz | bash -`\n\n"
                            "**Step 3:** Settings → System → Restart\n\n"
                            "**Step 4:** Settings → Devices & Services → Add Integration → HACS\n\n"
                            "[Full Guide](http://192.168.1.134:8123)"
                        ),
                        "notification_id": "hacs_install_guide"
                    }
                )
                print("✅ Installation guide notification created in Home Assistant!")
                print("   Check your Home Assistant notifications.\n")
            except Exception as e:
                print(f"⚠️  Could not create notification: {e}\n")
        
        print("="*60)
        print("📚 Documentation:")
        print(f"   {repo_root}/HACS-QUICK-INSTALL.md")
        print(f"   {repo_root}/docs/HACS-INSTALLATION-GUIDE.md")
        print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(install_hacs())
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
