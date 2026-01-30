package com.homeai.app.integrations.mqtt

import android.content.Context
import android.util.Log
import com.homeai.app.models.*
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.withContext
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * MQTT Client for IoT Device Control
 * 
 * Supports:
 * - Tasmota devices (default topic: tasmota/+/+)
 * - Zigbee2MQTT (default topic: zigbee2mqtt/+)
 * - ESPHome (default topic: esphome/+/+)
 * - Custom MQTT topics
 * 
 * Setup Guide:
 * 1. Set up MQTT broker (Mosquitto, EMQX, etc.)
 * 2. Configure your IoT devices to use the broker
 * 3. Enter broker URL in app settings (e.g., tcp://192.168.1.100:1883)
 */
@Singleton
class MqttClient @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private var client: MqttAsyncClient? = null
    private var connected = false
    
    private val _messages = MutableSharedFlow<MqttMessage>()
    val messages: SharedFlow<MqttMessage> = _messages
    
    private val discoveredDevices = mutableMapOf<String, Device>()

    companion object {
        private const val TAG = "MqttClient"
        
        // Common MQTT topic patterns
        const val TASMOTA_DISCOVERY = "tasmota/discovery/#"
        const val TASMOTA_STATE = "tele/+/STATE"
        const val ZIGBEE2MQTT = "zigbee2mqtt/#"
        const val ESPHOME = "esphome/+/state"
        const val HOMEAI_TOPIC = "homeai/#"
    }

    suspend fun connect(brokerUrl: String, username: String, password: String) = 
        withContext(Dispatchers.IO) {
            try {
                val clientId = "HomeAI_${UUID.randomUUID().toString().take(8)}"
                client = MqttAsyncClient(brokerUrl, clientId, MemoryPersistence())
                
                val options = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 10
                    keepAliveInterval = 60
                    if (username.isNotBlank()) {
                        this.userName = username
                        this.password = password.toCharArray()
                    }
                    isAutomaticReconnect = true
                }
                
                client?.setCallback(object : MqttCallback {
                    override fun connectionLost(cause: Throwable?) {
                        connected = false
                        Log.w(TAG, "Connection lost: ${cause?.message}")
                    }
                    
                    override fun messageArrived(topic: String?, message: org.eclipse.paho.client.mqttv3.MqttMessage?) {
                        topic ?: return
                        message ?: return
                        handleMessage(topic, message.payload)
                    }
                    
                    override fun deliveryComplete(token: IMqttDeliveryToken?) {}
                })
                
                client?.connect(options)?.waitForCompletion()
                connected = true
                
                // Subscribe to common topics
                subscribeToTopics()
                
            } catch (e: Exception) {
                Log.e(TAG, "Connection failed: ${e.message}")
                connected = false
            }
        }

    private suspend fun subscribeToTopics() {
        try {
            client?.subscribe(arrayOf(HOMEAI_TOPIC, TASMOTA_STATE, ZIGBEE2MQTT), intArrayOf(0, 0, 0))
        } catch (e: Exception) {
            Log.e(TAG, "Subscribe failed: ${e.message}")
        }
    }

    private fun handleMessage(topic: String, payload: ByteArray) {
        try {
            val payloadStr = String(payload)
            
            when {
                topic.startsWith("tele/") && topic.endsWith("/STATE") -> {
                    // Tasmota state update
                    val deviceId = topic.split("/")[1]
                    val json = JSONObject(payloadStr)
                    updateTasmotaDevice(deviceId, json)
                }
                topic.startsWith("zigbee2mqtt/") -> {
                    // Zigbee2MQTT update
                    val deviceId = topic.removePrefix("zigbee2mqtt/")
                    if (!deviceId.contains("/")) {
                        val json = JSONObject(payloadStr)
                        updateZigbeeDevice(deviceId, json)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling message: ${e.message}")
        }
    }

    private fun updateTasmotaDevice(deviceId: String, json: JSONObject) {
        val power = json.optString("POWER", json.optString("POWER1", ""))
        val isOn = power.equals("ON", ignoreCase = true)
        
        val device = Device(
            id = "tasmota_$deviceId",
            name = deviceId.replace("_", " ").replaceFirstChar { it.uppercase() },
            type = DeviceType.SWITCH,
            room = "Unknown",
            state = DeviceState(isOn = isOn),
            integration = IntegrationType.MQTT,
            attributes = mapOf("mqtt_topic" to "cmnd/$deviceId/POWER")
        )
        discoveredDevices[device.id] = device
    }

    private fun updateZigbeeDevice(deviceId: String, json: JSONObject) {
        val state = json.optString("state", "")
        val brightness = json.optInt("brightness", -1)
        val temperature = json.optDouble("temperature", Double.NaN)
        
        val type = when {
            brightness >= 0 -> DeviceType.LIGHT
            !temperature.isNaN() -> DeviceType.SENSOR
            state.isNotEmpty() -> DeviceType.SWITCH
            else -> DeviceType.OTHER
        }
        
        val device = Device(
            id = "zigbee_$deviceId",
            name = deviceId.replace("_", " ").replaceFirstChar { it.uppercase() },
            type = type,
            room = "Unknown",
            state = DeviceState(
                isOn = state.equals("ON", ignoreCase = true),
                brightness = if (brightness >= 0) brightness * 100 / 254 else null,
                temperature = if (!temperature.isNaN()) temperature else null
            ),
            integration = IntegrationType.MQTT,
            attributes = mapOf("mqtt_topic" to "zigbee2mqtt/$deviceId/set")
        )
        discoveredDevices[device.id] = device
    }

    fun isConnected(): Boolean = connected

    fun getDiscoveredDevices(): List<Device> = discoveredDevices.values.toList()

    suspend fun publishState(deviceId: String, state: DeviceState) = withContext(Dispatchers.IO) {
        val device = discoveredDevices[deviceId] ?: return@withContext
        val topic = device.attributes["mqtt_topic"] as? String ?: return@withContext
        
        val payload = when {
            device.id.startsWith("tasmota_") -> {
                if (state.isOn) "ON" else "OFF"
            }
            device.id.startsWith("zigbee_") -> {
                JSONObject().apply {
                    put("state", if (state.isOn) "ON" else "OFF")
                    state.brightness?.let { put("brightness", it * 254 / 100) }
                }.toString()
            }
            else -> if (state.isOn) "ON" else "OFF"
        }
        
        try {
            val message = org.eclipse.paho.client.mqttv3.MqttMessage(payload.toByteArray())
            message.qos = 0
            client?.publish(topic, message)
        } catch (e: Exception) {
            Log.e(TAG, "Publish failed: ${e.message}")
        }
    }

    suspend fun publish(topic: String, payload: String, qos: Int = 0) = withContext(Dispatchers.IO) {
        try {
            val message = org.eclipse.paho.client.mqttv3.MqttMessage(payload.toByteArray())
            message.qos = qos
            client?.publish(topic, message)
        } catch (e: Exception) {
            Log.e(TAG, "Publish failed: ${e.message}")
        }
    }

    suspend fun subscribe(topic: String, qos: Int = 0) = withContext(Dispatchers.IO) {
        try {
            client?.subscribe(topic, qos)
        } catch (e: Exception) {
            Log.e(TAG, "Subscribe failed: ${e.message}")
        }
    }

    fun disconnect() {
        try {
            client?.disconnect()
            connected = false
        } catch (e: Exception) {
            Log.e(TAG, "Disconnect failed: ${e.message}")
        }
    }
}

data class MqttMessage(
    val topic: String,
    val payload: String,
    val timestamp: Long = System.currentTimeMillis()
)
