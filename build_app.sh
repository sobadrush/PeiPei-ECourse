#!/bin/bash

# 確保已安裝 PyInstaller
echo "📦 安裝/更新 PyInstaller..."
uv pip install pyinstaller

# 清理舊的構建檔案與日誌
echo "🧹 清理舊的構建檔案..."
rm -f "$LOG_FILE"
rm -rf build dist *.spec

# 執行打包
# --windowed: 產生 macOS .app 應用程式 (無黑窗)
# --onedir: 這是預設值，對於 .app 來說通常比 --onefile 啟動更快且容錯較高
# --clean: 清除快取
# --name: 應用程式名稱
echo "🚀開始打包..."
uv run pyinstaller --noconfirm --clean \
    --windowed \
    --name "PeiPei-ECourse" \
    --icon "build_icons/Bazzi_icon.png" \
    --collect-all "selenium" \
    --collect-all "webdriver_manager" \
    guiCourse.py

echo "✅ 打包完成！"
echo "👉 應用程式位於: dist/PeiPei-ECourse.app"
echo "您可以直接雙擊該 .app 檔案來執行。"
