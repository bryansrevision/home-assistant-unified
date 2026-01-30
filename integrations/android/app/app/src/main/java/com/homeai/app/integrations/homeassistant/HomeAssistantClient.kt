package com.homeai.app.integrations.homeassistant

import com.homeai.app.models.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Home Assistant REST API Client
 * 
 * Setup Guide:
 * 1. Go to Home Assistant → Profile → Long-Lived Access Tokens
 * 2. Create a new token and copy it
 * 3. Enter the token in the app settings
 * 4. Server URL format: http://homeassistant.local:8123 or http://IP:8123
 */
@Singleton
class HomeAssistantClient @Inject constructor() {

    private var baseUrl: String = ""
    private var accessToken: String = ""
    private var connected: Boolean = false

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    suspend fun connect(url: String, token: String) {
        baseUrl = url.trimEnd('/')
        accessToken = token
        
        // Test connection
        withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$baseUrl/api/")
                    .addHeader("Authorization", "Bearer $accessToken")
                    .build()
                
                val response = client.newCall(request).execute()
                connected = response.isSuccessful
            } catch (e: Exception) {
                connected = false
            }
        }
    }

    fun isConnected(): Boolean = connected

    suspend fun getDevices(): List<Device> = withContext(Dispatchers.IO) {
        if (!connected) return@withContext emptyList()
        
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/states")
                .addHeader("Authorization", "Bearer $accessToken")
                .build()
            
            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return@withContext emptyList()
            
            val states = JSONArray(body)
            val devices = mutableListOf<Device>()
            
            for (i in 0 until states.length()) {
                val entity = states.getJSONObject(i)
                val entityId = entity.getString("entity_id")
                val state = entity.getString("state")
                val attributes = entity.optJSONObject("attributes") ?: JSONObject()
                
                val device = parseEntity(entityId, state, attributes)
                if (device != null) {
                    devices.add(device)
                }
            }
            
            devices
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun parseEntity(entityId: String, state: String, attributes: JSONObject): Device? {
        val domain = entityId.split(".").firstOrNull() ?: return null
        val name = attributes.optString("friendly_name", entityId)
        val room = attributes.optString("room", "Unknown")
        
        val (type, deviceState) = when (domain) {
            "light" -> {
                DeviceType.LIGHT to DeviceState(
                    isOn = state == "on",
                    brightness = attributes.optInt("brightness", 255) * 100 / 255,
                    color = attributes.optString("rgb_color", null)
                )
            }
            "switch" -> DeviceType.SWITCH to DeviceState(isOn = state == "on")
            "climate" -> {
                DeviceType.THERMOSTAT to DeviceState(
                    isOn = state != "off",
                    temperature = attributes.optDouble("current_temperature", 0.0),
                    targetTemperature = attributes.optDouble("temperature", 72.0)
                )
            }
            "lock" -> DeviceType.LOCK to DeviceState(isLocked = state == "locked")
            "fan" -> DeviceType.FAN to DeviceState(isOn = state == "on")
            "cover" -> DeviceType.BLINDS to DeviceState(
                isOn = state == "open",
                level = attributes.optInt("current_position", 0)
            )
            "sensor", "binary_sensor" -> DeviceType.SENSOR to DeviceState(isOn = true)
            "camera" -> DeviceType.CAMERA to DeviceState(isOn = state == "recording")
            "media_player" -> DeviceType.TV to DeviceState(isOn = state == "on" || state == "playing")
            else -> return null
        }
        
        return Device(
            id = entityId,
            name = name,
            type = type,
            room = room,
            state = deviceState,
            integration = IntegrationType.HOME_ASSISTANT,
            attributes = mapOf("entity_id" to entityId)
        )
    }

    suspend fun setState(entityId: String, state: DeviceState) = withContext(Dispatchers.IO) {
        if (!connected) return@withContext
        
        val domain = entityId.split(".").firstOrNull() ?: return@withContext
        val service = if (state.isOn) "turn_on" else "turn_off"
        
        val requestBody = JSONObject().apply {
            put("entity_id", entityId)
            state.brightness?.let { put("brightness", it * 255 / 100) }
            state.targetTemperature?.let { put("temperature", it) }
        }
        
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/services/$domain/$service")
                .addHeader("Authorization", "Bearer $accessToken")
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                .build()
            
            client.newCall(request).execute()
        } catch (e: Exception) {
            // Log error
        }
    }

    suspend fun callService(domain: String, service: String, data: Map<String, Any>) = 
        withContext(Dispatchers.IO) {
            if (!connected) return@withContext
            
            val requestBody = JSONObject(data)
            
            val request = Request.Builder()
                .url("$baseUrl/api/services/$domain/$service")
                .addHeader("Authorization", "Bearer $accessToken")
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                .build()
            
            try {
                client.newCall(request).execute()
            } catch (e: Exception) {
                // Log error
            }
        }
}
