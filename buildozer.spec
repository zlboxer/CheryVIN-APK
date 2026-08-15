[app]
title = CheryVIN
package.name = cheryvin
package.domain = com.zlboxer
source.dir = .
source.include_exts = py,so,spec,md
# 关键：排除核心源码，只保留 .so
source.exclude_exts = pyc,pyo
source.exclude_patterns = vinpin_core.py, build_nuitka.py, push.sh, .git/*, .github/*
version = 1.0
author = zlboxer

# 不依赖 kivy 以外的第三方库
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.archs = arm64-v8a,armeabi-v7a
android.release = True

[buildozer]
log_level = 2
warn_on_root = 0
