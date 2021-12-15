# -*- coding: utf-8 -*-
#ref. https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules

import logging
import datetime
import os, os.path

_logLevel = logging.INFO

logger = logging.getLogger()
basePath = "D:/autoCourse_logs"
if not os.path.exists(basePath):
    os.makedirs(basePath)
myFormat = '[%(levelname)1.1s %(asctime)s %(module)s: L:%(lineno)d] %(message)s'
myDatefmt = '%Y%m%d %H:%M:%S'
log_filename = basePath + "/autoCourse_" + datetime.datetime.now().strftime("%Y-%m-%d.log")
logging.basicConfig(level=_logLevel, filename=log_filename, encoding='utf-8', filemode='a', # append
    format=myFormat,
    datefmt=myDatefmt,
)

# 設定 console 輸出
ch = logging.StreamHandler()
ch.setLevel(_logLevel)
ch.setFormatter(logging.Formatter(myFormat, datefmt=myDatefmt))

logger.addHandler(ch)