# -*- coding: utf-8 -*-

import time
import datetime
import logging

import os, os.path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 跳轉到特定課程
def gotoCourse(_browser, courseId):
    _browser.execute_script(f'document.location.href = "{"/" + courseId}"')

# 上課並累計時數
def attendToCourse(_browser, courseInfo, refreshSecs=5 * 60, neededSecs=60 * 60):
    courseId = courseInfo.get("courseId")
    gotoCourse(_browser, courseId)

    secs = 0
    while True:
        secs += 1
        print(f"{courseInfo} -- Count seconds: {secs} s")

        if secs % refreshSecs == 0: # default 5mis refresh, selenium refresh not working
            gotoCourse(_browser, courseId)

        if secs == neededSecs: # default: 1hr, break
            break

        time.sleep(1)

# ref: Google: python hh mm ss to seconds
# https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
def convertToSecs(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def initLogging(_logLevel=logging.DEBUG):
    logger = logging.getLogger()
    basePath = "D:/autoCourse_logs"
    if not os.path.exists(basePath):
        os.makedirs(basePath)
    myFormat = '[%(levelname)1.1s %(asctime)s %(module)s: L:%(lineno)d] %(message)s'
    myDatefmt = '%Y%m%d %H:%M:%S'
    log_filename = basePath + "/autoCourse_" + datetime.datetime.now().strftime("%Y-%m-%d.log")
    logging.basicConfig(level=_logLevel, filename=log_filename, filemode='a', # append
        format=myFormat,
        datefmt=myDatefmt,
    )
    ch = logging.StreamHandler()
    ch.setLevel(_logLevel)
    ch.setFormatter(logging.Formatter(myFormat, datefmt=myDatefmt))
    logger.addHandler(ch)
    return logger

if __name__ == '__main__':
    # print(convertToSecs("00:15:01"))
    print(convertToSecs("01:00:00") - convertToSecs("00:15:01"))
    