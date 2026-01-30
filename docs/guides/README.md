# 🏠 HOME-AI-AUTOMATION

[![CI/CD Pipeline](https://github.com/bryansrevision/HOME-AI-AUTOMATION/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/bryansrevision/HOME-AI-AUTOMATION/actions/workflows/ci-cd.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An intelligent, AI-powered home automation system that enables natural language control of smart devices, advanced automation rules, comprehensive monitoring capabilities, and seamless integration with Home Assistant, mobile devices, and remote TV/media control.

## ✨ Features

### 🤖 AI-Powered Control
- **Multi-AI Provider Support**: OpenAI, Google Gemini, Grok AI with automatic fallback
- **Natural Language Processing**: Control devices using conversational commands
- **Smart Interpretation**: Automatically understands context and intent
- **Response Generation**: Provides natural, helpful feedback

### 🏠 Home Assistant Integration
- **Seamless Connectivity**: Direct integration with Home Assistant at 192.168.1.201
- **Entity Control**: Turn on/off lights, switches, and other entities
- **State Monitoring**: Real-time status of all Home Assistant devices
- **Service Calls**: Execute any Home Assistant service
- **Easy Setup**: Simple configuration with long-lived access tokens

### 📱 Mobile Device Connectivity
- **Android Device Support**: Connect via WiFi, USB (ADB), or Bluetooth
- **Home Assistant App Integration**: Full support for the official companion app
- **Push Notifications**: Send alerts and notifications to mobile devices
- **Connection Testing**: Built-in diagnostics for connectivity issues
- **Multiple Devices**: Manage and control multiple mobile devices

### 📺 Remote Control Features
- **Universal Remote**: Control TVs and media devices from the web interface
- **Wide Device Support**: Samsung TV, Google TV, Android TV, Fire TV, Roku, and more
- **Intuitive UI**: Beautiful web-based remote control with all standard buttons
- **Navigation Controls**: Full directional pad, media controls, and app shortcuts
- **Home Assistant Integration**: Use existing Home Assistant media players

### 🔧 Device Management
- **Smart Lights**: Control brightness, color, and power state
- **Thermostats**: Set temperature, mode, and scheduling
- **Sensors**: Monitor temperature, humidity, motion, and more
- **Extensible Architecture**: Easy to add new device types

### 📊 Monitoring & Analytics
- **Real-time Dashboard**: Web-based control interface
- **Sensor Data Tracking**: Historical data storage and analysis
- **System Health**: Monitor device status and connectivity
- **AI Insights**: Automatic analysis and recommendations

### 🔧 Automation Engine
- **Rule-based Automation**: Create complex automation scenarios
- **Event-driven Actions**: Respond to sensor data and time events
- **Condition Matching**: Advanced trigger conditions
- **Multi-device Coordination**: Control multiple devices simultaneously

### 🌐 API & Integration
- **RESTful API**: Complete programmatic control
- **MQTT Support**: Industry-standard IoT communication
- **Docker Ready**: Containerized deployment
- **Web Dashboard**: Modern, responsive interface

### 💾 Backup & Recovery
- **Automated Backups**: Daily scheduled backups via GitHub Actions
- **API Integration**: Direct Home Assistant API backup creation
- **Version Control**: Backup metadata tracked in Git
- **Retention Management**: Automatic cleanup of old backups
- **Manual Triggers**: On-demand backup creation support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bryansrevision/HOME-AI-AUTOMATION.git
   cd HOME-AI-AUTOMATION
   ```

2. **Set up the environment**
   ```bash
   # Copy environment configuration
   cp .env.example .env
   
   # Edit .env with your settings (especially OpenAI API key)
   nano .env
   ```

3. **Choose deployment method**

   **Option A: Docker Deployment (Recommended)**
   ```bash
   # Make deploy script executable
   chmod +x deploy.sh
   
   # Deploy everything
   ./deploy.sh all
   ```

   **Option B: Manual Development Setup**
   ```bash
   # Set up Python environment
   ./deploy.sh setup
   
   # Run tests
   ./deploy.sh test
   
   # Start the application
   python -m home_automation.main
   ```

4. **Access the dashboard**
   - Open your browser and go to `http://localhost:5000`
   - The API is available at `http://localhost:5000/api/`
   - Remote Control: `http://localhost:5000/remote`
   - Mobile Setup: `http://localhost:5000/mobile`

## 🆕 New Features Setup

### Home Assistant Integration

1. **Get a Long-Lived Access Token**
   - In Home Assistant, go to your profile
   - Scroll to "Long-Lived Access Tokens"
   - Create a new token named "HOME-AI-AUTOMATION"

2. **Configure in `.env`**
   ```bash
   HOME_ASSISTANT_URL=http://192.168.1.201:8123
   HOME_ASSISTANT_TOKEN=your_token_here
   HOME_ASSISTANT_VERIFY_SSL=false
   ```

3. **Test Connection**
   ```bash
   curl http://localhost:5000/api/homeassistant/connection
   ```

### Mobile Device Setup

1. **Install Home Assistant Companion App**
   - Download from Google Play Store
   - Connect to `http://192.168.1.201:8123`
   - Grant necessary permissions

2. **Configure Devices** in `config/mobile_devices.json`

3. **Access Mobile Setup Page**
   - Visit `http://localhost:5000/mobile`
   - Follow the setup instructions

### Remote Control Setup

1. **Configure TV Devices** in `config/tv_devices.json`
   ```json
   {
     "tv_devices": [
       {
         "name": "Living Room TV",
         "type": "samsung_tv",
         "ip_address": "192.168.1.100",
         "entity_id": "media_player.living_room_tv"
       }
     ]
   }
   ```

2. **Access Remote Control**
   - Visit `http://localhost:5000/remote`
   - Select your device from the dropdown
   - Use the on-screen remote

### Multi-AI Provider Setup

Configure multiple AI providers for automatic fallback:

```bash
# Primary provider
AI_PROVIDER=openai
AI_FALLBACK_PROVIDERS=gemini,grok

# API Keys
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
GROK_API_KEY=your_grok_key
```

📖 **Detailed Setup Guide**: See [MOBILE_REMOTE_SETUP.md](MOBILE_REMOTE_SETUP.md) for comprehensive configuration instructions.


## 📖 Usage

### Web Dashboard
Access the main dashboard at `http://localhost:5000` to:
- View all connected devices
- Monitor system status
- Execute natural language commands
- View sensor data and insights

### Natural Language Commands
The system understands natural language commands such as:
- "Turn on the living room light"
- "Set the thermostat to 22 degrees"
- "What's the status of the bedroom light?"
- "Turn off all lights"
- "Set the living room light to 50% brightness"

### API Endpoints

#### Health Check
```bash
curl http://localhost:5000/api/health
```

#### System Status
```bash
curl http://localhost:5000/api/status
```

#### List Devices
```bash
curl http://localhost:5000/api/devices
```

#### Control Device
```bash
curl -X POST http://localhost:5000/api/devices/living_room_light \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on"}'
```

#### Execute Command
```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "turn on the living room light"}'
```

## 🏗️ Architecture

```
HOME-AI-AUTOMATION/
├── home_automation/           # Main application code
│   ├── core/                 # Core system components
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database models and operations
│   │   └── automation_engine.py  # Main automation logic
│   ├── devices/              # Device management
│   │   └── device_manager.py # Device classes and control
│   ├── ai/                   # AI and intelligence
│   │   └── intelligence.py   # Natural language processing
│   ├── api/                  # REST API
│   │   └── routes.py         # API endpoints
│   └── main.py              # Application entry point
├── tests/                    # Test suite
├── templates/                # Web interface templates
├── config/                   # Configuration files
├── .github/workflows/        # CI/CD pipelines
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service deployment
└── deploy.sh               # Deployment automation
```

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env`:

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Settings
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_DEBUG=false

# Database
DATABASE_URL=sqlite:///home_automation.db

# MQTT (Optional)
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

### Device Configuration
Edit `config/devices.json` to define your devices:

```json
{
  "devices": [
    {
      "name": "Living Room Light",
      "type": "light",
      "location": "Living Room"
    },
    {
      "name": "Main Thermostat",
      "type": "thermostat",
      "location": "Living Room"
    }
  ]
}
```

## 🧪 Development

### Running Tests
```bash
# Run all tests
./deploy.sh test

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=home_automation --cov-report=html
```

### Code Quality
```bash
# Run all quality checks
./deploy.sh check

# Individual tools
black home_automation/ tests/        # Code formatting
isort home_automation/ tests/        # Import sorting
flake8 home_automation/ tests/       # Linting
mypy home_automation/                # Type checking
```

### Development Setup
```bash
# Set up development environment
./deploy.sh setup

# Install pre-commit hooks
pre-commit install
```

## 📊 Monitoring

### Application Logs
```bash
# View logs in real-time
./deploy.sh logs

# Or with Docker Compose
docker-compose logs -f home-automation
```

### Health Monitoring
```bash
# Check service status
./deploy.sh status

# Manual health check
curl http://localhost:5000/api/health
```

## 🚀 Deployment

### Production Deployment
1. **Configure environment variables**
2. **Set up SSL certificates** (if using HTTPS)
3. **Deploy with Docker Compose**
   ```bash
   docker-compose --profile production up -d
   ```

### Scaling
- Use Docker Swarm or Kubernetes for horizontal scaling
- Configure load balancer for multiple instances
- Use external database for shared state

## 💾 Automated Backups

### Overview
Automated backup system for Home Assistant that creates daily backups, stores them securely, and tracks metadata in version control.

### Features
- **Scheduled Execution**: Daily backups at 2 AM UTC via GitHub Actions
- **API-Based**: Uses Home Assistant's native backup API
- **Version Control**: Backup metadata committed to Git
- **Artifact Storage**: Backup files stored as GitHub artifacts (7-day retention)
- **Automatic Cleanup**: Old backups removed automatically
- **Manual Triggers**: Run backups on-demand via workflow dispatch
- **Error Reporting**: Comprehensive failure notifications and logs

### Quick Setup

1. **Configure GitHub Secret**:
   ```bash
   # In GitHub repository: Settings → Secrets → Actions
   # Add secret: HA_TOKEN = <your_home_assistant_token>
   ```

2. **Test Locally** (optional):
   ```bash
   # Set environment variables
   export HA_URL="http://192.168.1.201:8123"
   export HA_TOKEN="your_token_here"
   
   # Validate setup
   python scripts/test_backup_setup.py
   
   # Run backup test
   python scripts/ha_backup.py --test-connection
   python scripts/ha_backup.py
   ```

3. **Enable GitHub Actions**:
   - Workflow runs automatically daily
   - Or trigger manually: Actions → Home Assistant Automated Backup → Run workflow

### Documentation
- **Setup Guide**: [scripts/README_BACKUP.md](scripts/README_BACKUP.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Script Documentation**: Inline comments in [scripts/ha_backup.py](scripts/ha_backup.py)

### Backup Locations
- **Artifacts**: Available in GitHub Actions (7 days)
- **Metadata**: Committed to repository in `backups/*.json`
- **Local**: `./backups/` directory when running locally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`./deploy.sh test`)
5. Commit your changes (`git commit -am 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use type hints
- Follow semantic versioning

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- Flask for the web framework
- Docker for containerization
- The open-source community for various libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bryansrevision/HOME-AI-AUTOMATION/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bryansrevision/HOME-AI-AUTOMATION/discussions)
- **Documentation**: [Wiki](https://github.com/bryansrevision/HOME-AI-AUTOMATION/wiki)

---

**Made with ❤️ for smart home enthusiasts**