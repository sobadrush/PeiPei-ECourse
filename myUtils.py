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


# 跳轉到【我修的課】&& 篩選【進行中】課程
def gotoChoosedCourseAndFilter(_browser):
    # 1. 進入[我修的課]
    logger.info(">>> 呼叫 gotoChoosedCourseAndFilter(), 進入[我修的課]")
    # time.sleep(5)
    # browser.execute_script('''document.querySelector(".action__button-text").click()''')
    # time.sleep(1)
    # browser.execute_script('''document.querySelectorAll(".menu__link")[0].click()''')
    time.sleep(1)
    _browser.execute_script(f'document.location.href = "https://moocs.moe.edu.tw/moocs/#/course/my-learning"')

    # 2. 篩選【進行中】課程
    time.sleep(2)
    _browser.execute_script('''document.querySelector(".mat-form-field-infix").click()''') # 點擊篩選下拉選單
    
    time.sleep(1)
    _browser.execute_script('''document.querySelector("mat-option[value='uncompleted']").click()''') # 點擊【進行中】


# 上課並累計時數
def attendToCourse(_browser, idx, courseInfo, refreshSecs=10, neededSecs=60 * 60):

    time.sleep(2)
    tdArr = _browser.find_elements(By.XPATH, "//td[@moocsenterevent='']") # 可被點擊的超連結 td
    tdArr[idx].click();
    time.sleep(2)

    secs = 0
    while secs < neededSecs:
        secs += 1
        
        # 每隔 refreshSecs 秒重新整理一次畫面
        if secs % refreshSecs == 0:
            logger.info(f"已達到 {refreshSecs} 秒，執行畫面重新整理與進度檢查...")
            _browser.refresh()
            time.sleep(5)  # 等待重新整理完成
            
            try:
                # 1. 點擊「通過標準」頁籤
                # 這裡使用包含文字的方式定位，因為 mat-tab-label-id 可能會變動
                criteria_tab = _browser.find_element(By.XPATH, "//div[contains(@class, 'mat-tab-label-content') and contains(text(), '通過標準')]")
                criteria_tab.click()
                time.sleep(2) # 等待分頁內容載入

                # 2. 檢查「閱讀時數」百分比
                # 定位策略：先找「閱讀時數」標籤，再找同層級或父層下的百分比 small 標籤
                percent_element = _browser.find_element(By.XPATH, "//span[contains(text(), '閱讀時數')]/parent::div//div[contains(@class, 'course-status__progress-info')]/small")
                percent_text = percent_element.text  # 格式如 "(72%)"
                
                # 解析數據
                import re
                match = re.search(r"(\d+)%", percent_text)
                if match:
                    progress = int(match.group(1))
                    logger.info(f"目前的閱讀時數進度：{progress}%")
                    
                    if progress >= 100:
                        logger.info("檢測到課程進度已達 100%，提前結束課程！")
                        break
            except Exception as e:
                logger.warning(f"檢查進度時發生錯誤 (可能尚未載入完成): {str(e)}")
        else:
            time.sleep(1)
            
        if secs % 10 == 0 or secs == 1: # 每 10 秒印一次 log，避免洗版，除非是第 1 秒
            logger.info(f"{courseInfo.get('courseName')} -- 已累計秒數: {secs} s / 目標秒數: {neededSecs} s")

    # 課程結束（達成時數或 100%）
    logger.info(f"課程『{courseInfo.get('courseName')}』課程結束（達成時數或 100%），準備回到課程列表...")

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