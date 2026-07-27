[app]
title = BotTradingPro
package.name = bottradingpro
package.domain = com.trading.bot
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas,json,env,txt
version = 1.0

requirements = python3==3.10.11,hostpython3==3.10.11,kivy==2.3.0,pillow==10.3.0,charset-normalizer,idna,urllib3,certifi,requests,python-dateutil,six,plyer,python-binance==1.0.19,python-dotenv==1.0.1,kivymd==1.2.0

orientation = portrait
fullscreen = 0
android.api = 33
android.ndk = 25.2.9519653
android.archs = arm64-v8a
android.build_tools_version = 33.0.3
android.sdk_path = /home/runner/Android/Sdk
android.ndk_path = /home/runner/Android/Sdk/ndk/25.2.9519653
android.accept_sdk_license = True
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK, FOREGROUND_SERVICE, POST_NOTIFICATIONS, RECEIVE_BOOT_COMPLETED
android.apptheme = @android:style/Theme.Material.Light.NoActionBar
android.allowBackups = True
android.wakelock = True
android.use_aapt2 = True
android.release_artifact = apk
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png
presplash_color = #0B0E11

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = bin
android_builddir = .buildozer/android/platform/android-ndk
