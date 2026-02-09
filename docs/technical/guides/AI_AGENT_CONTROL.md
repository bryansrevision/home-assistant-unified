# 🤖 AI Agent Control & Integration Guide

## Multi-AI Service Integration

This guide covers integration of multiple AI services for home automation control, SMS management, workflow approvals, and intelligent assistance.

---

## 🧠 AI Services Integration

### Supported AI Platforms

1. **Microsoft Copilot** - Microsoft 365 integration
2. **ChatGPT (OpenAI)** - GPT-4/GPT-3.5 models
3. **Google Gemini Pro** - Google's advanced AI
4. **Perplexity AI** - Research and search
5. **Claude (Anthropic)** - Advanced reasoning
6. **Local LLM** - Privacy-focused local models

---

## 📱 SMS AI Control System

### SMS Command Processing

```yaml
# config/home-assistant/ulefone-sms-ai-control.yaml

automation:
  # SMS Command Processor
  - alias: "AI - Process SMS Commands"
    trigger:
      - platform: event
        event_type: mobile_app_notification_received
        event_data:
          source: sms
    action:
      - service: rest_command.ai_process_sms
        data:
          sender: "{{ trigger.event.data.sender }}"
          message: "{{ trigger.event.data.message }}"
          timestamp: "{{ now().isoformat() }}"

# REST Commands for AI Processing
rest_command:
  ai_process_sms:
    url: 'http://192.168.1.134:5000/api/ai/process_sms'
    method: POST
    content_type: 'application/json'
    payload: >
      {
        "sender": "{{ sender }}",
        "message": "{{ message }}",
        "context": {
          "home_state": "{{ states('input_select.house_mode') }}",
          "location": "{{ states('device_tracker.mobile_app_ulefone') }}",
          "time": "{{ timestamp }}"
        }
      }

  ai_send_sms_response:
    url: 'http://192.168.1.134:3000/api/sms/send'
    method: POST
    content_type: 'application/json'
    payload: >
      {
        "recipient": "{{ recipient }}",
        "message": "{{ message }}",
        "priority": "{{ priority | default('normal') }}"
      }

# SMS AI Agent Script
script:
  sms_ai_agent_response:
    alias: "SMS AI Agent - Generate Response"
    fields:
      message:
        description: "Incoming SMS message"
        example: "Lock the front door"
      sender:
        description: "Sender phone number"
        example: "+1234567890"
    sequence:
      # Step 1: Parse intent with AI
      - service: rest_command.ai_process_sms
        data:
          sender: "{{ sender }}"
          message: "{{ message }}"
      
      # Step 2: Execute action based on intent
      - choose:
          # Lock doors command
          - conditions:
              - condition: template
                value_template: "{{ 'lock' in message.lower() }}"
            sequence:
              - service: lock.lock
                target:
                  entity_id: all
              - service: rest_command.ai_send_sms_response
                data:
                  recipient: "{{ sender }}"
                  message: "All doors have been locked. ✓"
          
          # Turn off lights
          - conditions:
              - condition: template
                value_template: "{{ 'lights off' in message.lower() or 'turn off lights' in message.lower() }}"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: all
              - service: rest_command.ai_send_sms_response
                data:
                  recipient: "{{ sender }}"
                  message: "All lights turned off. ✓"
          
          # Status request
          - conditions:
              - condition: template
                value_template: "{{ 'status' in message.lower() or 'how is' in message.lower() }}"
            sequence:
              - service: rest_command.ai_send_sms_response
                data:
                  recipient: "{{ sender }}"
                  message: >
                    Home Status:
                    🏠 Mode: {{ states('input_select.house_mode') }}
                    🔒 Doors: {{ 'Locked' if is_state('lock.front_door', 'locked') else 'Unlocked' }}
                    💡 Lights: {{ states.light | selectattr('state', 'eq', 'on') | list | count }} on
                    🌡️ Temp: {{ states('sensor.indoor_temperature') }}°F
        default:
          - service: rest_command.ai_send_sms_response
            data:
              recipient: "{{ sender }}"
              message: "I didn't understand that command. Try: 'lock doors', 'lights off', or 'status'"
```

### Authorized SMS Senders

```yaml
# config/home-assistant/sms-authorized-senders.yaml

input_text:
  sms_authorized_numbers:
    name: "Authorized SMS Numbers"
    initial: "+1234567890,+0987654321"  # Comma-separated
    icon: mdi:phone-check

# Verification automation
automation:
  - alias: "SMS - Verify Authorized Sender"
    trigger:
      - platform: event
        event_type: mobile_app_notification_received
        event_data:
          source: sms
    condition:
      - condition: template
        value_template: >
          {{ trigger.event.data.sender in states('input_text.sms_authorized_numbers').split(',') }}
    action:
      - service: script.sms_ai_agent_response
        data:
          message: "{{ trigger.event.data.message }}"
          sender: "{{ trigger.event.data.sender }}"
```

---

## 🔗 AI Service Integrations

### 1. Microsoft Copilot Integration

```yaml
# config/home-assistant/ai-copilot-integration.yaml

rest_command:
  copilot_query:
    url: 'https://api.microsoft.com/copilot/v1/chat'
    method: POST
    headers:
      Authorization: '******
      Content-Type: 'application/json'
    payload: >
      {
        "messages": [
          {
            "role": "system",
            "content": "You are a home automation assistant. Provide concise, actionable responses."
          },
          {
            "role": "user",
            "content": "{{ query }}"
          }
        ],
        "context": {
          "home_status": {
            "mode": "{{ states('input_select.house_mode') }}",
            "temperature": "{{ states('sensor.indoor_temperature') }}",
            "lights_on": {{ states.light | selectattr('state', 'eq', 'on') | list | count }},
            "doors_locked": {{ is_state('lock.front_door', 'locked') }}
          }
        }
      }

script:
  ask_copilot:
    alias: "Ask Microsoft Copilot"
    fields:
      question:
        description: "Question to ask"
        example: "What should I do to optimize energy usage?"
    sequence:
      - service: rest_command.copilot_query
        data:
          query: "{{ question }}"
      - service: notify.mobile_app_ulefone
        data:
          message: "Copilot is analyzing your question..."
          title: "AI Assistant"
```

### 2. ChatGPT (OpenAI) Integration

```yaml
# config/home-assistant/ai-chatgpt-integration.yaml

rest_command:
  chatgpt_query:
    url: 'https://api.openai.com/v1/chat/completions'
    method: POST
    headers:
      Authorization: '******
      Content-Type: 'application/json'
    payload: >
      {
        "model": "gpt-4-turbo-preview",
        "messages": [
          {
            "role": "system",
            "content": "You are a smart home automation expert. Provide brief, specific advice for home automation scenarios."
          },
          {
            "role": "user",
            "content": "{{ query }}"
          }
        ],
        "temperature": 0.7,
        "max_tokens": 500
      }

script:
  ask_chatgpt:
    alias: "Ask ChatGPT"
    fields:
      query:
        description: "Query for ChatGPT"
        example: "Suggest an evening routine for energy savings"
    sequence:
      - service: rest_command.chatgpt_query
        data:
          query: "{{ query }}"
      - delay:
          seconds: 2
      - service: notify.mobile_app_ulefone
        data:
          message: "ChatGPT response received"
          title: "AI Assistant"
```

### 3. Google Gemini Pro Integration

```yaml
# config/home-assistant/ai-gemini-integration.yaml

rest_command:
  gemini_query:
    url: 'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent'
    method: POST
    headers:
      Content-Type: 'application/json'
    payload: >
      {
        "contents": [{
          "parts": [{
            "text": "{{ query }}\n\nContext: Home automation system with current status - Mode: {{ states('input_select.house_mode') }}, Temperature: {{ states('sensor.indoor_temperature') }}°F"
          }]
        }],
        "generationConfig": {
          "temperature": 0.7,
          "maxOutputTokens": 500
        }
      }

script:
  ask_gemini:
    alias: "Ask Google Gemini"
    fields:
      query:
        description: "Query for Gemini"
        example: "Analyze my home's current state and suggest improvements"
    sequence:
      - service: rest_command.gemini_query
        data:
          query: "{{ query }}"
      - service: notify.mobile_app_ulefone
        data:
          message: "Gemini AI analyzing..."
          title: "AI Assistant"
```

### 4. Claude (Anthropic) Integration

```yaml
# config/home-assistant/ai-claude-integration.yaml

rest_command:
  claude_query:
    url: 'https://api.anthropic.com/v1/messages'
    method: POST
    headers:
      x-api-key: '{{ api_key }}'
      anthropic-version: '2023-06-01'
      Content-Type: 'application/json'
    payload: >
      {
        "model": "claude-3-opus-20240229",
        "max_tokens": 500,
        "messages": [{
          "role": "user",
          "content": "{{ query }}\n\nYou are helping manage a smart home. Current state: {{ states('input_select.house_mode') }} mode."
        }]
      }

script:
  ask_claude:
    alias: "Ask Claude AI"
    fields:
      query:
        description: "Query for Claude"
        example: "What security measures should I take before vacation?"
    sequence:
      - service: rest_command.claude_query
        data:
          query: "{{ query }}"
          api_key: !secret claude_api_key
```

### 5. Perplexity AI Integration

```yaml
# config/home-assistant/ai-perplexity-integration.yaml

rest_command:
  perplexity_query:
    url: 'https://api.perplexity.ai/chat/completions'
    method: POST
    headers:
      Authorization: '******
      Content-Type: 'application/json'
    payload: >
      {
        "model": "sonar-medium-online",
        "messages": [{
          "role": "user",
          "content": "{{ query }}"
        }],
        "temperature": 0.7,
        "max_tokens": 500
      }

script:
  ask_perplexity:
    alias: "Ask Perplexity AI"
    fields:
      query:
        description: "Research query"
        example: "What are the latest smart home security recommendations?"
    sequence:
      - service: rest_command.perplexity_query
        data:
          query: "{{ query }}"
```

---

## 🎙️ AI Wearable Integration

### Omi.me DevKit2 Integration

```yaml
# config/home-assistant/ai-wearable-omi.yaml

# Omi.me DevKit2 - AI Wearable
# Features: Always-on voice recording, context-aware assistance

sensor:
  - platform: rest
    name: "Omi Wearable Status"
    resource: 'http://192.168.1.xxx:8080/status'
    method: GET
    value_template: "{{ value_json.status }}"
    json_attributes:
      - battery_level
      - recording_active
      - last_interaction
    scan_interval: 300

# Omi Voice Command Processing
automation:
  - alias: "Omi - Process Voice Command"
    trigger:
      - platform: webhook
        webhook_id: omi_voice_command
    action:
      - service: script.process_ai_command
        data:
          command: "{{ trigger.json.transcript }}"
          source: "omi_wearable"
          confidence: "{{ trigger.json.confidence }}"

# Integration Scripts
script:
  omi_send_notification:
    alias: "Omi - Send Notification"
    fields:
      message:
        description: "Message to send to Omi wearable"
        example: "Door is unlocked"
    sequence:
      - service: rest_command.omi_notify
        data:
          message: "{{ message }}"
          priority: "high"

rest_command:
  omi_notify:
    url: 'http://192.168.1.xxx:8080/notify'
    method: POST
    content_type: 'application/json'
    payload: >
      {
        "message": "{{ message }}",
        "priority": "{{ priority | default('normal') }}",
        "vibrate": true
      }

  omi_start_recording:
    url: 'http://192.168.1.xxx:8080/record/start'
    method: POST

  omi_stop_recording:
    url: 'http://192.168.1.xxx:8080/record/stop'
    method: POST
```

### Bee AI Wearable (Apple) Integration

```yaml
# config/home-assistant/ai-wearable-bee.yaml

# Bee AI Wearable - Apple Integration
# Cross-platform notifications via Home Assistant

automation:
  - alias: "Bee - Sync with Home Assistant"
    trigger:
      - platform: state
        entity_id: input_boolean.bee_wearable_connected
        to: 'on'
    action:
      - service: notify.mobile_app_iphone
        data:
          message: "Bee AI wearable connected"
          data:
            push:
              badge: 0

# Bee voice command webhook
  - alias: "Bee - Process Voice Command"
    trigger:
      - platform: webhook
        webhook_id: bee_voice_command
    action:
      - service: script.process_ai_command
        data:
          command: "{{ trigger.json.command }}"
          source: "bee_wearable"

script:
  bee_send_haptic:
    alias: "Bee - Send Haptic Feedback"
    fields:
      pattern:
        description: "Haptic pattern"
        example: "notification"
    sequence:
      - service: rest_command.bee_haptic
        data:
          pattern: "{{ pattern }}"

rest_command:
  bee_haptic:
    url: 'http://192.168.1.xxx:9090/haptic'
    method: POST
    content_type: 'application/json'
    payload: >
      {
        "pattern": "{{ pattern }}",
        "intensity": "medium"
      }
```

---

## 📋 Workflow Approvals & Webhooks

### Workflow Approval System

```yaml
# config/home-assistant/workflow-approvals.yaml

# Approval Request Tracker
input_boolean:
  pending_approval_vm_restart:
    name: "VM Restart Approval Pending"
    icon: mdi:server-security

  pending_approval_security_disarm:
    name: "Security Disarm Approval Pending"
    icon: mdi:shield-off

  pending_approval_backup_deletion:
    name: "Backup Deletion Approval Pending"
    icon: mdi:delete-alert

# Approval Request Script
script:
  request_approval:
    alias: "Request Workflow Approval"
    fields:
      workflow:
        description: "Workflow name"
        example: "vm_restart"
      details:
        description: "Approval details"
        example: "Restart Proxmox VM 101"
      requester:
        description: "Who requested"
        example: "automated_system"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: |
            🔔 Approval Required
            
            Workflow: {{ workflow }}
            Details: {{ details }}
            Requester: {{ requester }}
            Time: {{ now().strftime('%Y-%m-%d %H:%M') }}
          title: "Workflow Approval"
          data:
            priority: high
            ttl: 0
            actions:
              - action: "APPROVE_{{ workflow | upper }}"
                title: "✓ Approve"
              - action: "DENY_{{ workflow | upper }}"
                title: "✗ Deny"
              - action: "DEFER_{{ workflow | upper }}"
                title: "Later"
      
      - service: input_boolean.turn_on
        target:
          entity_id: "input_boolean.pending_approval_{{ workflow }}"
      
      - service: logbook.log
        data:
          name: "Workflow Approval"
          message: "Approval requested for {{ workflow }}"

# Handle Approval Responses
automation:
  - alias: "Workflow - Handle Approval"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
    action:
      - choose:
          # VM Restart Approved
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'APPROVE_VM_RESTART' }}"
            sequence:
              - service: switch.turn_off
                target:
                  entity_id: switch.proxmox_vm_101
              - delay:
                  seconds: 10
              - service: switch.turn_on
                target:
                  entity_id: switch.proxmox_vm_101
              - service: input_boolean.turn_off
                target:
                  entity_id: input_boolean.pending_approval_vm_restart
              - service: notify.mobile_app_ulefone
                data:
                  message: "VM restart approved and executed"
                  title: "Approval Processed"
          
          # Security Disarm Approved
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.action == 'APPROVE_SECURITY_DISARM' }}"
            sequence:
              - service: alarm_control_panel.alarm_disarm
                target:
                  entity_id: alarm_control_panel.home_security
                data:
                  code: !secret alarm_code
              - service: input_boolean.turn_off
                target:
                  entity_id: input_boolean.pending_approval_security_disarm
          
          # Deny Actions
          - conditions:
              - condition: template
                value_template: "{{ 'DENY_' in trigger.event.data.action }}"
            sequence:
              - service: notify.mobile_app_ulefone
                data:
                  message: "Workflow denied by user"
                  title: "Approval Denied"
              - service: logbook.log
                data:
                  name: "Workflow Approval"
                  message: "Workflow {{ trigger.event.data.action }} denied"
```

### Webhook Configuration

```yaml
# config/home-assistant/webhooks-config.yaml

# Webhook Endpoints
automation:
  # Generic webhook receiver
  - alias: "Webhook - Process Incoming"
    trigger:
      - platform: webhook
        webhook_id: ulefone_generic
        allowed_methods:
          - POST
          - GET
    action:
      - service: notify.mobile_app_ulefone
        data:
          message: "Webhook received: {{ trigger.json }}"
          title: "Webhook Event"
      
      - service: logbook.log
        data:
          name: "Webhook"
          message: "Received from {{ trigger.json.source | default('unknown') }}"

  # IFTTT webhook
  - alias: "Webhook - IFTTT Integration"
    trigger:
      - platform: webhook
        webhook_id: ifttt_trigger
    action:
      - service: script.process_ifttt_action
        data:
          action: "{{ trigger.json.action }}"
          value1: "{{ trigger.json.value1 }}"
          value2: "{{ trigger.json.value2 }}"

  # Tasker webhook
  - alias: "Webhook - Tasker Integration"
    trigger:
      - platform: webhook
        webhook_id: tasker_action
    action:
      - service: script.process_tasker_action
        data:
          task: "{{ trigger.json.task }}"
          parameters: "{{ trigger.json.params }}"

script:
  send_webhook_notification:
    alias: "Send Webhook Notification"
    fields:
      url:
        description: "Webhook URL"
        example: "https://maker.ifttt.com/trigger/event/with/key/YOUR_KEY"
      payload:
        description: "JSON payload"
        example: '{"value1": "test"}'
    sequence:
      - service: rest_command.send_webhook
        data:
          url: "{{ url }}"
          payload: "{{ payload }}"

rest_command:
  send_webhook:
    url: "{{ url }}"
    method: POST
    content_type: 'application/json'
    payload: "{{ payload }}"
```

---

## 🔗 Cross-Service Integration

### Multi-Platform Search & Data Access

```yaml
# config/home-assistant/cross-service-search.yaml

# Universal search script
script:
  universal_search:
    alias: "Universal Cross-Service Search"
    fields:
      query:
        description: "Search query"
        example: "vacation photos 2024"
    sequence:
      # Search Google Drive
      - service: rest_command.search_google_drive
        data:
          query: "{{ query }}"
      
      # Search iCloud
      - service: rest_command.search_icloud
        data:
          query: "{{ query }}"
      
      # Search OneDrive
      - service: rest_command.search_onedrive
        data:
          query: "{{ query }}"
      
      # Search Proxmox storage
      - service: rest_command.search_proxmox_storage
        data:
          query: "{{ query }}"
      
      # Aggregate results
      - service: notify.mobile_app_ulefone
        data:
          message: "Search complete. Results compiled from all services."
          title: "Universal Search"
          data:
            actions:
              - action: "VIEW_RESULTS"
                title: "View Results"

rest_command:
  search_google_drive:
    url: 'https://www.googleapis.com/drive/v3/files'
    method: GET
    headers:
      Authorization: '******
    params:
      q: "{{ query }}"
      fields: "files(id, name, mimeType, modifiedTime)"

  search_icloud:
    url: 'https://api.icloud.com/search'
    method: POST
    headers:
      Authorization: '******
    payload: >
      {
        "query": "{{ query }}",
        "types": ["photos", "documents"]
      }

  search_onedrive:
    url: 'https://graph.microsoft.com/v1.0/me/drive/search(q='{{ query }}')'
    method: GET
    headers:
      Authorization: '******
```

---

## 📱 Next Steps

1. **Configure API Keys**: Add all AI service API keys to `secrets.yaml`
2. **Test SMS Commands**: Send test SMS to verify AI processing
3. **Setup Wearables**: Configure Omi.me and Bee AI devices
4. **Create Workflows**: Design approval workflows for critical actions
5. **Test Webhooks**: Verify IFTTT and Tasker integrations
6. **Enable Cross-Search**: Authorize all cloud services

See [IFTTT_TASKER_ADVANCED.md](./IFTTT_TASKER_ADVANCED.md) for automation platform details.
