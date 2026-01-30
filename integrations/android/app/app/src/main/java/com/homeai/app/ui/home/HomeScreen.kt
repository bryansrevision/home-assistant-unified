package com.homeai.app.ui.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.homeai.app.models.*

@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val rooms by viewModel.rooms.collectAsState()
    val quickScenes by viewModel.quickScenes.collectAsState()
    val connectionStatus by viewModel.connectionStatus.collectAsState()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Connection Status
        item {
            ConnectionStatusCard(connectionStatus)
        }

        // Quick Scenes
        item {
            Text(
                "Quick Scenes",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(quickScenes) { scene ->
                    SceneCard(
                        scene = scene,
                        onClick = { viewModel.activateScene(scene) }
                    )
                }
            }
        }

        // Rooms
        item {
            Text(
                "Rooms",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        items(rooms) { room ->
            RoomCard(
                room = room,
                onDeviceToggle = { device -> viewModel.toggleDevice(device) }
            )
        }
    }
}

@Composable
fun ConnectionStatusCard(status: Map<IntegrationType, Boolean>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Integrations", fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                status.forEach { (type, connected) ->
                    IntegrationStatus(type, connected)
                }
            }
        }
    }
}

@Composable
fun IntegrationStatus(type: IntegrationType, connected: Boolean) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            imageVector = when (type) {
                IntegrationType.HOME_ASSISTANT -> Icons.Default.Home
                IntegrationType.GOOGLE_HOME -> Icons.Default.Devices
                IntegrationType.SMARTTHINGS -> Icons.Default.Hub
                IntegrationType.MQTT -> Icons.Default.Lan
                IntegrationType.MATTER -> Icons.Default.WifiTethering
            },
            contentDescription = type.name,
            tint = if (connected) MaterialTheme.colorScheme.primary 
                   else MaterialTheme.colorScheme.outline
        )
        Text(
            type.name.replace("_", " "),
            fontSize = 10.sp,
            color = if (connected) MaterialTheme.colorScheme.onPrimaryContainer
                    else MaterialTheme.colorScheme.outline
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SceneCard(scene: Scene, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = Modifier.size(100.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = getSceneIcon(scene.icon),
                contentDescription = scene.name,
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(scene.name, fontSize = 12.sp)
        }
    }
}

@Composable
fun RoomCard(room: Room, onDeviceToggle: (Device) -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    room.name,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    "${room.devices.count { it.state.isOn }}/${room.devices.size} on",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            room.devices.take(4).forEach { device ->
                DeviceRow(device = device, onToggle = { onDeviceToggle(device) })
                if (device != room.devices.take(4).last()) {
                    Divider(modifier = Modifier.padding(vertical = 8.dp))
                }
            }
            
            if (room.devices.size > 4) {
                TextButton(onClick = { /* Show all devices */ }) {
                    Text("View all ${room.devices.size} devices")
                }
            }
        }
    }
}

@Composable
fun DeviceRow(device: Device, onToggle: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = getDeviceIcon(device.type),
                contentDescription = device.type.name,
                tint = if (device.state.isOn) MaterialTheme.colorScheme.primary 
                       else MaterialTheme.colorScheme.outline
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(device.name)
                device.state.brightness?.let {
                    Text(
                        "$it% brightness",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                device.state.temperature?.let {
                    Text(
                        "${it}°",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
        
        Switch(
            checked = device.state.isOn,
            onCheckedChange = { onToggle() }
        )
    }
}

fun getDeviceIcon(type: DeviceType): ImageVector = when (type) {
    DeviceType.LIGHT -> Icons.Default.Lightbulb
    DeviceType.SWITCH -> Icons.Default.ToggleOn
    DeviceType.THERMOSTAT -> Icons.Default.Thermostat
    DeviceType.LOCK -> Icons.Default.Lock
    DeviceType.SENSOR -> Icons.Default.Sensors
    DeviceType.CAMERA -> Icons.Default.Videocam
    DeviceType.SPEAKER -> Icons.Default.Speaker
    DeviceType.FAN -> Icons.Default.Air
    DeviceType.BLINDS -> Icons.Default.Blinds
    DeviceType.PLUG -> Icons.Default.Power
    DeviceType.TV -> Icons.Default.Tv
    DeviceType.OTHER -> Icons.Default.DevicesOther
}

fun getSceneIcon(icon: String): ImageVector = when (icon) {
    "night" -> Icons.Default.Bedtime
    "movie" -> Icons.Default.Movie
    "morning" -> Icons.Default.WbSunny
    "away" -> Icons.Default.ExitToApp
    "party" -> Icons.Default.Celebration
    else -> Icons.Default.PlayArrow
}
