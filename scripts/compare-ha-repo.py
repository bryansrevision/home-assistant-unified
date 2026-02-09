"""
Compare Home Assistant live server (VM 102) with repository data.
Outputs a JSON report to stdout.
"""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "mcp-servers"))

from ha_mcp_client import HomeAssistantMCPClient, MCPConfig

# Load environment variables
load_dotenv(repo_root / "config" / ".env")


def file_to_entity_id(path: Path) -> str | None:
    name = path.stem
    if name.startswith("automation_"):
        return "automation." + name[len("automation_"):]
    return None


async def main():
    config = MCPConfig.from_env()
    async with HomeAssistantMCPClient(config) as client:
        config_data = await client.get_config()
        states = await client.get_all_states()

    # Domain counts
    domain_counts = {}
    for s in states:
        entity_id = s.get("entity_id", "")
        if "." in entity_id:
            domain = entity_id.split(".", 1)[0]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    # Automations from server
    server_automation_ids = sorted(
        [s.get("entity_id") for s in states if s.get("entity_id", "").startswith("automation.")]
    )

    # Repo automations
    automations_dir = repo_root / "automations"
    repo_automation_files = []
    if automations_dir.exists():
        repo_automation_files = [p for p in automations_dir.rglob("*.yaml")]

    repo_automation_entities = [file_to_entity_id(p) for p in repo_automation_files]
    repo_automation_entities = [e for e in repo_automation_entities if e]
    repo_automation_ids = sorted(set(repo_automation_entities))

    server_only = sorted(set(server_automation_ids) - set(repo_automation_ids))
    repo_only = sorted(set(repo_automation_ids) - set(server_automation_ids))

    # Repo integrations overview
    integrations_dir = repo_root / "integrations"
    repo_integrations = []
    if integrations_dir.exists():
        repo_integrations = sorted([p.name for p in integrations_dir.iterdir() if p.is_dir()])

    report = {
        "server": {
            "host": f"{config.host}:{config.port}",
            "version": config_data.get("version"),
            "location": config_data.get("location_name"),
            "time_zone": config_data.get("time_zone"),
            "unit_system": config_data.get("unit_system"),
            "currency": config_data.get("currency"),
        },
        "entities": {
            "total": len(states),
            "domains": domain_counts,
        },
        "automations": {
            "server_count": len(server_automation_ids),
            "repo_count": len(repo_automation_ids),
            "server_only": server_only,
            "repo_only": repo_only,
        },
        "repo": {
            "automation_files": len(repo_automation_files),
            "integrations_dirs": repo_integrations,
        },
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
