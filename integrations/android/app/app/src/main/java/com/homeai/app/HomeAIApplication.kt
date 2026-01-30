package com.homeai.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class HomeAIApplication : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
