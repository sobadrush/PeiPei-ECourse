# -*- coding: utf-8 -*-
#ref. https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules

import logging
import os
from logging.handlers import RotatingFileHandler

_logLevel = logging.INFO

logger = logging.getLogger()
logger.setLevel(_logLevel)

# 設定日誌目錄
basePath = "./logs"
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