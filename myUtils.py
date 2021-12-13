# -*- coding: utf-8 -*-

import time

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
def attendToCourse(_browser, courseInfo, refreshMins=5, targetMins=60):
    courseId = courseInfo.get("courseId")
    gotoCourse(_browser, courseId)

    secs = 0
    while True:
        secs += 1
        print(f"{courseInfo} -- Count seconds: {secs} s")

        if secs % (60 * refreshMins) == 0: # 5mis, refresh not working
            gotoCourse(courseId)

        if secs == 60 * targetMins: # 1hr, break
            break

        time.sleep(1)

# 選取第4個li
def gotoVideoItem(sid):
    # switch to a specific iframe (First frame) using Id as locator
    # iframe = browser.execute_script('return document.querySelector("#CGroup iframe")')
    # print("iframe >>>>>>>>>>", iframe)
    # browser.switch_to.frame(iframe)
    # time.sleep(2)
    # browser.execute_script(f'launchActivity(this, "S16", "null")')
    # browser.switch_to.default_content()
    pass