# -*- coding: utf-8 -*-

import time
from base_logger import logger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

# 跳轉到【我修的課】&& 篩選【未通過】課程
def gotoChoosedCourseAndFilter(_browser):
    # 1. 進入[我修的課]
    # time.sleep(5)
    # browser.execute_script('''document.querySelector(".action__button-text").click()''')
    # time.sleep(1)
    # browser.execute_script('''document.querySelectorAll(".menu__link")[0].click()''')
    time.sleep(1)
    _browser.execute_script(f'document.location.href = "https://moocs.moe.edu.tw/moocs/#/course/my-learning"')

    # 2. 篩選【未完成】課程
    time.sleep(2)
    _browser.execute_script('''document.querySelector(".mat-form-field-infix").click()''')
    time.sleep(1)
    _browser.execute_script('''document.querySelector("mat-option[value='uncompleted']").click()''')

# 上課並累計時數
def attendToCourse(_browser, idx, courseInfo, refreshSecs=5 * 60, neededSecs=60 * 60):

    time.sleep(2)
    tdArr = _browser.find_elements(By.XPATH, "//td[@moocsenterevent='']") # 可被點擊的超連結 td
    tdArr[idx].click();
    time.sleep(2)

    secs = 0
    while True:
        secs += 1
        logger.info(f"{courseInfo} -- Count seconds: {secs} s")

        # if secs % refreshSecs == 0: # default 5mis refresh, selenium refresh not working
        #    gotoCourse(_browser, courseId)

        if secs == neededSecs: # default: 1hr, break
            break

        time.sleep(1)

# # 跳轉到特定課程
# def gotoCourse(_browser, courseId):
#     _browser.execute_script(f'document.location.href = "{"/" + courseId}"')

# # 上課並累計時數
# def attendToCourse(_browser, courseInfo, refreshSecs=5 * 60, neededSecs=60 * 60):
#     courseId = courseInfo.get("courseId")
#     gotoCourse(_browser, courseId)

#     secs = 0
#     while True:
#         secs += 1
#         logger.info(f"{courseInfo} -- Count seconds: {secs} s")

#         if secs % refreshSecs == 0: # default 5mis refresh, selenium refresh not working
#             gotoCourse(_browser, courseId)

#         if secs == neededSecs: # default: 1hr, break
#             break

#         time.sleep(1)

# ref: Google: python hh mm ss to seconds
# https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
def convertToSecs(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# 根據 xpath 判斷元素是否存在
# Xpath (XML Path Language)，是W3C定義的選擇節點的語言
# descendant - 定位子孫節點
def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

if __name__ == '__main__':
    print(convertToSecs("00:15:01"))
    print(convertToSecs("01:00:00") - convertToSecs("00:15:01"))
    
    # arr = ['111', '222', '333', '444', '555']
    # print(arr[1:]) # 從索引 1 取到最末