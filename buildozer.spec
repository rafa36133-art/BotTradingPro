[app]
title = BotTradingPro
package.name = bottradingpro
package.domain = com.trading.bot
source.dir = .
source.main = main.py
version = 1.0
requirements = python3,kivy==2.3.0,pillow==10.3.0,kivymd==1.2.0,plyer,python-binance==1.0.19,python-dotenv==1.0.1,requests
orientation = portrait
android.api = 33
android.ndk = 25.2.9519653
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.skip_update = True
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS

[buildozer]
log_level = 2
warn_on_root = 1
android.ndk_download = False
android.sdk_download = False
