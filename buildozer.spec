[app]
title = CheryVIN
package.name = cheryvin
package.domain = com.cheryvin
source.dir = .
source.include_exts = py,png,jpg,kv,so
# 关键：排除所有 .py 源码，只打包 .so
source.exclude_exts = py
source.exclude_patterns = buildozer.spec,README.md,*.py
source.include_patterns = vinpin_core*.so,main.py

main.module = main
version = 1.0

# 核心：requirements 只保留 kivy，不暴露其他依赖
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.branch = develop
log_level = 2
warn_on_root = 0
