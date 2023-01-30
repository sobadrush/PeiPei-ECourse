# -*- coding: utf-8 -*-

import time
import re
import base64
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

from myUtils import *
from base_logger import logger
# from myUtils import attendToCourse

if __name__ == '__main__':

    acctUsername = input("請輸入登入帳號：") or "tvbear8068"
    acctPassword = base64.b64encode(input("請輸入登入密碼：").encode("UTF-8") ) or "SnVsbGllMjAwOTA4MjQ="
    # targetHHmmss = input("請輸入課程目標時數(格式: HH:MM:SS，不輸入預設為 01:15:00)：") or "01:15:00"
    startCourseIndex = input("請輸入要開始掛課程的課程編號(預設為1)：") or "1"

    options = Options()
    #options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
    
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    browser.get("https://moocs.moe.edu.tw/moocs/#/home")
    browser.maximize_window()

    # 若有彈出dialog → 關閉
    # 使用 xpath 查詢 id 叫 uploadHourModal 的 div 下的 class='close' 的 button ( document.querySelector("#uploadHourModal button[class='close']").click() )
    if check_exists_by_xpath(browser, "//div[@id='uploadHourModal']/descendant::button[@class='close']"):
        print("Dialog Button Exists, let's close it!")
        closeDialogBtn = browser.find_element(By.ID, "uploadHourModal").find_element(By.CLASS_NAME, "close")
        closeDialogBtn.click()
    else:
        print("Dialog Button Not Exists.")
    
    time.sleep(2)
    loginBtn = browser.find_element(By.CLASS_NAME, 'action__button-text')
    loginBtn.click()
    time.sleep(1)

    ### 使用教育雲端帳號或縣市帳號登入
    eduActLoginBtn = browser.execute_script('''
        return document.querySelector(".login-link__guide-title");
    ''')
    eduActLoginBtn.click()

    ### 輸入帳密
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入帳號']").value="{acctUsername}"''')
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入密碼']").value="{base64.b64decode(acctPassword).decode("UTF-8")}"''')
    
    time.sleep(12) # 停12秒用來手動輸入圖形驗證碼

    # 登入
    browser.find_element(By.ID, "id15").click()

    # 跳轉到【我修的課】&& 篩選【未通過】課程
    gotoChoosedCourseAndFilter(browser)

    # 查找出【未完成】課程名稱
    time.sleep(1)
    courseTrList = browser.execute_script('''
        return document.querySelectorAll("mat-expansion-panel-header tr");
    ''')

    courseList = [
        {
            "courseName": tr.text.split("\n")[1], 
            "certHours": tr.text.split("\n")[2]
        } for tr in courseTrList] # ref. https://blog.finxter.com/python-one-line-for-loop-a-simple-tutorial/
    logger.info("=========================================================")
    logger.info(f"@@@ 需要掛時間的課程 - 共 {len(courseList)} 堂 @@@")
    logger.info(f"課程名稱清單(courseList) = {courseList}")
    logger.info(f"起始課程索引 startCourseIndex = {startCourseIndex}")
    logger.info("=========================================================")

    courseList = courseList[(int(startCourseIndex)-1):] # 從 startCourseIndex 取到 last
    logger.info(f"@@@ 從指定索引開始 - 共 {len(courseList)} 堂 @@@")
    for item in courseList:
        print(item, end = ',\n')

    for idx, courseInfo in enumerate(courseList):
        logger.info(idx, courseInfo)
        attendToCourse(browser, idx + (int(startCourseIndex)-1), courseInfo, neededSecs=((int(courseInfo.get("certHours"))) * 60 * 60) + (5 * 60)) # 除認證時數外，多加5分鐘
        # attendToCourse(browser, idx + (int(startCourseIndex)-1), courseInfo, neededSecs=10) # for test
        gotoChoosedCourseAndFilter(browser) # 跳轉到【我修的課】&& 篩選【未通過】課程
        logger.info(f"課程『{courseInfo.get('courseName')}』結束!")

    browser.close()