package com.homeai.app.integrations

import com.homeai.app.ai.DeviceController
import com.homeai.app.integrations.homeassistant.HomeAssistantClient
import com.homeai.app.integrations.mqtt.MqttClient
import com.homeai.app.integrations.smartthings.SmartThingsClient
import com.homeai.app.models.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DeviceRepositoryImpl @Inject constructor(
    private val homeAssistantClient: HomeAssistantClient,
    private val mqttClient: MqttClient,
    private val smartThingsClient: SmartThingsClient
) : DeviceRepository, DeviceController {

    private val devicesFlow = MutableStateFlow<List<Device>>(sampleDevices())

    override suspend fun getAllDevices(): List<Device> {
        val allDevices = mutableListOf<Device>()
        
        // Fetch from all integrations
        try {
            allDevices.addAll(homeAssistantClient.getDevices())
        } catch (_: Exception) {}
        
        try {
            allDevices.addAll(smartThingsClient.getDevices())
        } catch (_: Exception) {}
        
        // If no devices from integrations, return sample devices
        return if (allDevices.isEmpty()) sampleDevices() else allDevices
    }

    override suspend fun getDevice(id: String): Device? {
        return getAllDevices().find { it.id == id }
    }

    override suspend fun updateDeviceState(deviceId: String, state: DeviceState) {
        val device = getDevice(deviceId) ?: return
        
        when (device.integration) {
            IntegrationType.HOME_ASSISTANT -> {
                homeAssistantClient.setState(deviceId, state)
            }
            IntegrationType.MQTT -> {
                mqttClient.publishState(deviceId, state)
            }
            IntegrationType.SMARTTHINGS -> {
                smartThingsClient.setDeviceState(deviceId, state)
            }
            else -> {
                // Local update for demo
                val updated = devicesFlow.value.map {
                    if (it.id == deviceId) it.copy(state = state) else it
                }
                devicesFlow.value = updated
            }
        }
    }

    override suspend fun addDevice(device: Device) {
        devicesFlow.value = devicesFlow.value + device
    }

    override suspend fun removeDevice(deviceId: String) {
        devicesFlow.value = devicesFlow.value.filter { it.id != deviceId }
    }

    override suspend fun executeDeviceAction(action: DeviceAction): String {
        return executeAction(action)
    }

    override suspend fun executeAction(action: DeviceAction): String {
        val device = getDevice(action.deviceId)
        
        return try {
            when (action.action) {
                "turn_on" -> {
                    updateDeviceState(action.deviceId, device?.state?.copy(isOn = true) ?: DeviceState(isOn = true))
                    "Turned on ${action.deviceName}"
                }
                "turn_off" -> {
                    updateDeviceState(action.deviceId, device?.state?.copy(isOn = false) ?: DeviceState(isOn = false))
                    "Turned off ${action.deviceName}"
                }
                "set_brightness" -> {
                    val brightness = action.parameters["brightness"] as? Int ?: 50
                    updateDeviceState(action.deviceId, device?.state?.copy(brightness = brightness) ?: DeviceState(brightness = brightness))
                    "Set ${action.deviceName} brightness to $brightness%"
                }
                "set_temperature" -> {
                    val temp = (action.parameters["temperature"] as? Number)?.toDouble() ?: 72.0
                    updateDeviceState(action.deviceId, device?.state?.copy(targetTemperature = temp) ?: DeviceState(targetTemperature = temp))
                    "Set ${action.deviceName} to $temp°F"
                }
                "lock" -> {
                    updateDeviceState(action.deviceId, device?.state?.copy(isLocked = true) ?: DeviceState(isLocked = true))
                    "Locked ${action.deviceName}"
                }
                "unlock" -> {
                    updateDeviceState(action.deviceId, device?.state?.copy(isLocked = false) ?: DeviceState(isLocked = false))
                    "Unlocked ${action.deviceName}"
                }
                else -> "Unknown action: ${action.action}"
            }
        } catch (e: Exception) {
            "Error: ${e.message}"
        }
    }

    override fun observeDevices(): Flow<List<Device>> = devicesFlow

    private fun sampleDevices(): List<Device> = listOf(
        Device("living_room_light", "Main Light", DeviceType.LIGHT, "Living Room", 
            DeviceState(isOn = true, brightness = 80), IntegrationType.HOME_ASSISTANT),
        Device("living_room_lamp", "Floor Lamp", DeviceType.LIGHT, "Living Room", 
            DeviceState(isOn = false, brightness = 50), IntegrationType.HOME_ASSISTANT),
        Device("living_room_tv", "Smart TV", DeviceType.TV, "Living Room", 
            DeviceState(isOn = false), IntegrationType.SMARTTHINGS),
        Device("bedroom_light", "Ceiling Light", DeviceType.LIGHT, "Bedroom", 
            DeviceState(isOn = false, brightness = 100), IntegrationType.HOME_ASSISTANT),
        Device("bedroom_lamp", "Bedside Lamp", DeviceType.LIGHT, "Bedroom", 
            DeviceState(isOn = true, brightness = 30), IntegrationType.MQTT),
        Device("thermostat", "Main Thermostat", DeviceType.THERMOSTAT, "Living Room", 
            DeviceState(isOn = true, temperature = 71.0, targetTemperature = 72.0), IntegrationType.HOME_ASSISTANT),
        Device("front_door_lock", "Front Door", DeviceType.LOCK, "Entryway", 
            DeviceState(isOn = true, isLocked = true), IntegrationType.SMARTTHINGS),
        Device("garage_door", "Garage Door", DeviceType.SWITCH, "Garage", 
            DeviceState(isOn = false), IntegrationType.MQTT),
        Device("kitchen_light", "Kitchen Light", DeviceType.LIGHT, "Kitchen", 
            DeviceState(isOn = false, brightness = 100), IntegrationType.HOME_ASSISTANT),
        Device("motion_sensor", "Hallway Sensor", DeviceType.SENSOR, "Hallway", 
            DeviceState(isOn = true), IntegrationType.HOME_ASSISTANT)
    )
}
