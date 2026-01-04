# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import base64
import time
import logging
import queue
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

class AppHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)

class CourseAutomationUI:
    def __init__(self, root):
        self.root = root
        self.root.title("磨課師上課助手")
        self.root.geometry("700x800")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 現代深色主題樣式
        self.style.configure("TFrame", background="#1a1a2e")
        self.style.configure("TLabel", background="#1a1a2e", foreground="#e8e8e8", font=("Helvetica Neue", 14))
        self.style.configure("Header.TLabel", font=("Helvetica Neue", 22, "bold"), foreground="#00d4ff", background="#1a1a2e")
        self.style.configure("Sub.TLabel", font=("Helvetica Neue", 11), foreground="#888888", background="#1a1a2e")
        self.style.configure("TEntry", font=("Helvetica Neue", 14), padding=8)
        self.style.configure("TButton", font=("Helvetica Neue", 14, "bold"), padding=12)
        
        # 開始按鈕樣式 - 青色
        self.style.configure("Start.TButton", background="#00d4ff", foreground="#1a1a2e", font=("Helvetica Neue", 15, "bold"))
        self.style.map("Start.TButton", background=[('active', '#00b8e6'), ('disabled', '#555555')])
        
        # 暫停按鈕樣式 - 灰色
        self.style.configure("Pause.TButton", background="#4a4a5a", foreground="#e8e8e8", font=("Helvetica Neue", 15, "bold"))
        self.style.map("Pause.TButton", background=[('active', '#5a5a6a'), ('disabled', '#3a3a4a')])
        
        # 繼續按鈕樣式 - 綠色
        self.style.configure("Continue.TButton", background="#2ecc71", foreground="white", font=("Helvetica Neue", 15, "bold"))
        self.style.map("Continue.TButton", background=[('active', '#27ae60')])
        
        self.browser = None
        self.is_running = False
        self.is_running = False
        self.is_paused = False
        self.show_password = False
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        # 主容器
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 標題區域
        header = ttk.Label(main_frame, text="🎓 edu 磨課師 + 自動掛機助手", style="Header.TLabel")
        header.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, text="自動化課程時數累積工具", style="Sub.TLabel")
        subtitle.pack(pady=(0, 25))

        # 輸入區域容器 - 使用卡片式設計
        card_frame = tk.Frame(main_frame, bg="#16213e", highlightbackground="#0f3460", highlightthickness=2)
        card_frame.pack(fill=tk.X, pady=10, ipadx=20, ipady=15)
        
        input_container = tk.Frame(card_frame, bg="#16213e")
        input_container.pack(fill=tk.X, padx=20, pady=10)

        # 帳號
        tk.Label(input_container, text="登入帳號", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.user_entry = tk.Entry(input_container, width=35, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.user_entry.insert(0, "tvbear8068")
        self.user_entry.grid(row=0, column=1, pady=8, padx=(15, 0), sticky=tk.EW, ipady=6)

        # 密碼
        # 密碼區域 (包含 Entry 和 按鈕的容器)
        tk.Label(input_container, text="登入密碼", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=1, column=0, sticky=tk.W, pady=8)
        
        pwd_container = tk.Frame(input_container, bg="#16213e")
        pwd_container.grid(row=1, column=1, pady=8, padx=(15, 0), sticky=tk.EW)
        
        self.pass_entry = tk.Entry(pwd_container, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", show="●", highlightthickness=1, highlightbackground="#00d4ff")
        self.pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.pass_entry.insert(0, "Jullie20090824")
        
        self.eye_btn = tk.Button(pwd_container, text="🔓", font=("Helvetica Neue", 12), bg="#16213e", fg="#00d4ff", 
                                 activebackground="#16213e", activeforeground="#00b8e6",
                                 relief="flat", cursor="hand2", command=self.toggle_password_visibility)
        self.eye_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 課程索引
        tk.Label(input_container, text="起始課程索引", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.index_entry = tk.Entry(input_container, width=35, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.index_entry.insert(0, "1")
        self.index_entry.grid(row=2, column=1, pady=8, padx=(15, 0), sticky=tk.EW, ipady=6)

        # 刷新間隔 (refreshSecs)
        tk.Label(input_container, text="刷新間隔 (分鐘)", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.refresh_entry = tk.Entry(input_container, width=35, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.refresh_entry.insert(0, "10")
        self.refresh_entry.grid(row=3, column=1, pady=8, padx=(15, 0), sticky=tk.EW, ipady=6)

        input_container.columnconfigure(1, weight=1)

        # 操作按鈕容器
        btn_container = ttk.Frame(main_frame)
        btn_container.pack(fill=tk.X, pady=25)
        
        self.start_btn = ttk.Button(btn_container, text="🚀 開始自動掛機", style="Start.TButton", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8), ipady=8)
        
        self.pause_btn = ttk.Button(btn_container, text="⏸ 暫停", style="Pause.TButton", command=self.toggle_pause, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0), ipady=8)

        # 日誌區域
        log_label = tk.Label(main_frame, text="📋 執行日誌", bg="#1a1a2e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_area = scrolledtext.ScrolledText(main_frame, height=12, font=("JetBrains Mono", 12), 
                                                   bg="#0f3460", fg="#e8e8e8", insertbackground="white",
                                                   relief="flat", state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

    def setup_logging(self):
        # 建立一個自定義 Handler，將所有 logger 輸出轉發至 UI
        ui_instance = self
        
        class UILogHandler(logging.Handler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    ui_instance.log_to_ui(msg)
                except Exception:
                    pass
        
        handler = UILogHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S'))
        handler.setLevel(logging.INFO)
        
        # 加入到 root logger，這樣所有模組的日誌都會被捕捉
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        self.log_to_ui("系統已就緒，請點擊「開始上課」...")
    
    def log_to_ui(self, message):
        """即時將訊息打印到 UI 日誌區域"""
        def update():
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message + '\n')
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
            self.log_area.update_idletasks()  # 強制立即刷新 UI
        
        # 使用 after 確保在主線程執行
        self.root.after(0, update)

    def start_automation(self):
        if self.is_running:
            return
        
        username = self.user_entry.get()
        password = self.pass_entry.get()
        start_index = self.index_entry.get()
        refresh_mins = self.refresh_entry.get()
        
        if not username or not password:
            messagebox.showwarning("警告", "請輸入帳號與密碼")
            return
        
        # 驗證刷新間隔為數字
        try:
            refresh_secs = int(refresh_mins) * 60
        except ValueError:
            messagebox.showwarning("警告", "刷新間隔必須為數字")
            return

        self.is_running = True
        self.is_paused = False
        self.start_btn.configure(state='disabled', text="運行中...")
        self.pause_btn.configure(state='normal')
        
        # 在新執行緒中運行腳本
        threading.Thread(target=self.run_logic, args=(username, password, start_index, refresh_secs), daemon=True).start()

    def run_logic(self, username, password, start_index, refresh_secs):
        try:
            acctUsername = username
            acctPassword = base64.b64encode(password.encode("UTF-8"))
            startCourseIndex = start_index
            self.refresh_secs = refresh_secs

            self.log_to_ui("正在啟動 Chrome 瀏覽器...")
            options = Options()
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=options)
            self.browser.get("https://moocs.moe.edu.tw/moocs/#/home")
            self.browser.maximize_window()
            self.log_to_ui("瀏覽器已啟動，正在開啟磨課師首頁...")

            # 彈出視窗檢查
            if check_exists_by_xpath(self.browser, "//div[@id='uploadHourModal']/descendant::button[@class='close']"):
                self.log_to_ui("關閉公告彈窗")
                closeDialogBtn = self.browser.find_element(By.ID, "uploadHourModal").find_element(By.CLASS_NAME, "close")
                closeDialogBtn.click()

            time.sleep(2)
            self.browser.find_element(By.CLASS_NAME, 'action__button-text').click()
            time.sleep(1)

            # 教育雲登入
            self.log_to_ui("正在導航至教育雲登入頁面...")
            self.browser.find_element(By.CSS_SELECTOR, ".login-link__guide-title").click()
            time.sleep(2)

            # 填寫帳密
            try:
                self.log_to_ui("正在填入帳號密碼...")
                wait = WebDriverWait(self.browser, 10)
                user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='請輸入帳號']")))
                self.browser.execute_script(f'arguments[0].value="{acctUsername}";', user_input)
                
                # 同樣等待密碼框
                pwd_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='請輸入密碼']")))
                self.browser.execute_script(f'arguments[0].value="{base64.b64decode(acctPassword).decode("UTF-8")}";', pwd_input)
                self.log_to_ui("帳密已填入，請在網頁上輸入圖形驗證碼...")
            except TimeoutException:
                self.log_to_ui("[錯誤] 找不到帳密輸入框，請確認是否已進入正確的登入頁面")
                raise

            # 驗證碼等待
            total_wait = 20
            for i in range(total_wait, 0, -1):
                if not self.browser.find_elements(By.ID, "id15"):
                    self.log_to_ui("偵測到登入完成，繼續執行...")
                    break
                try:
                    self.browser.execute_script(f'''
                        var btn = document.getElementById("id15");
                        if (btn) {{
                            btn.innerText = "登入 (倒數 " + {i} + "s)";
                            btn.style.border = "3px solid red";
                        }}
                    ''')
                except: pass
                time.sleep(1)

            try:
                if self.browser.find_elements(By.ID, "id15"):
                    self.browser.find_element(By.ID, "id15").click()
            except: pass

            self.log_to_ui("正在跳轉到【我修的課】...")
            gotoChoosedCourseAndFilter(self.browser)
            time.sleep(1)
            courseTrList = self.browser.execute_script('return document.querySelectorAll(".table__accordion-head");')

            courseList = [
                {
                    "courseName": tr.text.split("\n")[1], 
                    "certHours": tr.text.split("\n")[2]
                } for tr in courseTrList]

            courseList = courseList[(int(startCourseIndex)-1):]
            self.log_to_ui(f"準備掛機 - 共 {len(courseList)} 堂課程")

            for idx, courseInfo in enumerate(courseList):
                if not self.is_running: 
                    self.log_to_ui("使用者已要求停止執行。")
                    break
                
                course_name = courseInfo.get('courseName')
                self.log_to_ui(f"▶ 開始課程 [{idx+1}/{len(courseList)}]：{course_name}")
                
                # 處理認證時數（只取出數字）
                raw_hours = courseInfo.get("certHours", "0")
                digits_only = "".join(filter(str.isdigit, str(raw_hours)))
                cert_hours = int(digits_only) if digits_only else 0
                
                # 計算所需秒數
                target_secs = (cert_hours * 60 * 60) + (5 * 60) # 多加 5 分鐘
                self.log_to_ui(f"   認證時數：{cert_hours} 小時，目標累計：{target_secs} 秒")
                
                attendToCourse(self.browser, idx + (int(startCourseIndex)-1), courseInfo, refreshSecs=self.refresh_secs, neededSecs=target_secs, pause_check=lambda: self.is_paused)
                
                if not self.is_running: break
                self.log_to_ui(f"✓ 課程『{course_name}』完成！回到課程列表...")
                gotoChoosedCourseAndFilter(self.browser)

            self.log_to_ui("🎉 所有課程掛機完成！")
            messagebox.showinfo("完成", "所有課程掛機完成！")

        except Exception as e:
            self.log_to_ui(f"[錯誤] 執行出錯: {str(e)}")
            messagebox.showerror("錯誤", f"發生錯誤: {str(e)}")
        finally:
            self.is_running = False
            self.is_paused = False
            self.start_btn.configure(state='normal', text="🚀 開始上課")
            self.pause_btn.configure(state='disabled', text="⏸ 暫停", style="Pause.TButton")
            if self.browser:
                try: self.browser.quit()
                except: pass

    def toggle_pause(self):
        """切換暫停/繼續狀態"""
        if self.is_paused:
            # 繼續執行 - 切回灰色暫停按鈕
            self.is_paused = False
            self.pause_btn.configure(text="⏸ 暫停", style="Pause.TButton")
            self.log_to_ui("▶ 已繼續執行...")
        else:
            # 暫停 - 切換為綠色繼續按鈕
            self.is_paused = True
            self.pause_btn.configure(text="▶ 繼續", style="Continue.TButton")
            self.log_to_ui("⏸ 已暫停，點擊「繼續」恢復執行...")

    def toggle_password_visibility(self):
        """切換密碼顯示狀態"""
        if self.show_password:
            self.pass_entry.configure(show="●")
            self.eye_btn.configure(text="🔓")
            self.show_password = False
        else:
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="🔐")
            self.show_password = True

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseAutomationUI(root)
    root.mainloop()
