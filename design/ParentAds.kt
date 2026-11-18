package com.mhmmad.shaplumkidsgames.ui

import android.content.Context
import androidx.activity.compose.LocalActivity
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.huawei.hms.ads.*
import com.huawei.hms.ads.banner.BannerView
import com.mhmmad.shaplumkidsgames.BuildConfig
import com.mhmmad.shaplumkidsgames.R

// This component exists exclusively inside the verified parent area.
// No SDK initialization, request or advertising choice at startup.
@Composable
internal fun ParentAdPanel(openProgress: () -> Unit, openAbout: () -> Unit) {
    val context = LocalContext.current
    val activity = LocalActivity.current
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val prefs = remember { context.applicationContext.getSharedPreferences("guardian_privacy_v1", Context.MODE_PRIVATE) }
    var accepted by remember { mutableStateOf(prefs.getLong("accepted_at", 0L) > prefs.getLong("withdrawn_at", 0L)) }
    var ready by remember { mutableStateOf(false) }
    var interstitial by remember { mutableStateOf<InterstitialAd?>(null) }
    var showing by remember { mutableStateOf(false) }
    val navigate by rememberUpdatedState(openProgress)
    val allowed = accepted && BuildConfig.ADS_ENABLED && activity != null
    DisposableEffect(allowed, activity) {
        var alive = true
        if (allowed && activity != null) {
            try {
                val options = RequestOptions.Builder()
                    .setTagForChildProtection(1)
                    .setTagForUnderAgeOfPromise(1)
                    .setNonPersonalizedAd(1)
                    .setAdContentClassification("W")
                    .build()
                HwAds.setRequestOptions(options)
                HwAds.init(context.applicationContext)
                HwAds.setRequestOptions(options)
                ready = true
                val ad = InterstitialAd(activity)
                ad.adId = if (BuildConfig.DEBUG) "testb4znbuh3n2" else BuildConfig.HUAWEI_INTERSTITIAL_ID
                ad.setVideoConfiguration(VideoConfiguration.Builder().setStartMuted(true).build())
                ad.adListener = object : AdListener() {
                    override fun onAdClosed() {
                        if (alive && showing) {
                            showing = false
                            navigate()
                        }
                    }
                    override fun onAdFailed(errorCode: Int) {
                        if (alive && showing) {
                            showing = false
                            navigate()
                        }
                    }
                }
                interstitial = ad
                ad.loadAd(AdParam.Builder().build())
            } catch (_: Exception) {
                ready = false
                interstitial = null
            } catch (_: LinkageError) {
                ready = false
                interstitial = null
            }
        }
        onDispose {
            alive = false
            runCatching { interstitial?.adListener = null }
            interstitial = null
            ready = false
            showing = false
        }
    }
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        // Required privacy acknowledgement is non-modal and behind the parent gate.
        if (BuildConfig.ADS_ENABLED && !accepted) {
            Text(stringResource(R.string.guardian_ad_privacy))
            TextButton(onClick = openAbout) { Text(stringResource(R.string.privacy_policy)) }
            OutlinedButton(onClick = {
                val now = System.currentTimeMillis()
                if (prefs.edit().putLong("accepted_at", now).putInt("policy_version", 1).commit()) accepted = true
            }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.guardian_privacy_accept)) }
        }
        Button(onClick = {
            val ad = interstitial
            val now = System.currentTimeMillis()
            val last = prefs.getLong("last_interstitial_at", 0L)
            if (allowed && ready && activity != null && lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)
                && !showing && ad != null && ad.isLoaded && now - last >= 600_000L) {
                try {
                    prefs.edit().putLong("last_interstitial_at", now).apply()
                    showing = true
                    ad.show(activity)
                } catch (_: Exception) {
                    showing = false
                    openProgress()
                }
            } else if (!showing) openProgress()
        }, enabled = !showing, modifier = Modifier.fillMaxWidth()) {
            Text(stringResource(R.string.guardian_activity_summary))
        }
        if (allowed && ready && !showing && activity != null) {
            ParentBanner()
        }
        if (BuildConfig.ADS_ENABLED && accepted) {
            TextButton(onClick = {
                if (prefs.edit().putLong("withdrawn_at", System.currentTimeMillis()).commit()) accepted = false
            }) { Text(stringResource(R.string.guardian_privacy_withdraw)) }
        }
    }
}

@Composable
private fun ParentBanner() {
    val context = LocalActivity.current ?: return
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    var loaded by remember { mutableStateOf(false) }
    val banner = remember(context) {
        BannerView(context).apply {
            adId = if (BuildConfig.DEBUG) "testw6vs28auh3" else BuildConfig.HUAWEI_BANNER_ID
            bannerAdSize = BannerAdSize.BANNER_SIZE_320_50
            setBannerRefresh(60)
            adListener = object : AdListener() {
                override fun onAdLoaded() { loaded = true }
                override fun onAdFailed(errorCode: Int) { loaded = false }
            }
        }
    }
    DisposableEffect(banner, lifecycle) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_PAUSE -> runCatching { banner.pause() }
                Lifecycle.Event.ON_RESUME -> runCatching { banner.resume() }
                else -> Unit
            }
        }
        lifecycle.addObserver(observer)
        runCatching { banner.loadAd(AdParam.Builder().build()) }
        onDispose {
            lifecycle.removeObserver(observer)
            runCatching { banner.destroy() }
        }
    }
    if (loaded) Text(stringResource(R.string.guardian_ad_label), style = MaterialTheme.typography.labelSmall)
    AndroidView(factory = { banner }, modifier = Modifier.fillMaxWidth().height(if (loaded) 50.dp else 1.dp))
}
