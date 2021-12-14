# -*- coding: utf-8 -*-

import time
import re
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

from myUtils import *
# from myUtils import attendToCourse

if __name__ == '__main__':

    acctUsername = input("請輸登入入帳號:") or "tvbear8068"
    acctPassword = base64.b64encode(input("請輸入登入密碼:").encode("UTF-8") ) or "SnVsbGllMjAwOTA4MjQ="

    options = Options()
    #options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
    
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    browser.get("https://ups.moe.edu.tw/mooc/index.php")
    browser.maximize_window()

    loginBtn = browser.find_element(By.CLASS_NAME, 'btLogin')
    loginBtn.click()

    ### 
    eduActLoginBtn = browser.execute_script('''
        return document.querySelector("a[href*='https://oidc.tanet.edu.tw/oidc/v1/azp']");
    ''')
    eduActLoginBtn.click()

    ### 輸入帳密
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入帳號']").value="{acctUsername}"''')
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入密碼']").value="{base64.b64decode(acctPassword).decode("UTF-8")}"''')
    
    time.sleep(12) # 停12秒用來手動輸入圖形驗證碼

    # 我的課程
    browser.execute_script('''document.querySelector("a[href='/mooc/profile.php']").click()''')

    # 選課清單
    myCourseUrl="https://ups.moe.edu.tw/mooc/user/mycourse.php"
    curseTrList = browser.execute_script('''return document.querySelectorAll(".table.subject.row")[1].tBodies[0].children''')
    time.sleep(3)
    print(f"curseTrList = {curseTrList}")
    print(f"len(curseTrList) = {len(curseTrList)}")

    courseList = [] # 課程List
    for curseTr in curseTrList:
        tdArr = curseTr.find_elements(By.TAG_NAME, "td")
        # print(f"tdArr : {tdArr}")
        # print(f"tdArr[2] : {tdArr[2]}")
        # print(f"tdArr[5] : {tdArr[5]}")
        courseName = tdArr[2].text
        accmulateTime = tdArr[5].text
        print(f"courseName : {courseName}")
        print(f"accmulateTime : {accmulateTime}")
        accmulateSecs = convertToSecs(accmulateTime) # 轉換成 second
        if accmulateSecs < convertToSecs("01:00:00"): # 累計時數1小時以下的才去掛課
            goToCourseStr = curseTr.get_attribute("onclick")
            courseId = re.search("\(([^)]+)\)", goToCourseStr).group(1) # 取得括號中的courseId → ex: gotoCourse("10041")
            needSecs = convertToSecs("01:00:00") - convertToSecs(accmulateTime) # 需多少時間(秒)
            courseList.append({ "courseName": courseName, "courseId": courseId, "needSecs": needSecs })

    print("=========================================================")
    print(f"@@@ 需要掛時間的課程 @@@ : {courseList}")
    print("=========================================================")

    for idx, courseInfo in enumerate(courseList):
        print(idx, courseInfo)
        attendToCourse(browser, courseInfo, neededSecs=int(courseInfo.get("needSecs")))
        print(f"課程「{courseInfo.get('courseName')}」結束!")

    browser.close()