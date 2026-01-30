package com.homeai.app.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.homeai.app.integrations.IntegrationManager
import com.homeai.app.utils.SettingsDataStore
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsDataStore: SettingsDataStore,
    private val integrationManager: IntegrationManager
) : ViewModel() {

    private val _settings = MutableStateFlow(AppSettings())
    val settings: StateFlow<AppSettings> = _settings.asStateFlow()

    init {
        loadSettings()
    }

    private fun loadSettings() {
        viewModelScope.launch {
            settingsDataStore.settingsFlow.collect { savedSettings ->
                _settings.value = savedSettings
            }
        }
    }

    fun updateOpenAiKey(key: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(openAiApiKey = key)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateHomeAssistantUrl(url: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(homeAssistantUrl = url)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateHomeAssistantToken(token: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(homeAssistantToken = token)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateMqttUrl(url: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(mqttBrokerUrl = url)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateMqttUsername(username: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(mqttUsername = username)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateMqttPassword(password: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(mqttPassword = password)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun updateSmartThingsToken(token: String) {
        viewModelScope.launch {
            val updated = _settings.value.copy(smartThingsToken = token)
            _settings.value = updated
            settingsDataStore.saveSettings(updated)
        }
    }

    fun testHomeAssistant() {
        viewModelScope.launch {
            val connected = integrationManager.testHomeAssistant(
                _settings.value.homeAssistantUrl,
                _settings.value.homeAssistantToken
            )
            _settings.value = _settings.value.copy(homeAssistantConnected = connected)
        }
    }

    fun testMqtt() {
        viewModelScope.launch {
            integrationManager.testMqtt(
                _settings.value.mqttBrokerUrl,
                _settings.value.mqttUsername,
                _settings.value.mqttPassword
            )
        }
    }

    fun testSmartThings() {
        viewModelScope.launch {
            integrationManager.testSmartThings(_settings.value.smartThingsToken)
        }
    }

    fun connectGoogleHome() {
        viewModelScope.launch {
            integrationManager.initiateGoogleHomeAuth()
        }
    }
}

data class AppSettings(
    val openAiApiKey: String = "",
    val homeAssistantUrl: String = "",
    val homeAssistantToken: String = "",
    val homeAssistantConnected: Boolean = false,
    val mqttBrokerUrl: String = "",
    val mqttUsername: String = "",
    val mqttPassword: String = "",
    val smartThingsToken: String = "",
    val googleHomeConnected: Boolean = false
)
