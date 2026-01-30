package com.homeai.app.ai

import com.homeai.app.BuildConfig
import com.homeai.app.models.ChatMessage
import com.homeai.app.models.Device
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OpenAIServiceImpl @Inject constructor() : OpenAIService {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    override suspend fun generateResponse(
        systemPrompt: String,
        history: List<ChatMessage>,
        devices: List<Device>
    ): String = withContext(Dispatchers.IO) {
        
        val apiKey = BuildConfig.OPENAI_API_KEY
        if (apiKey.isBlank()) {
            return@withContext "Please configure your OpenAI API key in settings to enable AI responses."
        }

        try {
            val deviceContext = buildDeviceContext(devices)
            val fullSystemPrompt = "$systemPrompt\n\nAvailable devices:\n$deviceContext"
            
            val messages = JSONArray().apply {
                put(JSONObject().apply {
                    put("role", "system")
                    put("content", fullSystemPrompt)
                })
                
                history.takeLast(10).forEach { msg ->
                    put(JSONObject().apply {
                        put("role", if (msg.isFromUser) "user" else "assistant")
                        put("content", msg.content)
                    })
                }
            }

            val requestBody = JSONObject().apply {
                put("model", "gpt-4-turbo-preview")
                put("messages", messages)
                put("max_tokens", 500)
                put("temperature", 0.7)
            }

            val request = Request.Builder()
                .url("https://api.openai.com/v1/chat/completions")
                .addHeader("Authorization", "Bearer $apiKey")
                .addHeader("Content-Type", "application/json")
                .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: ""
            
            if (response.isSuccessful) {
                val json = JSONObject(responseBody)
                json.getJSONArray("choices")
                    .getJSONObject(0)
                    .getJSONObject("message")
                    .getString("content")
            } else {
                "I'm having trouble connecting to my AI service. Error: ${response.code}"
            }
        } catch (e: Exception) {
            "I encountered an error: ${e.message}. Please try again."
        }
    }

    private fun buildDeviceContext(devices: List<Device>): String {
        return devices.groupBy { it.room }.entries.joinToString("\n") { (room, roomDevices) ->
            "$room:\n" + roomDevices.joinToString("\n") { device ->
                "  - ${device.name} (${device.type.name.lowercase()}): ${if (device.state.isOn) "on" else "off"}"
            }
        }
    }
}
