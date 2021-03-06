# 使用方式
    1. 至 https://ups.moe.edu.tw/mooc/index.php 進行選課
    2. 執行 autoCourse.exe 並鍵入帳號密碼
    3. 輸入圖形驗證碼
    4. 程式會開啟瀏覽器並跳轉到選課畫面，將實數未滿1hr的課程掛滿1hr
    5. 手動停止程式: CTRL + C
    6. 閱讀時數是以『分鐘』累計，不會馬上更新
    7. 注意: 記得把電腦設定成不自動休眠&關機
    8. 若有異常請提供記錄檔給Roger，記錄檔位置→ D:/autoCourse_logs

# 開發相關
    1. 建立虛擬環境: virtualenv env01
    2. 啟動虛擬環境: .\env01\Scripts\activate
    3. 安裝所需的lib: pip install -r requirement.txt
    4. 安裝PyInstaller: pip install PyInstaller
    5. Build exe: pyinstaller.exe -F .\autoCourse.py

# 坑
    1. E-Course平台有做RWD，若 selenium 開啟的瀏覽器寬度太小 accmulateTime = tdArr[5].text 會選不到

# 參考資料
|Hint|說明|參考|
|:--:|:--:|:--:|
|pip install PyInstaller|安裝PyInstaller||
|pyinstaller.exe -F .\autoCourse.py|打包exe(若報 [WinError 110] 系統無法開啟指定的裝置或檔案，再執行一次此指令會好!)|https://medium.com/pyladies-taiwan/python-%E5%B0%87python%E6%89%93%E5%8C%85%E6%88%90exe%E6%AA%94-32a4bacbe351|
|python3 -m PyInstaller myscript.py| 將PyInstaller當成module執行, 打包exe |https://stackoverflow.com/questions/53798660/pyinstaller-command-not-found|
|pip freeze > ./requirements.txt <br> pip install -r ./requirements.txt|Python PIP 使用 requirements.txt 管理套件相依性|https://blog.longwin.com.tw/2019/03/python-pip-requirements-txt-management-package-2019/|
|Python Log使用|logging套件|https://shengyu7697.github.io/python-logging/|
|不同檔案(module)中使用同一個logger|獨立建立一個base_logger.py|https://stackoverflow.com/questions/15727420/using-logging-in-multiple-modules|
|使用 xpath (XML Path Language) 找尋不限層數子孫element||https://blog.csdn.net/weixin_42159940/article/details/93035008|
|Selenium 之find_element_by_xpath() 基礎用法||https://blog.csdn.net/qq_36652619/article/details/88424463|

# 將exe加入windows defender例外
![Alt text](/imgs/windows%20defender%20例外設定/Image%201.png)
![Alt text](/imgs/windows%20defender%20例外設定/Image%202.png)
![Alt text](/imgs/windows%20defender%20例外設定/Image%203.png)
![Alt text](/imgs/windows%20defender%20例外設定/Image%204.png)

# 關閉電腦休眠
![Alt text](/imgs/關閉電腦休眠/關閉電腦休眠-01.png)
![Alt text](/imgs/關閉電腦休眠/關閉電腦休眠-02.png)
![Alt text](/imgs/關閉電腦休眠/關閉電腦休眠-03.png)
![Alt text](/imgs/關閉電腦休眠/關閉電腦休眠-04.png)
