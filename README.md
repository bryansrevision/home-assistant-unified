# 🏠 Home Assistant Unified

**A comprehensive, production-ready Home Assistant configuration integrating AI automation, Android devices, Proxmox infrastructure, and wearable technology.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1-blue.svg)](https://www.home-assistant.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Overview

This repository consolidates multiple Home Assistant integrations into a unified, well-organized system:

- **🤖 AI-Powered Automation**: Natural language control with OpenAI, Gemini, and Grok
- **📱 Android Integration**: Native app with full device control
- **🖥️ Proxmox Management**: VM/LXC control and monitoring
- **⌚ Wearables Integration**: Omi Device Kit 2 with MCP protocol
- **🔗 MCP Servers**: Model Context Protocol for advanced integrations
- **📊 Monitoring Stack**: InfluxDB, Grafana, MQTT

## 📋 Quick Info

| Component | Details |
|-----------|---------|
| **Home Assistant** | 192.168.1.201:8123 (263 entities) |
| **Proxmox Host** | 192.168.1.185:8006 |
| **Automation Engine** | Port 5000 (Flask/Python) |
| **MQTT Broker** | Port 1883 (Mosquitto) |
| **InfluxDB** | Port 8086 |
| **Grafana** | Port 3000 |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Home Assistant (2024.1+)
- Proxmox VE (optional)
- Python 3.8+

### Installation

```bash
# Clone repository
git clone https://github.com/bryansrevision/home-assistant-unified.git
cd home-assistant-unified

# Copy environment template
cp config/.env.example config/.env

# Edit configuration
nano config/.env

# Start services
docker-compose up -d

# Verify installation
./scripts/setup/health-check.sh
```

## 📁 Repository Structure

```
home-assistant-unified/
├── core/                      # Home Assistant core configuration
├── mcp-servers/               # Model Context Protocol servers
├── automation-engine/         # AI automation engine (Python/Flask)
├── integrations/
│   ├── android/              # Android app and configs
│   ├── proxmox/              # VM/LXC management
│   ├── wearables/            # Omi wearables integration
│   └── mqtt/                 # MQTT broker configs
├── automations/              # Home Assistant automations
├── services/                 # Docker services
├── scripts/                  # Setup and maintenance scripts
├── docs/                     # Documentation
└── monitoring/               # Grafana dashboards
```

## 🔧 Features

### AI-Powered Automation
- Multi-provider AI support (OpenAI, Gemini, Grok)
- Natural language device control
- Intelligent scene management
- Context-aware responses

### Android Integration
- Native Material Design 3 app
- Real-time entity control
- Background sync
- Secure encrypted storage

### Proxmox Management
- VM start/stop/restart
- Resource monitoring
- Automated alerts
- API integration

### Wearables Support
- Omi Device Kit 2 integration
- Memory processing with Bee AI
- Health monitoring
- Task extraction from conversations

### MCP Servers
- **Omi MCP**: Wearable device integration
- **Home Assistant MCP**: HA control via MCP
- **Proxmox MCP**: Infrastructure management  
- **GitHub MCP**: Repository automation

## 📖 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Android Setup](docs/guides/android-setup.md)
- [Proxmox Integration](docs/guides/proxmox-setup.md)
- [MCP Configuration](docs/guides/mcp-setup.md)
- [AI Control Guide](docs/guides/ai-control.md)
- [Wearables Setup](docs/guides/wearables-setup.md)
- [API Reference](docs/api/REST_API.md)
- [MQTT Topics](docs/api/MQTT_TOPICS.md)
- [Troubleshooting](docs/troubleshooting/)

## 🔐 Security

- **Environment Variables**: All secrets in `.env` (not committed)
- **Token Authentication**: API tokens for all services
- **SSL/TLS**: Encrypted connections where applicable
- **Rate Limiting**: DDoS protection configured
- **Secret Rotation**: 90-day rotation policy

See [SECURITY.md](SECURITY.md) for detailed security practices.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test specific integration
pytest tests/test_android_integration.py

# Validate Home Assistant config
./scripts/setup/validate-ha-config.sh
```

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **Home Assistant Community**
- **Omi Device Team**
- **Model Context Protocol**
- **Proxmox VE**

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join Server](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/bryansrevision/home-assistant-unified/issues)

## 🗺️ Roadmap

- [ ] Voice assistant integration
- [ ] Machine learning automation
- [ ] Advanced energy management
- [ ] Multi-location support
- [ ] Mobile app iOS version

---

**Built with ❤️ for the smart home community**
