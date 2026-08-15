# CheryVIN - VIN转PIN码工具

奇瑞汽车 VIN 码转 PIN 码计算工具，Android APK。

## 功能

输入 17 位 VIN 码 → 自动校验 → 输出 8 位 PIN 码

## 技术架构

- **UI 层**: Kivy (Python)
- **核心算法**: 编译为 `.so` (Nuitka)，源码不进 APK
- **打包**: Buildozer → Android APK

## 防逆向保护

```
vinpin_core.py → Nuitka 编译 → vinpin_core.so (stripped ELF)
                                    ↓
                        删除 .py，仅 .so 进 APK
                                    ↓
                    APK 内无 Python 源码，反编译需 IDA Pro
```

## 开发

```bash
# 编译核心为 .so
python build_nuitka.py

# 本地构建 APK (需 Android SDK/NDK)
buildozer android debug
```

## GitHub Actions 自动构建

推送代码到 `main` 分支后自动触发构建，APK 在 Actions Artifacts 中下载。

## 使用

1. 打开 App
2. 输入 17 位 VIN 码
3. 点击计算 → 显示 PIN 码
