# -*- coding: utf-8 -*-

import time
import re
import base64
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
    
    # Selenium 4.x 的標準寫法
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.get("https://moocs.moe.edu.tw/moocs/#/home")
    browser.maximize_window()

    # 若有彈出 dialog → 關閉
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

    ### 使用 [教育雲端帳號] 或 [縣市帳號登入]
    eduActLoginBtn = browser.find_element(By.CSS_SELECTOR, ".login-link__guide-title")
    eduActLoginBtn.click()

    # 等待頁面跳轉至 [教育雲端登入頁]
    time.sleep(2) 

    ### 輸入帳密
    try:
        # 等待帳號輸入框出現
        wait = WebDriverWait(browser, 5)
        user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='請輸入帳號']")))
        
        # 使用 execute_script 設定值
        browser.execute_script(f'arguments[0].value="{acctUsername}";', user_input)
        
        # 密碼輸入框
        pwd_input = browser.find_element(By.CSS_SELECTOR, "input[placeholder='請輸入密碼']")
        browser.execute_script(f'arguments[0].value="{base64.b64decode(acctPassword).decode("UTF-8")}";', pwd_input)
    except TimeoutException:
        logger.error("在指定時間內找不到帳號或密碼輸入框，請檢查是否已成功跳轉至登入頁面。")
        raise
    
    # 停最多 20 秒用來手動輸入圖形驗證碼
    # 若提早手動點擊登入按鈕，則會因找不到按鈕而提早結束等待
    total_wait = 20
    for i in range(total_wait, 0, -1):
        if not browser.find_elements(By.ID, "id15"):
            break
        
        # 在網頁按鈕上顯示倒數 (Javascript 注入)
        try:
            browser.execute_script(f'''
                var btn = document.getElementById("id15");
                if (btn) {{
                    btn.innerText = "登入 (倒數 " + {i} + "s)";
                    btn.style.border = "3px solid red"; // 增加紅框提醒
                }}
            ''')
        except:
            pass
        time.sleep(1)

    # 嘗試執行點擊（若使用者已手動點擊或按 Enter 登入，則會忽略此處的找不到元素錯誤）
    try:
        browser.find_element(By.ID, "id15").click()
    except:
        pass

    # 跳轉到【我修的課】&& 篩選【進行中】課程
    gotoChoosedCourseAndFilter(browser)

    # 查找出【進行中】課程名稱
    time.sleep(1)
    courseTrList = browser.execute_script('''
        return document.querySelectorAll(".table__accordion-head");
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
        gotoChoosedCourseAndFilter(browser) # 跳轉到【我修的課】&& 篩選【進行中】課程

    browser.close()