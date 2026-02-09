#!/usr/bin/env python3
"""
Interactive HACS Installation Guide
Walks user through installation step-by-step
"""

import asyncio
import sys
from pathlib import Path
import time

# Add MCP client to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "mcp-servers"))

from ha_mcp_client import HomeAssistantMCPClient, MCPConfig
from dotenv import load_dotenv

# Load environment
load_dotenv(repo_root / "config" / ".env")


def clear_screen():
    """Clear terminal screen."""
    print("\n" * 2)


def print_step(step_num, total_steps, title, instructions):
    """Print a formatted step."""
    print("\n" + "="*70)
    print(f"📍 STEP {step_num}/{total_steps}: {title}")
    print("="*70)
    print(instructions)
    print("="*70 + "\n")


async def wait_for_hacs(client, timeout=300):
    """Wait for HACS to appear after restart."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            states = await client.get_all_states()
            hacs_entities = [s for s in states if "hacs" in s.get("entity_id", "").lower()]
            if hacs_entities:
                return True
        except:
            pass
        await asyncio.sleep(5)
    return False


async def interactive_installation():
    """Interactive HACS installation guide."""
    
    print("\n" + "🏪 "*25)
    print(" "*20 + "HACS INSTALLATION WIZARD")
    print("🏪 "*25 + "\n")
    
    config = MCPConfig.from_env()
    
    async with HomeAssistantMCPClient(config) as client:
        # Check current status
        states = await client.get_all_states()
        hacs_entities = [s for s in states if "hacs" in s.get("entity_id", "").lower()]
        
        if hacs_entities:
            print("✅ HACS is already installed!")
            print(f"   Found {len(hacs_entities)} HACS entities\n")
            return
        
        # Step 1: Access Terminal
        print_step(1, 6, "Access Terminal & SSH Add-on", """
In your Home Assistant browser window (http://192.168.1.201:8123):

1. Click ⚙️ **Settings** (bottom left sidebar)
2. Click **Add-ons**
3. Click **Add-on Store** (bottom right blue button)
4. In the search box, type: **Terminal & SSH**
5. Click on **Terminal & SSH** (or **SSH & Web Terminal**)
6. If not installed:
   - Click **INSTALL** button
   - Wait for installation to complete (30-60 seconds)
7. Click **START** button
8. Click **Configuration** tab
   - Set "Show in sidebar" to ON
9. Click **OPEN WEB UI** button

A new browser tab will open with a terminal window.
        """)
        
        input("Press ENTER when you have the Terminal window open...")
        
        # Step 2: Run installation command
        print_step(2, 6, "Run HACS Installation Command", f"""
In the Terminal window, copy and paste this EXACT command:

    \033[1;32mcd /config && wget -O - https://get.hacs.xyz | bash -\033[0m

Then press ENTER.

You should see:
  - Downloading HACS...
  - Installing...
  - ✅ HACS installation complete

This takes 10-30 seconds.

⚠️  If you get 'wget: command not found', use this instead:
    \033[1;32mcd /config && curl -sfSL https://get.hacs.xyz | bash -\033[0m
        """)
        
        input("Press ENTER after installation completes...")
        
        # Step 3: Verify installation
        print_step(3, 6, "Verify HACS Files", """
In the Terminal, run this command to verify:

    \033[1;32mls -la /config/custom_components/hacs/\033[0m

You should see multiple files including:
  - __init__.py
  - manifest.json
  - etc.

If you see these files, HACS is installed correctly!
        """)
        
        input("Press ENTER when you see HACS files listed...")
        
        # Step 4: Restart HA
        print_step(4, 6, "Restart Home Assistant", """
Back in the main Home Assistant window:

1. Click ⚙️ **Settings** (bottom left)
2. Click **System**
3. Click **RESTART** button (top right)
4. Click **RESTART** in the confirmation dialog

Home Assistant will restart (takes 30-60 seconds).
The page will reload automatically when ready.
        """)
        
        response = input("Press ENTER after you've triggered the restart...")
        
        print("\n⏳ Waiting for Home Assistant to restart...")
        print("   (This usually takes 30-60 seconds)\n")
        
        # Wait for restart
        await asyncio.sleep(10)  # Initial wait
        
        reconnected = False
        for i in range(12):  # Try for 60 seconds
            try:
                states = await client.get_all_states()
                reconnected = True
                print("✅ Home Assistant is back online!\n")
                break
            except:
                print(f"   Still restarting... ({(i+1)*5}s)")
                await asyncio.sleep(5)
        
        if not reconnected:
            print("⚠️  Taking longer than expected. Please wait and continue manually.\n")
        
        # Step 5: Add HACS integration
        print_step(5, 6, "Add HACS Integration", """
In Home Assistant:

1. Go to ⚙️ **Settings** → **Devices & Services**
2. Click the **+ ADD INTEGRATION** button (bottom right)
3. In the search box, type: **HACS**
4. Click on **HACS** when it appears
5. The HACS setup wizard will start

Follow the on-screen prompts.
        """)
        
        input("Press ENTER when HACS setup wizard appears...")
        
        # Step 6: GitHub authentication
        print_step(6, 6, "Authenticate with GitHub", """
HACS will show you:
   - An 8-character device activation code (like: ABCD-1234)
   - A link to https://github.com/login/device

Steps:
1. Click the link (or manually go to https://github.com/login/device)
2. Login to GitHub if needed
3. Enter the 8-character code
4. Click **Continue**
5. Click **Authorize hacs/integration**
6. Return to Home Assistant

In Home Assistant:
1. Check these boxes:
   ☑ **Integrations**
   ☑ **Frontend** 
   ☑ **Themes**
2. Read and accept the terms
3. Click **SUBMIT**

HACS will now initialize (takes 2-5 minutes).
When complete, you'll see HACS in the sidebar!
        """)
        
        input("Press ENTER when you've completed GitHub authentication...")
        
        print("\n⏳ Checking if HACS is now active...\n")
        
        # Check for HACS
        for i in range(6):
            states = await client.get_all_states()
            hacs_entities = [s for s in states if "hacs" in s.get("entity_id", "").lower()]
            if hacs_entities:
                print("\n" + "🎉 "*25)
                print("✅ HACS INSTALLATION COMPLETE!")
                print(f"   Found {len(hacs_entities)} HACS entities")
                print("🎉 "*25 + "\n")
                
                print("📦 Next Steps:")
                print("   1. Click HACS in the sidebar")
                print("   2. Explore integrations and frontend cards")
                print("   3. Install: button-card, card-mod, mini-media-player\n")
                return
            print(f"   Waiting for HACS entities... ({(i+1)*10}s)")
            await asyncio.sleep(10)
        
        print("\n⚠️  HACS entities not detected yet.")
        print("   HACS may still be initializing (can take up to 5 minutes).")
        print("   Check the HACS sidebar item in Home Assistant.\n")


if __name__ == "__main__":
    try:
        asyncio.run(interactive_installation())
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation wizard cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
