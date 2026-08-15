#!/usr/bin/env python3
"""Nuitka 编译脚本：将 vinpin_core.py 编译为 .so，删除源码"""
import subprocess, sys, os, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "vinpin_core.py")
SO_PATTERN = os.path.join(HERE, "vinpin_core.*.so")

# 清理旧产物
for f in glob.glob(SO_PATTERN):
    os.remove(f)
    print(f"🗑️  删除旧产物: {os.path.basename(f)}")

# Nuitka 编译
cmd = [
    sys.executable, "-m", "nuitka",
    "--module", CORE,
    "--lto=yes",
    "--remove-output",
    "--no-progressbar",
    "--output-dir=" + HERE,
]
print("🔨 编译中:", " ".join(cmd))
subprocess.run(cmd, check=True, cwd=HERE)

# 找到产物并 strip
sos = glob.glob(SO_PATTERN)
if not sos:
    print("❌ 未找到编译产物 .so")
    sys.exit(1)

so = sos[0]
# strip 减小体积+去除符号
subprocess.run(["strip", so], check=False)
size_kb = os.path.getsize(so) // 1024
print(f"✅ 编译完成: {os.path.basename(so)} ({size_kb} KB, stripped)")

# 删除源码 .py（不进 APK）
os.remove(CORE)
print(f"🗑️  删除源码: {os.path.basename(CORE)} (不会进入 APK)")
print("🎉 完成！当前目录只剩 .so + 构建配置")
