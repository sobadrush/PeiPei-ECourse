#!/bin/bash

# 確保已安裝 PyInstaller
echo "📦 安裝/更新 PyInstaller..."
uv pip install pyinstaller

# 清理舊的構建檔案與日誌
echo "🧹 清理舊的構建檔案..."
rm -f "$LOG_FILE"
rm -rf build dist *.spec

# 檢查圖示檔案是否存在
ICON_PATH="build_icons/Bazzi_icon.png"
if [ ! -f "$ICON_PATH" ]; then
    echo "⚠️ 找不到圖示檔案: $ICON_PATH，將使用預設圖示。"
    ICON_OPTS=""
else
    ICON_OPTS="--icon $ICON_PATH"
fi

# 執行打包
# --windowed: 產生 macOS .app 應用程式 (無黑窗)
# --onedir: 這是預設值，對於 .app 來說通常比 --onefile 啟動更快且容錯較高
# --clean: 清除快取
# --name: 應用程式名稱
# --osx-bundle-identifier: macOS App 的唯一識別碼 (對於 Retina 支援與權限管理有幫助)
echo "🚀開始打包 (目標：macOS)..."
uv run pyinstaller --noconfirm --clean \
    --windowed \
    --name "PeiPei-ECourse" \
    $ICON_OPTS \
    --osx-bundle-identifier "com.rogerlo.peipei-ecourse" \
    --collect-all "selenium" \
    --collect-all "webdriver_manager" \
    guiCourse.py

echo "✅ 打包完成！"
echo "👉 應用程式位於: dist/PeiPei-ECourse.app"
echo "您可以直接雙擊該 .app 檔案來執行。"
