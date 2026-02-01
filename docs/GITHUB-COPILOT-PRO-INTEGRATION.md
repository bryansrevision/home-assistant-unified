# GitHub Copilot Pro Integration Guide
# Integration with VS Code for AI-powered development
# Last Updated: February 1, 2026

## Overview

GitHub Copilot Pro is an AI-powered code completion tool that integrates with VS
Code and other IDEs. While it's not directly a Home Assistant integration, it
can significantly enhance your Home Assistant development workflow.

## Features

### 1. Code Completion
- Auto-complete YAML configurations
- Suggest automation triggers and conditions
- Generate template sensors and scripts
- Complete Jinja2 templates

### 2. Chat Interface
- Ask questions about Home Assistant
- Get help with configuration
- Debug automation issues
- Generate documentation

### 3. Inline Chat
- Quick code suggestions
- Fix syntax errors
- Refactor configurations
- Add comments and documentation

## Setup Instructions

### Prerequisites
- GitHub account with Copilot Pro subscription
- VS Code installed
- Home Assistant workspace open in VS Code

### Installation Steps

#### 1. Subscribe to GitHub Copilot Pro
```
1. Go to https://github.com/settings/copilot
2. Subscribe to GitHub Copilot Pro ($10/month)
3. Or use GitHub Copilot Business (if available through organization)
```

#### 2. Install VS Code Extension
```
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Install both:
   - GitHub Copilot
   - GitHub Copilot Chat
5. Sign in with your GitHub account
6. Authorize VS Code
```

#### 3. Configure for Home Assistant
Create `.vscode/settings.json` in your workspace:

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true,
    "plaintext": true
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "copilot-codex",
    "debug.testOverrideProxyUrl": "",
    "debug.overrideProxyUrl": ""
  },
  "github.copilot.editor.enableAutoCompletions": true,
  "[yaml]": {
    "editor.quickSuggestions": {
      "other": true,
      "comments": false,
      "strings": true
    }
  }
}
```

#### 4. Add Home Assistant Context
Create `.github/copilot-instructions.md`:

```markdown
# Home Assistant Development Context

This is a Home Assistant configuration repository.

## Key Information
- Platform: Home Assistant 2025.12.5
- Configuration: YAML-based
- Integrations: Alexa, SmartThings, IFTTT, Join, Tasker
- AI Services: OpenAI GPT-4, Google Gemini
- Smart Home Hub: 192.168.1.201:8123

## Coding Standards
- Use YAML syntax for all configurations
- Follow Home Assistant naming conventions
- Include comments for complex automations
- Use secrets.yaml for sensitive data
- Template sensors use Jinja2 syntax

## Common Tasks
- Creating automations
- Setting up integrations
- Writing template sensors
- Configuring notifications
- Debugging YAML syntax
```

### 5. Using Copilot with Home Assistant

#### Auto-Complete Example
Start typing in a YAML file:
```yaml
# Type: automation for motion detected
# Copilot will suggest:

automation:
  - alias: "Motion Detected - Turn On Lights"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

#### Chat Examples

**Ask Copilot:**
```
"Create an automation that turns on lights when motion is detected after sunset"

"How do I integrate Alexa with Home Assistant?"

"Debug this automation: [paste automation]"

"Generate a template sensor for battery levels"
```

#### Inline Chat (Ctrl+I)
Select code and ask:
- "Explain this automation"
- "Add error handling"
- "Convert to template"
- "Add comments"

## Best Practices

### 1. Provide Context
```yaml
# BAD - No context
automation:

# GOOD - With context
# Automation to control lights based on motion detection
# Triggers when motion sensor in living room detects movement
automation:
```

### 2. Use Comments for Complex Logic
```yaml
automation:
  - alias: "Smart Lighting - Evening Mode"
    # Trigger at sunset or when someone comes home
    trigger:
      # ... Copilot will better understand your intent
```

### 3. Ask Specific Questions
```
# Generic: "How do I use templates?"
# Specific: "Create a template sensor that shows battery level as a percentage"
```

### 4. Iterate on Suggestions
- Accept suggestion (Tab)
- Reject suggestion (Esc)
- See next suggestion (Alt+])
- See previous suggestion (Alt+[)

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Accept suggestion | Tab | Tab |
| Reject suggestion | Esc | Esc |
| Next suggestion | Alt+] | Option+] |
| Previous suggestion | Alt+[ | Option+[ |
| Open Copilot Chat | Ctrl+Shift+I | Cmd+Shift+I |
| Inline Chat | Ctrl+I | Cmd+I |
| Toggle Copilot | Ctrl+Alt+\ | Cmd+Option+\ |

## Integration with Home Assistant Workflow

### 1. Configuration Creation
```yaml
# Start with a comment describing what you want
# Copilot will suggest the complete configuration

# Create a sensor that monitors internet speed
sensor:
  # Copilot suggests REST sensor, speedtest integration, etc.
```

### 2. Automation Development
```yaml
# Describe the automation behavior
# Example: Turn on porch light 30 minutes before sunset

automation:
  - alias: "Porch Light - Before Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.porch
```

### 3. Template Debugging
```yaml
# Ask Copilot to explain or fix Jinja2 templates
# Example:
sensor:
  - platform: template
    sensors:
      garage_door_status:
        # Select template and ask: "Why isn't this working?"
        value_template: >
          {% if states('binary_sensor.garage_door') == 'on' %}
            Open
          {% else %}
            Closed
          {% endif %}
```

### 4. Integration Setup
Ask Copilot Chat:
```
"Show me how to set up the OpenAI conversation integration"
"Configure MQTT for Zigbee2MQTT"
"Add notification service for mobile app"
```

## Common Copilot Prompts for Home Assistant

### Automations
- "Create automation for bedtime routine"
- "Motion-activated lights with timeout"
- "Notify when door left open"
- "Climate control based on presence"

### Sensors
- "Template sensor for combined battery status"
- "Calculate energy usage costs"
- "Track device uptime"
- "Monitor API response times"

### Scripts
- "Notification script with iOS actions"
- "Multi-room audio control"
- "Backup configuration script"
- "Device health check"

### Integrations
- "Configure Alexa media player"
- "Setup SmartThings devices"
- "IFTTT webhook integration"
- "Android device tracking"

## Troubleshooting

### Copilot Not Working
1. Check GitHub Copilot status: https://www.githubstatus.com/
2. Sign out and sign in: Ctrl+Shift+P → "GitHub Copilot: Sign Out"
3. Reload VS Code: Ctrl+Shift+P → "Developer: Reload Window"
4. Check subscription: https://github.com/settings/copilot

### Poor Suggestions
1. Add more context in comments
2. Use `.github/copilot-instructions.md`
3. Provide examples of desired output
4. Use more specific language

### YAML Syntax Issues
1. Install YAML extension for VS Code
2. Enable YAML validation
3. Use Home Assistant VS Code extension
4. Check indentation (2 spaces)

## Advanced Features

### 1. Custom Instructions
Create workspace-specific instructions:
```markdown
# .vscode/copilot-workspace.md

When generating automations:
- Always include alias
- Use descriptive entity IDs
- Add comments for triggers
- Include error handling
```

### 2. Multi-File Context
Copilot uses:
- Open editor tabs
- Recently accessed files
- Git repository context
- Workspace structure

### 3. Code Review
Use Copilot Chat for:
- "Review this automation"
- "Find potential issues"
- "Suggest improvements"
- "Check best practices"

## Cost Considerations

- **Copilot Pro**: $10/month individual
- **Copilot Business**: $19/user/month (organization)
- **Copilot Enterprise**: $39/user/month (enterprise features)

Free alternatives:
- GitHub Copilot for Students (verify student status)
- GitHub Copilot for Open Source (apply for access)

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Copilot Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [Copilot Chat Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat)
- [Home Assistant VS Code Extension](https://marketplace.visualstudio.com/items?itemName=keesschollaart.vscode-home-assistant)

## Integration Status

✅ **GitHub Copilot Pro** - IDE integration for AI-assisted coding
- Platform: VS Code, JetBrains IDEs, Neovim, etc.
- Not a Home Assistant integration
- Enhances Home Assistant configuration development
- Works with YAML, Python, Jinja2 templates

## Next Steps

1. ✅ Subscribe to GitHub Copilot Pro
2. ✅ Install VS Code extensions
3. ✅ Configure workspace settings
4. ✅ Add context files
5. ✅ Start using Copilot for Home Assistant development

## Note

GitHub Copilot Pro is a development tool, not a Home Assistant integration. It
assists in writing and debugging Home Assistant configurations but does not
directly integrate with your Home Assistant instance.

For AI integrations within Home Assistant itself, see:
- `ai-assistant-integration.yaml` - OpenAI and Google Gemini
- `alexa-integration.yaml` - Amazon Alexa
- `google-home-integration.yaml` - Google Assistant

