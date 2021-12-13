# -*- coding: utf-8 -*-

import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 跳轉到特定課程
def gotoCourse(courseId):
    browser.execute_script(f'document.location.href = "{"/" + courseId}"')

# 上課並累計時數
def attendToCourse(courseInfo, refreshMins=5, targetMins=60):
    courseId = courseInfo.get("courseId")
    gotoCourse(courseId)

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

if __name__ == '__main__':

    acctUsername = input("請輸登入入帳號:") or "tvbear8068"
    acctPassword = input("請輸入登入密碼:") or "Jullie20090824"
    
    options = Options()
    #options.add_argument("--disable-notifications")  # 取消所有的alert彈出視窗
    
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    browser.get("https://ups.moe.edu.tw/mooc/index.php")

    loginBtn = browser.find_element_by_class_name('btLogin')
    loginBtn.click()

    ### 
    eduActLoginBtn = browser.execute_script('''
        return document.querySelector("a[href*='https://oidc.tanet.edu.tw/oidc/v1/azp']");
    ''')
    eduActLoginBtn.click()

    ### 輸入帳密
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入帳號']").value="{acctUsername}"''')
    browser.execute_script(f'''document.querySelector("input[placeholder='請輸入密碼']").value="{acctPassword}"''')
    # 手動輸入圖形驗證碼
    time.sleep(15)

    # 我的課程
    browser.execute_script('''document.querySelector("a[href='/mooc/profile.php']").click()''')

    # 選課清單
    myCourseUrl="https://ups.moe.edu.tw/mooc/user/mycourse.php"
    curseTrList = browser.execute_script('''return document.querySelectorAll(".table.subject.row")[1].tBodies[0].children''')
    print(f"curseTrList = {curseTrList}")
    print(f"len(curseTrList) = {len(curseTrList)}")

    courseList = [] # 課程List
    for curseTr in curseTrList:
        courseName = curseTr.find_elements_by_tag_name("td")[2].text
        accmulateTime = curseTr.find_elements_by_tag_name("td")[5].text
        print(f"accmulateTime : {accmulateTime}")
        accmulateHours = int(accmulateTime.split(":")[0])
        if accmulateHours < 1: # 累計時數1小時以下的才去掛課
            goToCourseStr = curseTr.get_attribute("onclick")
            courseId = re.search("\(([^)]+)\)", goToCourseStr).group(1)
            courseList.append({"courseName": courseName, "courseId": courseId})

    print(f"All choose courses : {courseList}")

    for idx, courseInfo in enumerate(courseList):
        print(idx, courseInfo)
        attendToCourse(courseInfo)
        print(f"課程「{courseInfo.get('courseName')}」結束!")

    browser.close()
    