#!/usr/bin/env python3
"""
编译 vinpin_core.py → .so (Nuitka)
删除源码，只保留 .so
"""
import subprocess, sys, os, glob, shutil

CORE = "vinpin_core.py"

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=False)
    if r.returncode != 0:
        print(f"❌ 失败: {r.returncode}")
        sys.exit(1)

# 确保源码存在
if not os.path.exists(CORE):
    print(f"❌ {CORE} 不存在！")
    sys.exit(1)

# 清理旧产物
for f in glob.glob("vinpin_core.*.so") + glob.glob("vinpin_core.bin") + glob.glob("vinpin_core.c"):
    os.remove(f)
    print(f"  删除旧: {f}")

# Nuitka 编译
print("🔨 编译中 (Nuitka --lto=yes)...")
run([
    sys.executable, "-m", "nuitka",
    "--module", CORE,
    "--lto=yes",
    "--remove-output",
    "--no-progressbar",
    "--assume-yes-for-downloads",
    "-o", "vinpin_core.so"
])

# 找产物
so_files = glob.glob("vinpin_core.*.so")
if not so_files:
    # Nuitka 可能输出为 .so 或带后缀
    so_files = glob.glob("*.so") + glob.glob("vinpin_core*.so")
if not so_files:
    print("❌ 找不到编译产物 .so")
    sys.exit(1)

so = so_files[0]
print(f"✅ 编译产物: {so} ({os.path.getsize(so)} bytes)")

# strip
run(["strip", so])
print(f"✅ strip 完成: {so} ({os.path.getsize(so)} bytes)")

# 删除源码
os.remove(CORE)
print(f"🗑️ 已删除 {CORE}")

# 验证
print("\n🧪 验证: 仅 .so 能否正常 import...")
test = subprocess.run(
    [sys.executable, "-c",
     f"import sys; sys.path.insert(0,'.'); import vinpin_core; pin=vinpin_core.vin_to_pin('LSJCRF3H0HX000001'); print(f'PIN={pin}')"],
    capture_output=True, text=True
)
if test.returncode == 0:
    print(f"  ✅ {test.stdout.strip()}")
    print(f"\n🎉 完成！APK 中将只包含 {so}，无 Python 源码")
else:
    print(f"  ❌ {test.stderr.strip()[:200]}")
    sys.exit(1)
