[app]
title = BotTradingPro
package.name = bottradingpro
package.domain = com.trading.bot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,env
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,python-binance,python-dotenv,requests,urllib3,chardet,idna,certifi,six,python-dateutil
orientation = portrait
fullscreen = 0
android.api = 33
android.ndk = 25b
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK, FOREGROUND_SERVICE, POST_NOTIFICATIONS
android.apptheme = @android:style/Theme.Material.Light.NoActionBar
android.allowBackups = True
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
