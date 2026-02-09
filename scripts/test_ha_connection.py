#!/usr/bin/env python3
"""Quick test of Home Assistant connection"""
import asyncio
import aiohttp
import os
from pathlib import Path

async def test_connection():
    config_path = Path(__file__).parent / ".." / "config" / ".env"
    
    # Load .env
    env_vars = {}
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key.strip()] = value.strip()
    
    token = env_vars.get("HOME_ASSISTANT_TOKEN", os.getenv("HOME_ASSISTANT_TOKEN", ""))
    url = env_vars.get("HOME_ASSISTANT_URL", os.getenv("HOME_ASSISTANT_URL", "http://192.168.1.134:8123"))
    
    print(f"URL: {url}")
    print(f"Token: {token[:30]}...")
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        print(f"\nHeaders: {headers}")
        
        async with session.get(f"{url}/api/", headers=headers) as resp:
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(f"Response: {text}")
            return resp.status == 200

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
