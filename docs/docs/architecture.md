# System Architecture

## Overview

This document describes the architecture of the Android home automation integration with the Proxmox VE infrastructure.

## Infrastructure Layout

### Proxmox VE Host
- **IP Address**: 192.168.1.185:8006
- **Resources**: 3 Virtual Machines, 5 LXC Containers
- **Role**: Virtualization platform hosting all services

### Virtual Machines and Containers

#### VM 1: Home Assistant
- **IP**: 192.168.1.134
- **Services**:
  - Home Assistant Core (Port 8123)
  - 263 entities configured
- **Purpose**: Central home automation hub

#### Container/VM: Communication Services
- **Services**:
  - Unified MCP Hub (Port 3000, TypeScript)
  - HOME-AI-AUTOMATION (Port 5000, Python/Flask)
  - MQTT Mosquitto (Port 1883)
  - Zigbee2MQTT
- **Purpose**: Service orchestration and IoT communication

#### Container: Data Services
- **Services**:
  - CloudDataSync
  - Configuration backups
- **Purpose**: Data persistence and synchronization

#### Container: Security Services
- **Services**:
  - Bitwarden (self-hosted option)
  - Tailscale VPN coordination node
- **Purpose**: Authentication and secure access

## Network Architecture

```
Internet
   |
   | Tailscale VPN
   |
Android Device <--[VPN Tunnel]--> Proxmox Network (192.168.1.0/24)
   |                                    |
   |                                    +-- Home Assistant (192.168.1.134:8123)
   |                                    +-- MCP Hub (192.168.1.134:3000)
   |                                    +-- AI Automation (192.168.1.134:5000)
   |                                    +-- MQTT Broker (192.168.1.134:1883)
   |                                    +-- Proxmox Host (192.168.1.185:8006)
   |
   +-- Home Assistant App
   +-- MQTT Client
   +-- Bitwarden App
   +-- Tailscale App
```

## Communication Patterns

### Home Assistant Integration
1. **HTTP/HTTPS**: REST API calls from Android app to Home Assistant
2. **WebSocket**: Real-time state updates and notifications
3. **Webhook**: Android device sensors reporting to Home Assistant

### MQTT Communication
1. **Pub/Sub**: Device state updates and commands
2. **QoS Levels**: Configurable message delivery guarantees
3. **Retained Messages**: State persistence

### MCP Hub Communication
1. **WebSocket**: Bidirectional service communication
2. **Event Bus**: Service orchestration events
3. **REST API**: External service integration

### AI Automation
1. **REST API**: Automation triggers and queries
2. **WebSocket**: Real-time automation status
3. **MQTT Integration**: IoT device automation

## Security Layers

### Layer 1: Network Security
- Tailscale VPN for remote access
- Local network isolation
- Firewall rules on Proxmox

### Layer 2: Application Security
- HTTPS/TLS for all web interfaces
- MQTT authentication and ACLs
- API tokens for service authentication

### Layer 3: Credential Management
- Bitwarden for password storage
- API key rotation
- Secure credential injection

### Layer 4: Device Security
- Android device authentication
- Certificate pinning
- Biometric authentication support

## Data Flow

### Device State Update
```
Physical Device (Zigbee)
  → Zigbee2MQTT
  → MQTT Broker
  → Home Assistant
  → WebSocket
  → Android App
```

### User Command
```
Android App
  → HTTPS/REST API
  → Home Assistant
  → Service Call
  → Device Controller
  → Physical Device
```

### Automation Trigger
```
Sensor Event
  → Home Assistant
  → AI Automation (Python/Flask)
  → MCP Hub (Orchestration)
  → Multiple Device Actions
  → Android Notification
```

## Scalability Considerations

### Horizontal Scaling
- Additional LXC containers for load distribution
- MQTT broker clustering capability
- Database replication for Home Assistant

### Vertical Scaling
- Proxmox resource allocation
- Container memory/CPU adjustments
- Storage expansion

## Backup Strategy

### Configuration Backups
- Home Assistant configuration files
- MQTT broker configuration
- Script and automation backups
- Frequency: Daily

### State Backups
- Home Assistant database
- Historical data
- Frequency: Weekly

### CloudDataSync Integration
- Automated backup to cloud storage
- Encryption at rest
- Restore procedures documented

## Monitoring and Logging

### Service Monitoring
- Health check endpoints
- Service status reporting
- Automated alerts

### Performance Metrics
- Response time monitoring
- Resource utilization
- Network latency

### Log Aggregation
- Centralized logging
- Log rotation
- Debug level configuration

## Disaster Recovery

### Recovery Time Objective (RTO)
- Critical services: < 1 hour
- Full restoration: < 4 hours

### Recovery Point Objective (RPO)
- Configuration: < 24 hours
- State data: < 1 week

### Recovery Procedures
1. Restore Proxmox snapshots
2. Restore configuration from CloudDataSync
3. Validate service connectivity
4. Restore Android app connections
