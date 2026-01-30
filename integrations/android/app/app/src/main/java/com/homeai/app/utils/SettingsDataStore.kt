package com.homeai.app.utils

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.homeai.app.ui.settings.AppSettings
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

@Singleton
class SettingsDataStore @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private object Keys {
        val OPENAI_API_KEY = stringPreferencesKey("openai_api_key")
        val HOME_ASSISTANT_URL = stringPreferencesKey("home_assistant_url")
        val HOME_ASSISTANT_TOKEN = stringPreferencesKey("home_assistant_token")
        val HOME_ASSISTANT_CONNECTED = booleanPreferencesKey("home_assistant_connected")
        val MQTT_BROKER_URL = stringPreferencesKey("mqtt_broker_url")
        val MQTT_USERNAME = stringPreferencesKey("mqtt_username")
        val MQTT_PASSWORD = stringPreferencesKey("mqtt_password")
        val SMARTTHINGS_TOKEN = stringPreferencesKey("smartthings_token")
        val GOOGLE_HOME_CONNECTED = booleanPreferencesKey("google_home_connected")
    }

    val settingsFlow: Flow<AppSettings> = context.dataStore.data.map { prefs ->
        AppSettings(
            openAiApiKey = prefs[Keys.OPENAI_API_KEY] ?: "",
            homeAssistantUrl = prefs[Keys.HOME_ASSISTANT_URL] ?: "",
            homeAssistantToken = prefs[Keys.HOME_ASSISTANT_TOKEN] ?: "",
            homeAssistantConnected = prefs[Keys.HOME_ASSISTANT_CONNECTED] ?: false,
            mqttBrokerUrl = prefs[Keys.MQTT_BROKER_URL] ?: "",
            mqttUsername = prefs[Keys.MQTT_USERNAME] ?: "",
            mqttPassword = prefs[Keys.MQTT_PASSWORD] ?: "",
            smartThingsToken = prefs[Keys.SMARTTHINGS_TOKEN] ?: "",
            googleHomeConnected = prefs[Keys.GOOGLE_HOME_CONNECTED] ?: false
        )
    }

    suspend fun saveSettings(settings: AppSettings) {
        context.dataStore.edit { prefs ->
            prefs[Keys.OPENAI_API_KEY] = settings.openAiApiKey
            prefs[Keys.HOME_ASSISTANT_URL] = settings.homeAssistantUrl
            prefs[Keys.HOME_ASSISTANT_TOKEN] = settings.homeAssistantToken
            prefs[Keys.HOME_ASSISTANT_CONNECTED] = settings.homeAssistantConnected
            prefs[Keys.MQTT_BROKER_URL] = settings.mqttBrokerUrl
            prefs[Keys.MQTT_USERNAME] = settings.mqttUsername
            prefs[Keys.MQTT_PASSWORD] = settings.mqttPassword
            prefs[Keys.SMARTTHINGS_TOKEN] = settings.smartThingsToken
            prefs[Keys.GOOGLE_HOME_CONNECTED] = settings.googleHomeConnected
        }
    }

    suspend fun getOpenAiKey(): String {
        var key = ""
        context.dataStore.data.collect { prefs ->
            key = prefs[Keys.OPENAI_API_KEY] ?: ""
        }
        return key
    }
}
