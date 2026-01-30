package com.homeai.app.models

import java.util.UUID

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val content: String,
    val isFromUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val deviceAction: DeviceAction? = null
)

data class DeviceAction(
    val deviceId: String,
    val deviceName: String,
    val action: String,
    val parameters: Map<String, Any> = emptyMap()
)

data class Device(
    val id: String,
    val name: String,
    val type: DeviceType,
    val room: String,
    val state: DeviceState,
    val integration: IntegrationType,
    val attributes: Map<String, Any> = emptyMap()
)

enum class DeviceType {
    LIGHT, SWITCH, THERMOSTAT, LOCK, SENSOR, CAMERA, SPEAKER, FAN, BLINDS, PLUG, TV, OTHER
}

data class DeviceState(
    val isOn: Boolean = false,
    val brightness: Int? = null,
    val color: String? = null,
    val temperature: Double? = null,
    val targetTemperature: Double? = null,
    val isLocked: Boolean? = null,
    val level: Int? = null
)

enum class IntegrationType {
    HOME_ASSISTANT, GOOGLE_HOME, SMARTTHINGS, MQTT, MATTER
}

data class Room(
    val id: String,
    val name: String,
    val devices: List<Device> = emptyList()
)

data class Scene(
    val id: String,
    val name: String,
    val icon: String,
    val actions: List<DeviceAction>
)
