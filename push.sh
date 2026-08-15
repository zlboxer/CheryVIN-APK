#!/bin/bash
# 用法: GITHUB_TOKEN=你的token bash push.sh
# 或直接编辑下方 TOKEN 变量后运行
set -e

TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "❌ 请设置 GITHUB_TOKEN 环境变量"
    echo "   例如: GITHUB_TOKEN=ghp_xxx bash push.sh"
    exit 1
fi

# 用 token 做鉴权推送
git remote remove origin 2>/dev/null || true
git remote add origin "https://${TOKEN}@github.com/zlboxer/CheryVIN-APK.git"

echo "▶ 推送到 zlboxer/CheryVIN-APK (main 分支) ..."
git push -u origin main --force

echo ""
echo "✅ 推送完成！"
echo "   打开 https://github.com/zlboxer/CheryVIN-APK/actions 查看 APK 构建进度"
echo "   构建完成后在 Actions → Artifacts 下载 cheryvin-release.apk"
