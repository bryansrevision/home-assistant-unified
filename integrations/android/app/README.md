# HomeAI - Smart Home AI Assistant

A complete Android app for controlling your smart home with AI-powered natural language commands.

## Features

- AI Chat Interface: Control your home with natural language
- Multi-Integration Support: Home Assistant, SmartThings, MQTT, Google Home, Matter
- Modern UI: Jetpack Compose with Material 3 design
- Voice Control: Built-in voice recognition
- Scenes: Quick activation of predefined scenes
- Device Management: View and control all your devices

## Quick Start

### 1. Build the App

```bash
cd android-app
./gradlew assembleDebug
```

### 2. Install via ADB

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 3. Configure Integrations

Open the app and go to Settings to configure:

#### Home Assistant
1. Get a Long-Lived Access Token from your Home Assistant profile
2. Enter your Home Assistant URL (e.g., http://homeassistant.local:8123)
3. Enter the access token
4. Test connection

#### MQTT (for Tasmota, Zigbee2MQTT, ESPHome)
1. Enter your MQTT broker URL (e.g., tcp://192.168.1.100:1883)
2. Enter username and password if required
3. The app auto-discovers devices on common topics

#### SmartThings
1. Create a Personal Access Token at https://account.smartthings.com/tokens
2. Select Devices and Locations scopes
3. Enter the token in settings

#### OpenAI (for AI responses)
1. Get an API key from https://platform.openai.com/api-keys
2. Enter the key in settings
3. The AI will understand natural language commands

## Example Commands

- Turn on the living room lights
- Set bedroom temperature to 72 degrees
- Lock all doors
- Turn off all lights
- Set kitchen brightness to 50 percent
- What devices are currently on?

## Project Structure

```
app/src/main/java/com/homeai/app/
├── MainActivity.kt           # Main entry point
├── HomeAIApplication.kt      # Application class
├── ui/
│   ├── HomeAIApp.kt         # Navigation and main UI
│   ├── chat/                # AI chat interface
│   ├── home/                # Home dashboard
│   ├── devices/             # Device management
│   ├── settings/            # Integration settings
│   └── theme/               # Material 3 theme
├── ai/
│   ├── AIAssistant.kt       # Intent parsing and AI logic
│   └── OpenAIServiceImpl.kt # OpenAI API client
├── integrations/
│   ├── homeassistant/       # Home Assistant REST API
│   ├── mqtt/                # MQTT client (Tasmota, Zigbee2MQTT)
│   ├── smartthings/         # SmartThings API
│   └── googlehome/          # Google Home / Matter
├── models/                  # Data models
├── di/                      # Dependency injection
├── services/                # Background services
└── utils/                   # Utilities and data store
```

## Requirements

- Android 8.0 (API 26) or higher
- Android Studio Hedgehog or newer
- Kotlin 1.9+
- Gradle 8.2+

## License

MIT License
