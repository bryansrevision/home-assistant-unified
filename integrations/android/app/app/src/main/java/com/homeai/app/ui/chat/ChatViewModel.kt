package com.homeai.app.ui.chat

import android.app.Application
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.homeai.app.ai.AIAssistant
import com.homeai.app.integrations.DeviceRepository
import com.homeai.app.models.ChatMessage
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ChatViewModel @Inject constructor(
    application: Application,
    private val aiAssistant: AIAssistant,
    private val deviceRepository: DeviceRepository
) : AndroidViewModel(application) {

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun sendMessage(text: String) {
        if (text.isBlank()) return
        
        val userMessage = ChatMessage(content = text, isFromUser = true)
        _messages.value = _messages.value + userMessage
        _isLoading.value = true
        
        viewModelScope.launch {
            try {
                val devices = deviceRepository.getAllDevices()
                aiAssistant.processMessage(text, devices).collect { response ->
                    _messages.value = _messages.value + response
                }
            } catch (e: Exception) {
                val errorMessage = ChatMessage(
                    content = "Sorry, I encountered an error: ${e.message}",
                    isFromUser = false
                )
                _messages.value = _messages.value + errorMessage
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun startVoiceInput() {
        // Voice input would be handled by the Activity
        // This is a placeholder for the intent
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Say a command...")
        }
        // The actual voice handling would be in the Activity
    }

    fun clearChat() {
        _messages.value = emptyList()
        aiAssistant.clearHistory()
    }
}
