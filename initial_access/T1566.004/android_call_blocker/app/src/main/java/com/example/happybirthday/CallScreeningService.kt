package com.example.happybirthday

import android.media.MediaPlayer
import android.provider.BlockedNumberContract
import android.telecom.Call
import android.telecom.CallScreeningService
import android.util.Log

import com.example.happybirthday.AppState

class CallScreeningService : CallScreeningService() {
    private val TAG = "CallScreeningService"

    override fun onScreenCall(callDetails: Call.Details) {
        val number = callDetails.handle?.schemeSpecificPart ?: return
        Log.d(TAG, "Check call: $number")

        val shouldBlock = BlockedNumbers.contains(number) && AppState.isCallBlockingEnabled

        val response = CallResponse.Builder().apply {
            if (shouldBlock) {
                setDisallowCall(true)
                setRejectCall(true)
                setSkipCallLog(false)
                setSkipNotification(false)
            } else {
                setDisallowCall(false)
            }
        }.build()

        if (shouldBlock) {
            var mediaPlayer: MediaPlayer? = null
            val mp = MediaPlayer.create(this, R.raw.number_blocked)
            mp.setOnCompletionListener {
                mp.release()
                mediaPlayer = null
            }
            mediaPlayer = mp
            mp.start()
        }

        respondToCall(callDetails, response)
    }
}