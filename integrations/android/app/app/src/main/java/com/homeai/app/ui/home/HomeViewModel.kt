package com.homeai.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.homeai.app.integrations.DeviceRepository
import com.homeai.app.integrations.IntegrationManager
import com.homeai.app.models.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val deviceRepository: DeviceRepository,
    private val integrationManager: IntegrationManager
) : ViewModel() {

    private val _rooms = MutableStateFlow<List<Room>>(emptyList())
    val rooms: StateFlow<List<Room>> = _rooms.asStateFlow()

    private val _quickScenes = MutableStateFlow<List<Scene>>(defaultScenes())
    val quickScenes: StateFlow<List<Scene>> = _quickScenes.asStateFlow()

    private val _connectionStatus = MutableStateFlow<Map<IntegrationType, Boolean>>(emptyMap())
    val connectionStatus: StateFlow<Map<IntegrationType, Boolean>> = _connectionStatus.asStateFlow()

    init {
        loadDevices()
        checkConnections()
    }

    private fun loadDevices() {
        viewModelScope.launch {
            val devices = deviceRepository.getAllDevices()
            val groupedRooms = devices.groupBy { it.room }.map { (roomName, roomDevices) ->
                Room(
                    id = roomName.lowercase().replace(" ", "_"),
                    name = roomName,
                    devices = roomDevices
                )
            }
            _rooms.value = groupedRooms
        }
    }

    private fun checkConnections() {
        viewModelScope.launch {
            _connectionStatus.value = integrationManager.checkAllConnections()
        }
    }

    fun toggleDevice(device: Device) {
        viewModelScope.launch {
            val newState = device.state.copy(isOn = !device.state.isOn)
            deviceRepository.updateDeviceState(device.id, newState)
            loadDevices()
        }
    }

    fun activateScene(scene: Scene) {
        viewModelScope.launch {
            scene.actions.forEach { action ->
                deviceRepository.executeDeviceAction(action)
            }
            loadDevices()
        }
    }

    private fun defaultScenes(): List<Scene> = listOf(
        Scene(
            id = "good_night",
            name = "Good Night",
            icon = "night",
            actions = listOf(
                DeviceAction("all_lights", "All Lights", "turn_off")
            )
        ),
        Scene(
            id = "movie_time",
            name = "Movie Time",
            icon = "movie",
            actions = listOf(
                DeviceAction("living_room_light", "Living Room", "set_brightness", mapOf("brightness" to 20))
            )
        ),
        Scene(
            id = "good_morning",
            name = "Good Morning",
            icon = "morning",
            actions = listOf(
                DeviceAction("bedroom_light", "Bedroom", "turn_on"),
                DeviceAction("thermostat", "Thermostat", "set_temperature", mapOf("temperature" to 72))
            )
        ),
        Scene(
            id = "away",
            name = "Away",
            icon = "away",
            actions = listOf(
                DeviceAction("all_lights", "All Lights", "turn_off"),
                DeviceAction("all_locks", "All Locks", "lock")
            )
        )
    )
}
