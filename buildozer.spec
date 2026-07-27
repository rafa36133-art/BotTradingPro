[app]
title = BotTradingPro
package.name = bottradingpro
package.domain = com.trading.bot
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,json,env,txt
version = 1.0

requirements = python3,kivy==2.3.0,pillow,kivymd==1.2.0,plyer,python-binance==1.0.19,python-dotenv==1.0.1,requests

orientation = portrait
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE,POST_NOTIFICATIONS,RECEIVE_BOOT_COMPLETED
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1
