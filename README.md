# 奇瑞 VIN → PIN 计算器

一款通过 VIN 码计算 PIN 码的安卓工具。

## 使用方式

1. 打开 App，输入 17 位 VIN 码
2. 点击「计算 PIN 码」按钮
3. 结果将显示在屏幕下方

## 本地开发

```bash
pip install kivy
python main.py
```

## 自动构建

Push 代码后，在 GitHub Actions 中手动触发 `Build APK` 工作流，构建完成后下载 APK 产物即可。
