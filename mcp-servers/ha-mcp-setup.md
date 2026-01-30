# Home Assistant MCP Setup

## Preconditions
- HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN set
- MCP server config present in ha-mcp-config.yaml

## Steps
1. Create a long-lived token in Home Assistant.
2. Update .env with HOME_ASSISTANT_TOKEN.
3. Validate access:
   - GET /api/ using token header.

## Validation
- Home Assistant returns 200 and basic API info.
