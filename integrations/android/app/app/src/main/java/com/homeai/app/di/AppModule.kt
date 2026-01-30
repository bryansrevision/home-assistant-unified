package com.homeai.app.di

import android.content.Context
import com.homeai.app.ai.DeviceController
import com.homeai.app.ai.OpenAIService
import com.homeai.app.ai.OpenAIServiceImpl
import com.homeai.app.integrations.*
import com.homeai.app.integrations.homeassistant.HomeAssistantClient
import com.homeai.app.integrations.mqtt.MqttClient
import com.homeai.app.integrations.smartthings.SmartThingsClient
import com.homeai.app.utils.SettingsDataStore
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class AppModule {

    @Binds
    @Singleton
    abstract fun bindDeviceRepository(impl: DeviceRepositoryImpl): DeviceRepository

    @Binds
    @Singleton
    abstract fun bindDeviceController(impl: DeviceRepositoryImpl): DeviceController

    @Binds
    @Singleton
    abstract fun bindIntegrationManager(impl: IntegrationManagerImpl): IntegrationManager

    @Binds
    @Singleton
    abstract fun bindOpenAIService(impl: OpenAIServiceImpl): OpenAIService
}

@Module
@InstallIn(SingletonComponent::class)
object ProvidersModule {

    @Provides
    @Singleton
    fun provideSettingsDataStore(
        @ApplicationContext context: Context
    ): SettingsDataStore = SettingsDataStore(context)

    @Provides
    @Singleton
    fun provideHomeAssistantClient(): HomeAssistantClient = HomeAssistantClient()

    @Provides
    @Singleton
    fun provideMqttClient(
        @ApplicationContext context: Context
    ): MqttClient = MqttClient(context)

    @Provides
    @Singleton
    fun provideSmartThingsClient(): SmartThingsClient = SmartThingsClient()
}
