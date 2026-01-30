package com.homeai.app.ui.devices

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.homeai.app.integrations.DeviceRepository
import com.homeai.app.models.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class DevicesViewModel @Inject constructor(
    private val deviceRepository: DeviceRepository
) : ViewModel() {

    private val _allDevices = MutableStateFlow<List<Device>>(emptyList())
    
    private val _selectedFilter = MutableStateFlow<DeviceType?>(null)
    val selectedFilter: StateFlow<DeviceType?> = _selectedFilter.asStateFlow()

    private val _devices = MutableStateFlow<List<Device>>(emptyList())
    val devices: StateFlow<List<Device>> = _devices.asStateFlow()

    init {
        loadDevices()
        
        viewModelScope.launch {
            combine(_allDevices, _selectedFilter) { allDevices, filter ->
                if (filter == null) allDevices else allDevices.filter { it.type == filter }
            }.collect { filtered ->
                _devices.value = filtered
            }
        }
    }

    private fun loadDevices() {
        viewModelScope.launch {
            _allDevices.value = deviceRepository.getAllDevices()
        }
    }

    fun setFilter(type: DeviceType?) {
        _selectedFilter.value = type
    }

    fun toggleDevice(device: Device) {
        viewModelScope.launch {
            val newState = device.state.copy(isOn = !device.state.isOn)
            deviceRepository.updateDeviceState(device.id, newState)
            loadDevices()
        }
    }

    fun setBrightness(device: Device, brightness: Int) {
        viewModelScope.launch {
            val newState = device.state.copy(brightness = brightness)
            deviceRepository.updateDeviceState(device.id, newState)
            loadDevices()
        }
    }

    fun setTemperature(device: Device, temperature: Double) {
        viewModelScope.launch {
            val newState = device.state.copy(targetTemperature = temperature)
            deviceRepository.updateDeviceState(device.id, newState)
            loadDevices()
        }
    }

    fun addDevice(name: String, type: DeviceType, room: String, integration: IntegrationType) {
        viewModelScope.launch {
            val device = Device(
                id = UUID.randomUUID().toString(),
                name = name,
                type = type,
                room = room,
                state = DeviceState(isOn = false),
                integration = integration
            )
            deviceRepository.addDevice(device)
            loadDevices()
        }
    }
}
