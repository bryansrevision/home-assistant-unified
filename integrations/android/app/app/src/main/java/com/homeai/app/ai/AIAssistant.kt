package com.homeai.app.ai

import com.homeai.app.models.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AIAssistant @Inject constructor(
    private val openAIService: OpenAIService,
    private val deviceController: DeviceController
) {
    private val conversationHistory = mutableListOf<ChatMessage>()
    
    private val systemPrompt = """
        You are HomeAI, a friendly and helpful AI assistant for smart home control.
        You can control lights, switches, thermostats, locks, and other smart devices.
        
        When the user asks to control a device, respond naturally and include the action.
        Available commands you can understand:
        - Turn on/off lights, switches, devices
        - Set brightness (0-100%)
        - Set temperature (thermostat)
        - Lock/unlock doors
        - Adjust blinds/shades
        - Create scenes and routines
        
        Always be helpful, concise, and confirm actions taken.
        If you don't understand a request, ask for clarification.
    """.trimIndent()

    suspend fun processMessage(userMessage: String, devices: List<Device>): Flow<ChatMessage> = flow {
        conversationHistory.add(ChatMessage(content = userMessage, isFromUser = true))
        
        // Parse intent and extract device commands
        val intent = parseIntent(userMessage, devices)
        
        // Execute device actions if detected
        val actionResults = mutableListOf<String>()
        intent.deviceActions.forEach { action ->
            val result = deviceController.executeAction(action)
            actionResults.add(result)
        }
        
        // Generate AI response
        val response = if (intent.deviceActions.isNotEmpty()) {
            generateActionResponse(intent, actionResults)
        } else {
            openAIService.generateResponse(systemPrompt, conversationHistory, devices)
        }
        
        val aiMessage = ChatMessage(
            content = response,
            isFromUser = false,
            deviceAction = intent.deviceActions.firstOrNull()
        )
        conversationHistory.add(aiMessage)
        emit(aiMessage)
    }

    private fun parseIntent(message: String, devices: List<Device>): UserIntent {
        val lowerMessage = message.lowercase()
        val actions = mutableListOf<DeviceAction>()
        
        // Simple intent parsing - can be enhanced with NLP
        devices.forEach { device ->
            val deviceNameLower = device.name.lowercase()
            if (lowerMessage.contains(deviceNameLower) || lowerMessage.contains(device.room.lowercase())) {
                when {
                    lowerMessage.contains("turn on") || lowerMessage.contains("switch on") -> {
                        actions.add(DeviceAction(device.id, device.name, "turn_on"))
                    }
                    lowerMessage.contains("turn off") || lowerMessage.contains("switch off") -> {
                        actions.add(DeviceAction(device.id, device.name, "turn_off"))
                    }
                    lowerMessage.contains("brightness") -> {
                        val brightness = extractNumber(lowerMessage) ?: 50
                        actions.add(DeviceAction(device.id, device.name, "set_brightness", 
                            mapOf("brightness" to brightness)))
                    }
                    lowerMessage.contains("temperature") || lowerMessage.contains("degrees") -> {
                        val temp = extractNumber(lowerMessage)?.toDouble() ?: 72.0
                        actions.add(DeviceAction(device.id, device.name, "set_temperature", 
                            mapOf("temperature" to temp)))
                    }
                    lowerMessage.contains("lock") -> {
                        actions.add(DeviceAction(device.id, device.name, "lock"))
                    }
                    lowerMessage.contains("unlock") -> {
                        actions.add(DeviceAction(device.id, device.name, "unlock"))
                    }
                }
            }
        }
        
        // Handle room-level commands
        if (actions.isEmpty()) {
            val rooms = listOf("living room", "bedroom", "kitchen", "bathroom", "office", "garage")
            rooms.forEach { room ->
                if (lowerMessage.contains(room)) {
                    val roomDevices = devices.filter { it.room.lowercase() == room }
                    if (lowerMessage.contains("turn on") || lowerMessage.contains("lights on")) {
                        roomDevices.filter { it.type == DeviceType.LIGHT }.forEach {
                            actions.add(DeviceAction(it.id, it.name, "turn_on"))
                        }
                    } else if (lowerMessage.contains("turn off") || lowerMessage.contains("lights off")) {
                        roomDevices.filter { it.type == DeviceType.LIGHT }.forEach {
                            actions.add(DeviceAction(it.id, it.name, "turn_off"))
                        }
                    }
                }
            }
        }
        
        return UserIntent(message, actions)
    }

    private fun extractNumber(text: String): Int? {
        val regex = Regex("\\d+")
        return regex.find(text)?.value?.toIntOrNull()
    }

    private fun generateActionResponse(intent: UserIntent, results: List<String>): String {
        val actions = intent.deviceActions
        return when {
            actions.isEmpty() -> "I'm not sure what you'd like me to do. Could you please clarify?"
            actions.size == 1 -> {
                val action = actions.first()
                "Done! I've ${action.action.replace("_", " ")} ${action.deviceName}."
            }
            else -> {
                val deviceNames = actions.map { it.deviceName }.joinToString(", ")
                "Done! I've updated these devices: $deviceNames"
            }
        }
    }

    fun clearHistory() {
        conversationHistory.clear()
    }
}

data class UserIntent(
    val originalMessage: String,
    val deviceActions: List<DeviceAction>
)

interface DeviceController {
    suspend fun executeAction(action: DeviceAction): String
}

interface OpenAIService {
    suspend fun generateResponse(
        systemPrompt: String,
        history: List<ChatMessage>,
        devices: List<Device>
    ): String
}
