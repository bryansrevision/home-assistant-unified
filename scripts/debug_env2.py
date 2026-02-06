#!/usr/bin/env python3
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Make sure we're in the right directory
print(f"CWD: {os.getcwd()}")

# Use absolute path
env_file = Path(__file__).parent / "config" / ".env"
print(f"Loading .env from (absolute): {env_file.absolute()}")
print(f"File exists: {env_file.exists()}")

# Force reload - clear any cached values
for key in list(os.environ.keys()):
    if key.startswith(('HOME_ASSISTANT', 'HA_')):
        del os.environ[key]

# Load explicitly
load_dotenv(env_file, override=True)

# Check what we got
token = os.getenv('HOME_ASSISTANT_TOKEN', 'NOT SET')
url = os.getenv('HOME_ASSISTANT_URL', 'NOT SET')

print(f"\nHOME_ASSISTANT_TOKEN={token[:80] if token != 'NOT SET' else token}")
print(f"HOME_ASSISTANT_URL={url}")

# Also check file directly
print(f"\nFile contents (HOME_ASSISTANT_TOKEN line):")
with open(env_file) as f:
    for line in f:
        if 'HOME_ASSISTANT_TOKEN=' in line:
            print(f"  {line[:100]}")
            break
