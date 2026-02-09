"""Configuration management for HOME-AI-AUTOMATION."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Keys
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for AI features")
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GROK_API_KEY: str = Field(default="", description="Grok AI API key")
    GOOGLE_CLOUD_API_KEY: str = Field(default="", description="Google Cloud API key")
    GITHUB_COPILOT_TOKEN: str = Field(default="", description="GitHub Copilot token")

    # Home Assistant Configuration
    HOME_ASSISTANT_URL: str = Field(default="http://192.168.1.134:8123", description="Home Assistant URL")
    HOME_ASSISTANT_TOKEN: str = Field(default="", description="Home Assistant long-lived access token")
    HOME_ASSISTANT_VERIFY_SSL: bool = Field(default=False, description="Verify SSL for Home Assistant")

    # Server Configuration
    FLASK_PORT: int = Field(default=5000, description="Flask server port")
    FLASK_HOST: str = Field(default="0.0.0.0", description="Flask server host")  # nosec B104
    FLASK_DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///home_automation.db", description="Database connection URL")

    # MQTT Configuration
    MQTT_BROKER_HOST: str = Field(default="localhost", description="MQTT broker hostname")
    MQTT_BROKER_PORT: int = Field(default=1883, description="MQTT broker port")
    MQTT_USERNAME: str = Field(default="", description="MQTT username")
    MQTT_PASSWORD: str = Field(default="", description="MQTT password")

    # Device Configuration
    DEVICES_CONFIG_PATH: str = Field(default="config/devices.json", description="Path to devices configuration")

    # AI Configuration
    AI_MODEL: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    AI_PROVIDER: str = Field(default="openai", description="Primary AI provider (openai, gemini, grok)")
    AI_FALLBACK_PROVIDERS: str = Field(default="gemini,grok", description="Comma-separated fallback providers")
    AI_TEMPERATURE: float = Field(default=0.7, description="AI temperature setting")
    AI_MAX_TOKENS: int = Field(default=150, description="Maximum tokens for AI responses")

    # Mobile Device Configuration
    ANDROID_DEVICE_IP: str = Field(default="", description="Android device IP address")
    ANDROID_DEVICE_PORT: int = Field(default=8080, description="Android device port")
    MOBILE_CONNECTION_METHOD: str = Field(default="wireless", description="Connection method: wireless, usb, bluetooth")

    # Remote Control Configuration
    ENABLE_TV_REMOTE: bool = Field(default=True, description="Enable TV remote control features")
    TV_DEVICES_CONFIG: str = Field(default="config/tv_devices.json", description="Path to TV devices configuration")

    # Proxmox VE Configuration
    PROXMOX_HOST: str = Field(default="", description="Proxmox VE host IP or hostname")
    PROXMOX_PORT: int = Field(default=8006, description="Proxmox VE port")
    PROXMOX_VERIFY_SSL: bool = Field(default=False, description="Verify SSL for Proxmox VE")
    PROXMOX_USERNAME: str = Field(default="", description="Proxmox VE username (e.g., root@pam)")
    PROXMOX_PASSWORD: str = Field(default="", description="Proxmox VE password")
    PROXMOX_TOKEN_ID: str = Field(default="", description="Proxmox VE API token ID")
    PROXMOX_TOKEN_SECRET: str = Field(default="", description="Proxmox VE API token secret")
    PROXMOX_NODE: str = Field(default="", description="Default Proxmox VE node name")

    # Webhook Configuration
    WEBHOOK_SECRET: str = Field(default="", description="Secret key for webhook validation")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/automation.log", description="Log file path")
