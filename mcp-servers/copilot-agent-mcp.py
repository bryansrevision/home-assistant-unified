#!/usr/bin/env python3
"""
GitHub Copilot Agent MCP Server for Home Assistant
Enables bidirectional control between Copilot CLI and Home Assistant
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import aiohttp
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("copilot-agent-mcp")

# Load environment
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_file, override=True)


@dataclass
class HAConfig:
    """Home Assistant configuration"""
    url: str = os.getenv("HOME_ASSISTANT_URL", "http://192.168.1.134:8123")
    token: str = os.getenv("HOME_ASSISTANT_TOKEN", "")
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }


class CopilotAgentMCP:
    """Copilot Agent MCP Server for Home Assistant integration"""
    
    def __init__(self, config: HAConfig = None):
        self.config = config or HAConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.command_history: List[Dict] = []
        
    async def start(self):
        """Start the MCP server"""
        self.session = aiohttp.ClientSession()
        logger.info(f"Copilot Agent MCP started - HA: {self.config.url}")
        
    async def stop(self):
        """Stop the MCP server"""
        if self.session:
            await self.session.close()
        logger.info("Copilot Agent MCP stopped")
    
    # =========================================================================
    # Home Assistant API Methods
    # =========================================================================
    
    async def get_states(self, domain: str = None) -> List[Dict]:
        """Get all entity states or filter by domain"""
        async with self.session.get(
            f"{self.config.url}/api/states",
            headers=self.config.headers
        ) as resp:
            states = await resp.json()
            if domain:
                states = [s for s in states if s["entity_id"].startswith(f"{domain}.")]
            return states
    
    async def get_state(self, entity_id: str) -> Dict:
        """Get single entity state"""
        async with self.session.get(
            f"{self.config.url}/api/states/{entity_id}",
            headers=self.config.headers
        ) as resp:
            return await resp.json()
    
    async def call_service(self, domain: str, service: str, data: Dict = None) -> Dict:
        """Call a Home Assistant service"""
        async with self.session.post(
            f"{self.config.url}/api/services/{domain}/{service}",
            headers=self.config.headers,
            json=data or {}
        ) as resp:
            result = await resp.json()
            self._log_command("service_call", f"{domain}.{service}", data)
            return result
    
    async def fire_event(self, event_type: str, event_data: Dict = None) -> Dict:
        """Fire a Home Assistant event"""
        async with self.session.post(
            f"{self.config.url}/api/events/{event_type}",
            headers=self.config.headers,
            json=event_data or {}
        ) as resp:
            return await resp.json()
    
    async def get_config(self) -> Dict:
        """Get Home Assistant configuration"""
        async with self.session.get(
            f"{self.config.url}/api/config",
            headers=self.config.headers
        ) as resp:
            return await resp.json()
    
    async def get_services(self) -> List[Dict]:
        """Get available services"""
        async with self.session.get(
            f"{self.config.url}/api/services",
            headers=self.config.headers
        ) as resp:
            return await resp.json()
    
    # =========================================================================
    # Copilot Agent Commands
    # =========================================================================
    
    async def execute_command(self, command: str, params: Dict = None) -> Dict:
        """Execute a Copilot agent command"""
        params = params or {}
        result = {"success": False, "command": command, "timestamp": datetime.now().isoformat()}
        
        try:
            # Parse command type
            cmd_lower = command.lower().strip()
            
            # Light commands
            if cmd_lower.startswith("turn on") or cmd_lower.startswith("turn off"):
                result = await self._handle_switch_command(cmd_lower, params)
            
            # Scene commands
            elif cmd_lower.startswith("activate scene") or cmd_lower.startswith("set scene"):
                result = await self._handle_scene_command(cmd_lower, params)
            
            # Climate commands
            elif "temperature" in cmd_lower or "thermostat" in cmd_lower:
                result = await self._handle_climate_command(cmd_lower, params)
            
            # Media commands
            elif any(x in cmd_lower for x in ["play", "pause", "stop", "volume", "media"]):
                result = await self._handle_media_command(cmd_lower, params)
            
            # Automation commands
            elif "automation" in cmd_lower or "trigger" in cmd_lower:
                result = await self._handle_automation_command(cmd_lower, params)
            
            # Query commands
            elif cmd_lower.startswith("get") or cmd_lower.startswith("show") or cmd_lower.startswith("list"):
                result = await self._handle_query_command(cmd_lower, params)
            
            # Script commands
            elif cmd_lower.startswith("run script") or cmd_lower.startswith("execute script"):
                result = await self._handle_script_command(cmd_lower, params)
            
            # Notification commands
            elif "notify" in cmd_lower or "send" in cmd_lower:
                result = await self._handle_notification_command(cmd_lower, params)
            
            # Raw service call
            elif "call service" in cmd_lower:
                result = await self._handle_raw_service(cmd_lower, params)
            
            else:
                result["error"] = f"Unknown command: {command}"
                result["hint"] = "Try: turn on/off, activate scene, get states, run script"
            
            self._log_command("execute", command, result)
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            result["error"] = str(e)
        
        return result
    
    async def _handle_switch_command(self, command: str, params: Dict) -> Dict:
        """Handle turn on/off commands"""
        action = "turn_on" if "turn on" in command else "turn_off"
        
        # Extract entity from command or params
        entity_id = params.get("entity_id")
        if not entity_id:
            # Try to parse from command
            parts = command.replace("turn on", "").replace("turn off", "").strip().split()
            if parts:
                entity_hint = "_".join(parts)
                # Search for matching entity
                states = await self.get_states()
                for state in states:
                    if entity_hint in state["entity_id"]:
                        entity_id = state["entity_id"]
                        break
        
        if not entity_id:
            return {"success": False, "error": "Entity not found. Specify entity_id in params."}
        
        domain = entity_id.split(".")[0]
        await self.call_service(domain, action, {"entity_id": entity_id})
        
        return {"success": True, "action": action, "entity_id": entity_id}
    
    async def _handle_scene_command(self, command: str, params: Dict) -> Dict:
        """Handle scene activation"""
        scene_id = params.get("scene_id") or params.get("entity_id")
        
        if not scene_id:
            # Extract from command
            scene_name = command.replace("activate scene", "").replace("set scene", "").strip()
            scene_id = f"scene.{scene_name.replace(' ', '_').lower()}"
        
        await self.call_service("scene", "turn_on", {"entity_id": scene_id})
        return {"success": True, "action": "scene_activated", "scene_id": scene_id}
    
    async def _handle_climate_command(self, command: str, params: Dict) -> Dict:
        """Handle climate/thermostat commands"""
        entity_id = params.get("entity_id", "climate.thermostat")
        
        if "set" in command and "temperature" in command:
            # Extract temperature
            import re
            temps = re.findall(r'\d+', command)
            if temps:
                temp = int(temps[0])
                await self.call_service("climate", "set_temperature", {
                    "entity_id": entity_id,
                    "temperature": temp
                })
                return {"success": True, "action": "set_temperature", "temperature": temp}
        
        return {"success": False, "error": "Could not parse climate command"}
    
    async def _handle_media_command(self, command: str, params: Dict) -> Dict:
        """Handle media player commands"""
        entity_id = params.get("entity_id", "media_player.living_room")
        
        if "play" in command:
            await self.call_service("media_player", "media_play", {"entity_id": entity_id})
            return {"success": True, "action": "play", "entity_id": entity_id}
        elif "pause" in command:
            await self.call_service("media_player", "media_pause", {"entity_id": entity_id})
            return {"success": True, "action": "pause", "entity_id": entity_id}
        elif "stop" in command:
            await self.call_service("media_player", "media_stop", {"entity_id": entity_id})
            return {"success": True, "action": "stop", "entity_id": entity_id}
        elif "volume" in command:
            import re
            vols = re.findall(r'\d+', command)
            if vols:
                vol = min(100, max(0, int(vols[0]))) / 100
                await self.call_service("media_player", "volume_set", {
                    "entity_id": entity_id,
                    "volume_level": vol
                })
                return {"success": True, "action": "volume_set", "volume": vol}
        
        return {"success": False, "error": "Unknown media command"}
    
    async def _handle_automation_command(self, command: str, params: Dict) -> Dict:
        """Handle automation commands"""
        entity_id = params.get("entity_id")
        
        if "trigger" in command:
            if entity_id:
                await self.call_service("automation", "trigger", {"entity_id": entity_id})
                return {"success": True, "action": "triggered", "entity_id": entity_id}
        elif "reload" in command:
            await self.call_service("automation", "reload", {})
            return {"success": True, "action": "reload"}
        elif "list" in command:
            states = await self.get_states("automation")
            return {"success": True, "automations": [s["entity_id"] for s in states]}
        
        return {"success": False, "error": "Specify automation entity_id"}
    
    async def _handle_query_command(self, command: str, params: Dict) -> Dict:
        """Handle query/get commands"""
        if "states" in command or "entities" in command:
            domain = params.get("domain")
            states = await self.get_states(domain)
            return {
                "success": True,
                "count": len(states),
                "entities": [{"entity_id": s["entity_id"], "state": s["state"]} for s in states[:50]]
            }
        elif "config" in command:
            config = await self.get_config()
            return {"success": True, "config": config}
        elif "services" in command:
            services = await self.get_services()
            return {"success": True, "services": [s["domain"] for s in services]}
        
        return {"success": False, "error": "Unknown query type"}
    
    async def _handle_script_command(self, command: str, params: Dict) -> Dict:
        """Handle script execution"""
        script_id = params.get("entity_id") or params.get("script_id")
        
        if not script_id:
            script_name = command.replace("run script", "").replace("execute script", "").strip()
            script_id = f"script.{script_name.replace(' ', '_').lower()}"
        
        await self.call_service("script", "turn_on", {"entity_id": script_id})
        return {"success": True, "action": "script_executed", "script_id": script_id}
    
    async def _handle_notification_command(self, command: str, params: Dict) -> Dict:
        """Handle notification commands"""
        message = params.get("message", command)
        target = params.get("target", "notify.mobile_app")
        title = params.get("title", "Copilot Agent")
        
        await self.call_service("notify", target.replace("notify.", ""), {
            "message": message,
            "title": title
        })
        return {"success": True, "action": "notification_sent", "target": target}
    
    async def _handle_raw_service(self, command: str, params: Dict) -> Dict:
        """Handle raw service calls"""
        domain = params.get("domain")
        service = params.get("service")
        data = params.get("data", {})
        
        if domain and service:
            result = await self.call_service(domain, service, data)
            return {"success": True, "result": result}
        
        return {"success": False, "error": "Specify domain, service, and data in params"}
    
    def _log_command(self, cmd_type: str, command: str, result: Any):
        """Log command execution"""
        self.command_history.append({
            "type": cmd_type,
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 100 commands
        self.command_history = self.command_history[-100:]


# =============================================================================
# HTTP API Server
# =============================================================================

class CopilotAgentServer:
    """HTTP server for Copilot Agent MCP"""
    
    def __init__(self, agent: CopilotAgentMCP, host: str = "0.0.0.0", port: int = 8888):
        self.agent = agent
        self.host = host
        self.port = port
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        self.app.router.add_get("/", self._handle_root)
        self.app.router.add_get("/api/health", self._handle_health)
        self.app.router.add_post("/api/execute", self._handle_execute)
        self.app.router.add_get("/api/states", self._handle_states)
        self.app.router.add_get("/api/states/{entity_id}", self._handle_state)
        self.app.router.add_post("/api/services/{domain}/{service}", self._handle_service)
        self.app.router.add_get("/api/history", self._handle_history)
    
    async def _handle_root(self, request: web.Request) -> web.Response:
        """Root endpoint"""
        return web.json_response({
            "name": "Copilot Agent MCP Server",
            "version": "1.0.0",
            "status": "running",
            "endpoints": [
                "GET /api/health",
                "POST /api/execute",
                "GET /api/states",
                "GET /api/states/{entity_id}",
                "POST /api/services/{domain}/{service}",
                "GET /api/history"
            ]
        })
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        try:
            config = await self.agent.get_config()
            return web.json_response({
                "status": "healthy",
                "ha_version": config.get("version"),
                "ha_connected": True,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "ha_connected": False
            }, status=503)
    
    async def _handle_execute(self, request: web.Request) -> web.Response:
        """Execute Copilot command"""
        try:
            data = await request.json()
            command = data.get("command", "")
            params = data.get("params", {})
            
            result = await self.agent.execute_command(command, params)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_states(self, request: web.Request) -> web.Response:
        """Get all states"""
        domain = request.query.get("domain")
        states = await self.agent.get_states(domain)
        return web.json_response({"states": states, "count": len(states)})
    
    async def _handle_state(self, request: web.Request) -> web.Response:
        """Get single entity state"""
        entity_id = request.match_info["entity_id"]
        state = await self.agent.get_state(entity_id)
        return web.json_response(state)
    
    async def _handle_service(self, request: web.Request) -> web.Response:
        """Call a service"""
        domain = request.match_info["domain"]
        service = request.match_info["service"]
        try:
            data = await request.json()
        except:
            data = {}
        
        result = await self.agent.call_service(domain, service, data)
        return web.json_response(result)
    
    async def _handle_history(self, request: web.Request) -> web.Response:
        """Get command history"""
        limit = int(request.query.get("limit", 20))
        history = self.agent.command_history[-limit:]
        return web.json_response({"history": history})
    
    async def start(self):
        """Start the server"""
        await self.agent.start()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"Copilot Agent MCP Server running on http://{self.host}:{self.port}")
    
    def run(self):
        """Run the server (blocking)"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        loop.run_forever()


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Copilot Agent MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8888, help="Server port")
    parser.add_argument("--test", action="store_true", help="Run test commands")
    
    args = parser.parse_args()
    
    # Create agent
    agent = CopilotAgentMCP()
    
    if args.test:
        # Test mode
        await agent.start()
        
        print("\n🧪 Testing Copilot Agent MCP...\n")
        
        # Test commands
        tests = [
            ("get states", {"domain": "light"}),
            ("get config", {}),
            ("list automations", {}),
        ]
        
        for cmd, params in tests:
            print(f"Command: {cmd}")
            result = await agent.execute_command(cmd, params)
            print(f"Result: {json.dumps(result, indent=2)[:500]}...\n")
        
        await agent.stop()
    else:
        # Server mode
        server = CopilotAgentServer(agent, args.host, args.port)
        await server.start()
        
        # Keep running
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
