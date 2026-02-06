#!/usr/bin/env python3
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env
env_file = Path("config/.env")
print(f"Loading .env from: {env_file.absolute()}")
result = load_dotenv(env_file)
print(f"Load result: {result}")

# Check what we got
token = os.getenv('HOME_ASSISTANT_TOKEN', 'NOT SET')
print(f"\nHOME_ASSISTANT_TOKEN={token[:80]}")

host_option1 = os.getenv('HA_HOST', 'NOT SET')
host_option2 = os.getenv('HOME_ASSISTANT_URL', 'NOT SET')
print(f"HA_HOST={host_option1}")
print(f"HOME_ASSISTANT_URL={host_option2}")

port = os.getenv('HOME_ASSISTANT_PORT', 'NOT SET')
print(f"HOME_ASSISTANT_PORT={port}")
