package com.homeai.app.integrations

import com.homeai.app.models.*
import kotlinx.coroutines.flow.Flow

interface DeviceRepository {
    suspend fun getAllDevices(): List<Device>
    suspend fun getDevice(id: String): Device?
    suspend fun updateDeviceState(deviceId: String, state: DeviceState)
    suspend fun addDevice(device: Device)
    suspend fun removeDevice(deviceId: String)
    suspend fun executeDeviceAction(action: DeviceAction): String
    fun observeDevices(): Flow<List<Device>>
}

interface IntegrationManager {
    suspend fun checkAllConnections(): Map<IntegrationType, Boolean>
    suspend fun testHomeAssistant(url: String, token: String): Boolean
    suspend fun testMqtt(url: String, username: String, password: String): Boolean
    suspend fun testSmartThings(token: String): Boolean
    suspend fun initiateGoogleHomeAuth()
}
