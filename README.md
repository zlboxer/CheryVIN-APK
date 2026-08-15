# CheryVIN - 奇瑞 VIN→PIN 计算工具

Android APK 工具，输入 17 位 VIN 码，计算对应 PIN 码。

## 源码保护

核心算法通过 **Nuitka** 编译为原生 `.so` 动态库，APK 内**不含任何 Python 源码**：

```
vinpin_core.py  ──Nuitka──▶  vinpin_core.cpython-310-*.so  (stripped ELF)
                                                    │
                                                    ▼
                                          Buildozer 打包进 APK
                                          (APK 内无 .py / .pyc)
```

反编译难度：需 IDA Pro / Ghidra 逆向 `.so`，门槛极高。

## 本地开发

```bash
# 1. 安装依赖
pip install nuitka kivy buildozer

# 2. 编译核心为 .so
python build_nuitka.py

# 3. 运行 UI 测试
python main.py

# 4. 打包 APK (需 Linux + Android SDK)
buildozer android debug
```

## GitHub Actions 自动构建

推送代码到 `main` 分支后自动触发：
1. Nuitka 编译核心 → `.so`
2. 删除 `.py` 源码
3. Buildozer 打包 APK
4. 上传 Artifact `CheryVIN-release`

下载地址：仓库 Actions 页面 → 最新构建 → Artifacts。

## 使用

1. 输入 17 位 VIN 码（字母自动大写）
2. 点击「计算 PIN 码」
3. 显示结果 + 历史记录

## License

Private - All rights reserved.
