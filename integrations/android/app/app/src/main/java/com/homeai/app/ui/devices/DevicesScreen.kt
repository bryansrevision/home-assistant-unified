package com.homeai.app.ui.devices

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.homeai.app.models.*
import com.homeai.app.ui.home.getDeviceIcon

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DevicesScreen(
    viewModel: DevicesViewModel = hiltViewModel()
) {
    val devices by viewModel.devices.collectAsState()
    val selectedFilter by viewModel.selectedFilter.collectAsState()
    var showAddDialog by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "All Devices",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            IconButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, "Add device")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Filter chips
        FilterChipsRow(
            selectedFilter = selectedFilter,
            onFilterSelected = { viewModel.setFilter(it) }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Devices list
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(devices) { device ->
                DeviceDetailCard(
                    device = device,
                    onToggle = { viewModel.toggleDevice(device) },
                    onBrightnessChange = { viewModel.setBrightness(device, it) },
                    onTemperatureChange = { viewModel.setTemperature(device, it) }
                )
            }
        }
    }

    if (showAddDialog) {
        AddDeviceDialog(
            onDismiss = { showAddDialog = false },
            onAdd = { name, type, room, integration ->
                viewModel.addDevice(name, type, room, integration)
                showAddDialog = false
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FilterChipsRow(
    selectedFilter: DeviceType?,
    onFilterSelected: (DeviceType?) -> Unit
) {
    val filters = listOf(null to "All") + DeviceType.values().map { it to it.name.lowercase().replaceFirstChar { c -> c.uppercase() } }
    
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        filters.take(5).forEach { (type, label) ->
            FilterChip(
                selected = selectedFilter == type,
                onClick = { onFilterSelected(type) },
                label = { Text(label) }
            )
        }
    }
}

@Composable
fun DeviceDetailCard(
    device: Device,
    onToggle: () -> Unit,
    onBrightnessChange: (Int) -> Unit,
    onTemperatureChange: (Double) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = getDeviceIcon(device.type),
                        contentDescription = device.type.name,
                        modifier = Modifier.size(40.dp),
                        tint = if (device.state.isOn) MaterialTheme.colorScheme.primary
                               else MaterialTheme.colorScheme.outline
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(device.name, fontWeight = FontWeight.Bold)
                        Text(
                            "${device.room} • ${device.integration.name.replace("_", " ")}",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Switch(
                    checked = device.state.isOn,
                    onCheckedChange = { onToggle() }
                )
            }

            // Brightness slider for lights
            if (device.type == DeviceType.LIGHT && device.state.isOn) {
                Spacer(modifier = Modifier.height(16.dp))
                Text("Brightness: ${device.state.brightness ?: 100}%", fontSize = 12.sp)
                Slider(
                    value = (device.state.brightness ?: 100).toFloat(),
                    onValueChange = { onBrightnessChange(it.toInt()) },
                    valueRange = 0f..100f
                )
            }

            // Temperature control for thermostats
            if (device.type == DeviceType.THERMOSTAT) {
                Spacer(modifier = Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Current: ${device.state.temperature ?: 0}°F", fontSize = 14.sp)
                        Text(
                            "Target: ${device.state.targetTemperature ?: 72}°F",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Row {
                        IconButton(onClick = {
                            onTemperatureChange((device.state.targetTemperature ?: 72.0) - 1)
                        }) {
                            Icon(Icons.Default.Remove, "Decrease")
                        }
                        Text(
                            "${(device.state.targetTemperature ?: 72).toInt()}°",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold
                        )
                        IconButton(onClick = {
                            onTemperatureChange((device.state.targetTemperature ?: 72.0) + 1)
                        }) {
                            Icon(Icons.Default.Add, "Increase")
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddDeviceDialog(
    onDismiss: () -> Unit,
    onAdd: (name: String, type: DeviceType, room: String, integration: IntegrationType) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var selectedType by remember { mutableStateOf(DeviceType.LIGHT) }
    var room by remember { mutableStateOf("") }
    var selectedIntegration by remember { mutableStateOf(IntegrationType.HOME_ASSISTANT) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Add Device") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Device Name") },
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = room,
                    onValueChange = { room = it },
                    label = { Text("Room") },
                    modifier = Modifier.fillMaxWidth()
                )
                // Simplified - in real app would use dropdowns
                Text("Type: ${selectedType.name}", fontSize = 12.sp)
                Text("Integration: ${selectedIntegration.name}", fontSize = 12.sp)
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onAdd(name, selectedType, room, selectedIntegration) },
                enabled = name.isNotBlank() && room.isNotBlank()
            ) {
                Text("Add")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
