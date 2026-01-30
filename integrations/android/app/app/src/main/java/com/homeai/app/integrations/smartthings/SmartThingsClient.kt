package com.homeai.app.integrations.smartthings

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
 * SmartThings API Client
 * 
 * Setup Guide:
 * 1. Go to https://account.smartthings.com/tokens
 * 2. Create a new Personal Access Token
 * 3. Select scopes: Devices (all), Locations (all)
 * 4. Copy the token and enter it in app settings
 */
@Singleton
class SmartThingsClient @Inject constructor() {

    private var accessToken: String = ""
    private var connected: Boolean = false

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    companion object {
        private const val BASE_URL = "https://api.smartthings.com/v1"
    }

    suspend fun connect(token: String) {
        accessToken = token
        
        withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$BASE_URL/locations")
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
                .url("$BASE_URL/devices")
                .addHeader("Authorization", "Bearer $accessToken")
                .build()
            
            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return@withContext emptyList()
            
            val json = JSONObject(body)
            val items = json.getJSONArray("items")
            val devices = mutableListOf<Device>()
            
            for (i in 0 until items.length()) {
                val item = items.getJSONObject(i)
                val device = parseDevice(item)
                if (device != null) {
                    devices.add(device)
                }
            }
            
            devices
        } catch (e: Exception) {
            emptyList()
        }
    }

    private suspend fun parseDevice(json: JSONObject): Device? {
        val deviceId = json.getString("deviceId")
        val label = json.optString("label", json.optString("name", "Unknown"))
        val roomId = json.optString("roomId", "")
        val components = json.optJSONArray("components") ?: return null
        
        var type = DeviceType.OTHER
        var state = DeviceState()
        
        // Parse capabilities
        for (i in 0 until components.length()) {
            val component = components.getJSONObject(i)
            val capabilities = component.optJSONArray("capabilities") ?: continue
            
            for (j in 0 until capabilities.length()) {
                val capability = capabilities.getJSONObject(j)
                val capId = capability.getString("id")
                
                when (capId) {
                    "switch" -> {
                        type = DeviceType.SWITCH
                        val status = getDeviceStatus(deviceId, "switch")
                        state = state.copy(isOn = status == "on")
                    }
                    "switchLevel" -> {
                        type = DeviceType.LIGHT
                        val level = getDeviceLevelStatus(deviceId)
                        state = state.copy(brightness = level)
                    }
                    "colorControl" -> {
                        type = DeviceType.LIGHT
                    }
                    "thermostat", "thermostatCoolingSetpoint", "thermostatHeatingSetpoint" -> {
                        type = DeviceType.THERMOSTAT
                        val temp = getDeviceTempStatus(deviceId)
                        state = state.copy(temperature = temp.first, targetTemperature = temp.second)
                    }
                    "lock" -> {
                        type = DeviceType.LOCK
                        val lockStatus = getDeviceStatus(deviceId, "lock")
                        state = state.copy(isLocked = lockStatus == "locked")
                    }
                    "motionSensor", "contactSensor", "temperatureMeasurement" -> {
                        type = DeviceType.SENSOR
                    }
                    "mediaPlayback" -> {
                        type = DeviceType.TV
                    }
                }
            }
        }
        
        val room = if (roomId.isNotEmpty()) getRoomName(roomId) else "Unknown"
        
        return Device(
            id = deviceId,
            name = label,
            type = type,
            room = room,
            state = state,
            integration = IntegrationType.SMARTTHINGS,
            attributes = mapOf("device_id" to deviceId)
        )
    }

    private suspend fun getDeviceStatus(deviceId: String, capability: String): String = 
        withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$BASE_URL/devices/$deviceId/components/main/capabilities/$capability/status")
                    .addHeader("Authorization", "Bearer $accessToken")
                    .build()
                
                val response = client.newCall(request).execute()
                val body = response.body?.string() ?: return@withContext ""
                val json = JSONObject(body)
                
                json.optJSONObject(capability)?.optJSONObject("value")?.optString("value", "") ?: ""
            } catch (e: Exception) {
                ""
            }
        }

    private suspend fun getDeviceLevelStatus(deviceId: String): Int = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$BASE_URL/devices/$deviceId/components/main/capabilities/switchLevel/status")
                .addHeader("Authorization", "Bearer $accessToken")
                .build()
            
            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return@withContext 100
            val json = JSONObject(body)
            
            json.optJSONObject("level")?.optInt("value", 100) ?: 100
        } catch (e: Exception) {
            100
        }
    }

    private suspend fun getDeviceTempStatus(deviceId: String): Pair<Double, Double> = 
        withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$BASE_URL/devices/$deviceId/status")
                    .addHeader("Authorization", "Bearer $accessToken")
                    .build()
                
                val response = client.newCall(request).execute()
                val body = response.body?.string() ?: return@withContext Pair(72.0, 72.0)
                val json = JSONObject(body)
                
                val main = json.optJSONObject("components")?.optJSONObject("main")
                val current = main?.optJSONObject("temperatureMeasurement")
                    ?.optJSONObject("temperature")?.optDouble("value", 72.0) ?: 72.0
                val target = main?.optJSONObject("thermostatCoolingSetpoint")
                    ?.optJSONObject("coolingSetpoint")?.optDouble("value", 72.0) ?: 72.0
                
                Pair(current, target)
            } catch (e: Exception) {
                Pair(72.0, 72.0)
            }
        }

    private suspend fun getRoomName(roomId: String): String = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$BASE_URL/rooms/$roomId")
                .addHeader("Authorization", "Bearer $accessToken")
                .build()
            
            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return@withContext "Unknown"
            val json = JSONObject(body)
            
            json.optString("name", "Unknown")
        } catch (e: Exception) {
            "Unknown"
        }
    }

    suspend fun setDeviceState(deviceId: String, state: DeviceState) = withContext(Dispatchers.IO) {
        if (!connected) return@withContext
        
        val commands = JSONArray()
        
        // On/Off command
        commands.put(JSONObject().apply {
            put("component", "main")
            put("capability", "switch")
            put("command", if (state.isOn) "on" else "off")
        })
        
        // Brightness command
        state.brightness?.let { brightness ->
            commands.put(JSONObject().apply {
                put("component", "main")
                put("capability", "switchLevel")
                put("command", "setLevel")
                put("arguments", JSONArray().apply { put(brightness) })
            })
        }
        
        // Temperature command
        state.targetTemperature?.let { temp ->
            commands.put(JSONObject().apply {
                put("component", "main")
                put("capability", "thermostatCoolingSetpoint")
                put("command", "setCoolingSetpoint")
                put("arguments", JSONArray().apply { put(temp) })
            })
        }
        
        // Lock command
        state.isLocked?.let { locked ->
            commands.put(JSONObject().apply {
                put("component", "main")
                put("capability", "lock")
                put("command", if (locked) "lock" else "unlock")
            })
        }
        
        val requestBody = JSONObject().apply {
            put("commands", commands)
        }
        
        try {
            val request = Request.Builder()
                .url("$BASE_URL/devices/$deviceId/commands")
                .addHeader("Authorization", "Bearer $accessToken")
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                .build()
            
            client.newCall(request).execute()
        } catch (e: Exception) {
            // Log error
        }
    }
}
