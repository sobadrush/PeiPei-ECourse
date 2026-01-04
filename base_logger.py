# -*- coding: utf-8 -*-
#ref. https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules

import logging
import os
from logging.handlers import RotatingFileHandler

_logLevel = logging.INFO

logger = logging.getLogger()
logger.setLevel(_logLevel)

import sys

# 設定日誌目錄
if getattr(sys, 'frozen', False):
    # 打包後的執行環境
    if sys.platform == 'darwin':
        # macOS: 往上找 3 層 (Contents/MacOS/ -> .app/ -> 所在目錄)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "../../.."))
        
        # [修復] 檢查是否處於 App Translocation (隔離環境)
        # 如果路徑包含 /private/var/.../AppTranslocation/...，代表被 macOS 隔離，
        # 此時寫入同級目錄會導致檔案消失在隨機路徑中。
        # 這種情況下，強制改寫入 ~/Documents/PeiPei-ECourse/autoCourse_logs
        if "AppTranslocation" in base_dir or not os.access(base_dir, os.W_OK):
             base_dir = os.path.expanduser("~/Documents/PeiPei-ECourse")
        
        basePath = os.path.join(base_dir, "autoCourse_logs")
    else:
        # Windows: 寫入執行檔所在目錄下的 autoCourse_logs
        basePath = os.path.join(os.path.dirname(sys.executable), "autoCourse_logs")
else:
    # 開發環境: 寫入當前目錄
    basePath = "./autoCourse_logs"
    
if not os.path.exists(basePath):
    try:
        os.makedirs(basePath)
    except OSError:
        # [修復] 若無法建立目錄 (權限不足或隔離)，回退到使用者文件夾
        # 這樣使用者至少還能找到日誌
        basePath = os.path.expanduser("~/Documents/PeiPei-ECourse/build_logs_fallback")
        if not os.path.exists(basePath):
            os.makedirs(basePath)

myFormat = '[%(levelname)1.1s %(asctime)s %(module)s: L:%(lineno)d] %(message)s'
myDatefmt = '%Y%m%d %H:%M:%S'
formatter = logging.Formatter(myFormat, datefmt=myDatefmt)

# 設定 RotatingFileHandler (30MB 上限, 保留 7 份)
log_filename = os.path.join(basePath, "autoCourse.log")
file_handler = RotatingFileHandler(
    log_filename, 
    maxBytes=30 * 1024 * 1024, # 30 MB
    backupCount=7, 
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(_logLevel)

# 設定 Console 輸出
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(_logLevel)

# 清除舊的 handler 避免重複 (如果有的話)
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)
logger.addHandler(console_handler)