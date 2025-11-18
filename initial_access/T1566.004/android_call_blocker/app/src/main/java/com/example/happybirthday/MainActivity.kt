package com.example.happybirthday

import android.app.role.RoleManager
import android.media.MediaPlayer
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext

import kotlinx.coroutines.delay


class MainActivity : ComponentActivity() {
    private var mediaPlayer: MediaPlayer? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                Osnova(mediaPlayer)
            }
        }
    }
    override fun onStop() {
        super.onStop()
        mediaPlayer?.release()
        mediaPlayer = null
    }
    override fun onStart() {
        super.onStart()
        mediaPlayer = MediaPlayer.create(this, R.raw.vtornik)
        mediaPlayer?.isLooping = true
        mediaPlayer?.start()
    }
}

@Composable
fun Osnova(player: MediaPlayer?,modifier: Modifier = Modifier) {
    var mediaPlayer2 by remember { mutableStateOf<MediaPlayer?>(null) }

    val textList = listOf(
        "Пусть ненавидят, лишь бы боялись.",
        "Поживу-увижу, доживу-узнаю, выживу-учту.",
        "Не долго музыка играла, не долго фраер песню пел",
        "Не верь. Не бойся. Не проси.",
        "Вась, ебись ты в дышло!",
        "Лучше быть простым тузом,чем козырной шестеркой."
    )

    val currentText = remember { mutableStateOf(textList[0]) }
    val currentIndex = remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        while (true) {
            delay(5000) // 3 секунды
            currentIndex.value = (currentIndex.value + 1) % textList.size
            currentText.value = textList[currentIndex.value]
        }
    }

    val context = LocalContext.current
    var isOn by remember { mutableStateOf(false) }

    val roleManager = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        context.getSystemService(RoleManager::class.java)
    } else null

    val isRoleHeld = remember {
        mutableStateOf(
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                roleManager?.isRoleHeld(RoleManager.ROLE_CALL_SCREENING) == true
            } else false
        )
    }

    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && roleManager != null) {
            isRoleHeld.value = roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)
        }
    }

    val roleRequestLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && roleManager != null) {
            if (roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
                isOn = true
                isRoleHeld.value = true
            } else {
                isOn = false
                isRoleHeld.value = false
            }
        }
    }

    val image = painterResource(R.drawable.oboi_android)
    Box (
    ) {
        Image (
            painter = image,
            contentDescription = null,
            modifier = Modifier.fillMaxSize().fillMaxWidth().fillMaxHeight(),
            contentScale = ContentScale.FillBounds,
        )
        Text(
            text = "Ксива_Approver 3.0 by byte0wner",
            fontSize = 20.sp,
            color = Color.White,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .statusBarsPadding()
                .padding(top = 8.dp)
        )
        Column(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 160.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Впрячься за кента?",
                fontSize = 14.sp,
                color = Color.White,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(
                onClick = {
                    mediaPlayer2?.release()
                    mediaPlayer2 = null


                    if (isOn) {
                        val mp = MediaPlayer.create(context, R.raw.stop)
                        mp.setOnCompletionListener {
                            mp.release()
                            mediaPlayer2 = null
                        }
                        mediaPlayer2 = mp
                        mp.start()

                        isOn = false
                        AppState.isCallBlockingEnabled = false
                    } else {
                        val mp = MediaPlayer.create(context, R.raw.start)
                        mp.setOnCompletionListener {
                            mp.release()
                            mediaPlayer2 = null
                        }
                        mediaPlayer2 = mp
                        mp.start()

                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && roleManager != null) {
                            if (roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
                                isOn = true
                                AppState.isCallBlockingEnabled = true
                            } else {
                                val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING)
                                roleRequestLauncher.launch(intent)
                            }
                        } else {
                            isOn = true
                            AppState.isCallBlockingEnabled = true
                        }
                    }
                },
                colors = ButtonDefaults.textButtonColors(
                    contentColor = if (isOn) Color.Green else Color.Red
                ),
                modifier = Modifier
                    .border(
                        width = 2.dp,
                        color = if (isOn) Color.Green else Color.Red,
                        shape = RoundedCornerShape(8.dp)
                    )
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text(
                    text = "Впряг state: ${if (isOn) "On" else "Off"}",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }
        }
        Text(
            currentText.value,
            fontSize = 12.sp,
            color = Color.White,
            modifier = Modifier
                .align(Alignment.BottomStart)
                .navigationBarsPadding()
                .padding(start = 16.dp, bottom = 15.dp)
        )
    }
}