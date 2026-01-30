package com.homeai.app.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.homeai.app.models.IntegrationType

@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val settings by viewModel.settings.collectAsState()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                "Settings",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // AI Settings
        item {
            SettingsSection(title = "AI Assistant") {
                SettingsTextField(
                    label = "OpenAI API Key",
                    value = settings.openAiApiKey,
                    onValueChange = { viewModel.updateOpenAiKey(it) },
                    isPassword = true
                )
            }
        }

        // Home Assistant
        item {
            SettingsSection(title = "Home Assistant") {
                SettingsTextField(
                    label = "Server URL",
                    value = settings.homeAssistantUrl,
                    onValueChange = { viewModel.updateHomeAssistantUrl(it) },
                    placeholder = "http://homeassistant.local:8123"
                )
                Spacer(modifier = Modifier.height(8.dp))
                SettingsTextField(
                    label = "Long-Lived Access Token",
                    value = settings.homeAssistantToken,
                    onValueChange = { viewModel.updateHomeAssistantToken(it) },
                    isPassword = true
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Connection Status")
                    if (settings.homeAssistantConnected) {
                        Icon(Icons.Default.CheckCircle, "Connected", tint = MaterialTheme.colorScheme.primary)
                    } else {
                        Icon(Icons.Default.Error, "Disconnected", tint = MaterialTheme.colorScheme.error)
                    }
                }
                Button(
                    onClick = { viewModel.testHomeAssistant() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Test Connection")
                }
            }
        }

        // MQTT
        item {
            SettingsSection(title = "MQTT Broker") {
                SettingsTextField(
                    label = "Broker URL",
                    value = settings.mqttBrokerUrl,
                    onValueChange = { viewModel.updateMqttUrl(it) },
                    placeholder = "tcp://192.168.1.100:1883"
                )
                Spacer(modifier = Modifier.height(8.dp))
                SettingsTextField(
                    label = "Username",
                    value = settings.mqttUsername,
                    onValueChange = { viewModel.updateMqttUsername(it) }
                )
                Spacer(modifier = Modifier.height(8.dp))
                SettingsTextField(
                    label = "Password",
                    value = settings.mqttPassword,
                    onValueChange = { viewModel.updateMqttPassword(it) },
                    isPassword = true
                )
                Button(
                    onClick = { viewModel.testMqtt() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Test Connection")
                }
            }
        }

        // SmartThings
        item {
            SettingsSection(title = "SmartThings") {
                SettingsTextField(
                    label = "Personal Access Token",
                    value = settings.smartThingsToken,
                    onValueChange = { viewModel.updateSmartThingsToken(it) },
                    isPassword = true
                )
                Button(
                    onClick = { viewModel.testSmartThings() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Connect SmartThings")
                }
            }
        }

        // Google Home
        item {
            SettingsSection(title = "Google Home") {
                Button(
                    onClick = { viewModel.connectGoogleHome() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Login, "Google", modifier = Modifier.size(20.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Sign in with Google")
                }
            }
        }

        // About
        item {
            SettingsSection(title = "About") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Version")
                    Text("1.0.0")
                }
            }
        }
    }
}

@Composable
fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                title,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(12.dp))
            content()
        }
    }
}

@Composable
fun SettingsTextField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String = "",
    isPassword: Boolean = false
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = { Text(placeholder) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        visualTransformation = if (isPassword) PasswordVisualTransformation() else androidx.compose.ui.text.input.VisualTransformation.None
    )
}
