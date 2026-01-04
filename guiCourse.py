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
        self.root.title("磨課師自動上課助手")
        
        # 視窗置中
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
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
        self.style.configure("Treeview", background="#0f3460", foreground="white", fieldbackground="#0f3460", rowheight=30, font=("Helvetica Neue", 12))
        self.style.configure("Treeview.Heading", background="#16213e", foreground="white", font=("Helvetica Neue", 13, "bold"), relief="flat")
        self.style.map("Treeview", background=[('selected', '#00d4ff')], foreground=[('selected', '#1a1a2e')])
        
        self.browser = None
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
        header = ttk.Label(main_frame, text="🎓 磨課師自動上課助手", style="Header.TLabel")
        header.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, text="自動化課程時數累積工具", style="Sub.TLabel")
        subtitle.pack(pady=(0, 25))

        # 內容容器 (左右分欄)
        content_frame = tk.Frame(main_frame, bg="#1a1a2e")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左側面板 (輸入 + 按鈕 + 日誌) - 固定寬度不延展
        left_panel = tk.Frame(content_frame, bg="#1a1a2e", width=480)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        left_panel.pack_propagate(False) # 固定大小
        
        # 右側面板 (課程清單) - 佔據剩餘空間
        right_panel = tk.Frame(content_frame, bg="#1a1a2e")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- 左側內容開始 ---
        
        # 輸入區域容器 - 使用卡片式設計 (移入 left_panel)
        card_frame = tk.Frame(left_panel, bg="#16213e", highlightbackground="#0f3460", highlightthickness=2)
        card_frame.pack(fill=tk.X, pady=0, ipadx=20, ipady=15)
        
        input_container = tk.Frame(card_frame, bg="#16213e")
        input_container.pack(fill=tk.X, padx=20, pady=10)

        # 帳號
        tk.Label(input_container, text="登入帳號", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.user_entry = tk.Entry(input_container, width=35, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.user_entry.insert(0, "tvbear8068")
        self.user_entry.grid(row=0, column=1, pady=8, padx=(15, 0), sticky=tk.EW, ipady=6)

        # 密碼
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
        
        idx_container = tk.Frame(input_container, bg="#16213e")
        idx_container.grid(row=2, column=1, pady=8, padx=(15, 0), sticky=tk.EW)
        
        self.index_entry = tk.Entry(idx_container, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.index_entry.insert(0, "1")
        self.index_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        tk.Button(idx_container, text="?", font=("Helvetica Neue", 11, "bold"), bg="#16213e", fg="#888888", activebackground="#16213e", activeforeground="white", relief="flat", cursor="hand2", 
                  command=lambda: messagebox.showinfo("說明", "因課程可能有測驗還未做，為避免因測驗沒做程式流程卡住，無法執行其他課程的掛課，此參數為設定要從第幾門課開始掛", icon='info')).pack(side=tk.LEFT, padx=(5, 0))

        # 刷新間隔 (refreshSecs)
        tk.Label(input_container, text="刷新間隔 (分鐘)", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=3, column=0, sticky=tk.W, pady=8)
        
        refresh_container = tk.Frame(input_container, bg="#16213e")
        refresh_container.grid(row=3, column=1, pady=8, padx=(15, 0), sticky=tk.EW)
        
        self.refresh_entry = tk.Entry(refresh_container, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.refresh_entry.insert(0, "10")
        self.refresh_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        tk.Button(refresh_container, text="?", font=("Helvetica Neue", 11, "bold"), bg="#16213e", fg="#888888", activebackground="#16213e", activeforeground="white", relief="flat", cursor="hand2",
                  command=lambda: messagebox.showinfo("說明", "進入課程頁面後，避免「如閒置超過30分鐘，將自動導向首頁，並扣除此30分鐘學習紀錄」，程式會依據所設定的間隔在該課程頁面重整", icon='info')).pack(side=tk.LEFT, padx=(5, 0))

        # 補正時間 (extra mins)
        tk.Label(input_container, text="補正時間 (分鐘)", bg="#16213e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold")).grid(row=4, column=0, sticky=tk.W, pady=8)
        
        extra_container = tk.Frame(input_container, bg="#16213e")
        extra_container.grid(row=4, column=1, pady=8, padx=(15, 0), sticky=tk.EW)
        
        self.extra_mins_entry = tk.Entry(extra_container, font=("Helvetica Neue", 14), bg="#0f3460", fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground="#00d4ff")
        self.extra_mins_entry.insert(0, "5")
        self.extra_mins_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        tk.Button(extra_container, text="?", font=("Helvetica Neue", 11, "bold"), bg="#16213e", fg="#888888", activebackground="#16213e", activeforeground="white", relief="flat", cursor="hand2",
                  command=lambda: messagebox.showinfo("說明", "因操作瀏覽器畫面渲染有延遲時間及 time.sleep 累加，避免累加結果延遲，造成上課時數不足，此欄位用以補足上課時數", icon='info')).pack(side=tk.LEFT, padx=(5, 0))

        input_container.columnconfigure(1, weight=1)

        # 操作按鈕容器
        btn_container = ttk.Frame(left_panel)
        btn_container.pack(fill=tk.X, pady=25)
        
        self.start_btn = ttk.Button(btn_container, text="🚀 開始自動上課", style="Start.TButton", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8), ipady=8)
        
        self.pause_btn = ttk.Button(btn_container, text="⏸ 暫停", style="Pause.TButton", command=self.toggle_pause, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0), ipady=8)

        # 日誌區域
        log_label = tk.Label(left_panel, text="📋 執行日誌", bg="#1a1a2e", fg="#00d4ff", font=("Helvetica Neue", 14, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_area = scrolledtext.ScrolledText(left_panel, height=12, font=("JetBrains Mono", 12), 
                                                   bg="#0f3460", fg="#e8e8e8", insertbackground="white",
                                                   relief="flat", state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # --- 右側內容開始 ---

        # 課程清單視窗 (Treeview)
        # 課程清單視窗 (Treeview)
        # 使用 frame 來包裝標題和總選修時數
        tree_header_frame = tk.Frame(right_panel, bg="#1a1a2e")
        tree_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(tree_header_frame, text="📚 已選課程清單", bg="#1a1a2e", fg="white", font=("Helvetica Neue", 14, "bold")).pack(side=tk.LEFT)
        
        self.total_hours_label = tk.Label(tree_header_frame, text="(總選修時數: 0 小時)", bg="#1a1a2e", fg="#00d4ff", font=("Helvetica Neue", 12))
        self.total_hours_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Treeview 容器 (包含 Scrollbar)
        tree_frame = tk.Frame(right_panel, bg="#1a1a2e")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("page", "idx", "name", "hours")
        self.course_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")
        
        self.course_tree.heading("page", text="頁碼")
        self.course_tree.column("page", width=50, minwidth=40, anchor="center")
        
        self.course_tree.heading("idx", text="#")
        self.course_tree.column("idx", width=50, minwidth=40, anchor="center")
        
        self.course_tree.heading("name", text="課程名稱")
        self.course_tree.column("name", width=300, minwidth=200, anchor="w", stretch=True)
        
        self.course_tree.heading("hours", text="時數")
        self.course_tree.column("hours", width=80, minwidth=60, anchor="center")
        
        # 加上 Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_logging(self):
        # 建立一個自定義 Handler，將所有 logger 輸出轉發至 UI
        ui_instance = self
        
        class UILogHandler(logging.Handler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    # 直接呼叫底層 UI 更新方法，避免遞迴呼叫 logger
                    ui_instance._append_to_ui(msg)
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
        """
        記錄日誌並顯示於 UI。
        此方法會透過 logger.info 記錄，進而觸發 UILogHandler 更新 UI。
        """
        logger.info(message)

    def _append_to_ui(self, message):
        """僅將訊息追加到 UI 元件 (由 UILogHandler 呼叫)"""
        def update():
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message + '\n')
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
            self.log_area.update_idletasks()
        
        self.root.after(0, update)

    def start_automation(self):
        if self.is_running:
            return
        
        username = self.user_entry.get()
        password = self.pass_entry.get()
        start_index = self.index_entry.get()
        refresh_mins = self.refresh_entry.get()
        extra_mins_str = self.extra_mins_entry.get()
        
        if not username or not password:
            messagebox.showwarning("警告", "請輸入帳號與密碼")
            return
        
        # 驗證刷新間隔與補正分鐘為數字
        try:
            refresh_secs = int(refresh_mins) * 60
            extra_mins_val = int(extra_mins_str) if extra_mins_str else 0
        except ValueError:
            messagebox.showwarning("警告", "刷新間隔與補正分鐘必須為數字")
            return

        self.is_running = True
        self.is_paused = False
        self.start_btn.configure(state='disabled', text="⏳ 執行中...")
        self.pause_btn.configure(state='normal', text="⏸ 暫停", style="Pause.TButton")
        self.log_to_ui("系統啟動中...")
        
        # 在新執行緒中運行腳本
        threading.Thread(target=self.run_logic, args=(username, password, start_index, refresh_secs, extra_mins_val), daemon=True).start()

    def run_logic(self, username, password, start_index, refresh_secs, extra_mins):
        try:
            acctUsername = username
            acctPassword = base64.b64encode(password.encode("UTF-8"))
            startCourseIndex = start_index
            self.refresh_secs = refresh_secs
            self.extra_mins = extra_mins

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
            time.sleep(2)
            
            # 1. 爬取所有分頁課程
            self.log_to_ui("正在掃描所有分頁課程...")
            all_courses = self.collect_all_courses()
            self.log_to_ui(f"掃描完成！共找到 {len(all_courses)} 堂課程。")
            
            if not all_courses:
                 self.log_to_ui("[錯誤] 未找到任何課程，請確認是否已選課。")
                 return

            # 過濾起始課程
            start_num = int(startCourseIndex)
            target_courses = [c for c in all_courses if c['global_idx'] >= start_num]
            
            self.log_to_ui(f"準備上課 - 從第 {start_num} 堂開始，共需執行 {len(target_courses)} 堂")
            
            # 重要：掃描結束後，瀏覽器停在最後一頁。必須重置回第一頁，因為 go_to_page 假設從第一頁開始。
            self.log_to_ui("重置頁面狀態，在「我修的課」頁面「重新整理」後，再篩選「進行中」課程...")
            self.browser.refresh()
            time.sleep(2)
            gotoChoosedCourseAndFilter(self.browser)
            time.sleep(2)

            # 2. 依序執行課程
            for i, course in enumerate(target_courses):
                if not self.is_running: 
                    self.log_to_ui("使用者已要求停止執行。")
                    break
                
                # 重新導航到正確頁面
                # 因為每次 attendToCourse 結束或重新開始，頁面狀態可能重置
                # 我們需要確保在點擊課程前，位於正確的分頁
                if not self.go_to_page(course['page']):
                   self.log_to_ui(f"[錯誤] 無法跳轉到第 {course['page']} 頁，跳過課程：{course['name']}")
                   continue
                
                self.log_to_ui(f"▶ 開始課程 [{course['global_idx']}/{len(all_courses)}]：{course['name']}")
                
                # 計算所需秒數
                # 計算所需秒數
                raw_hours = course.get("hours", "0")
                digits_only = "".join(filter(str.isdigit, str(raw_hours)))
                cert_hours = int(digits_only) if digits_only else 0
                
                extra_secs = self.extra_mins * 60
                target_secs = (cert_hours * 60 * 60) + extra_secs
                
                self.log_to_ui(f"   認證時數：{cert_hours} 小時，補正：{self.extra_mins} 分鐘，目標累計：{target_secs} 秒")
                
                # 呼叫 attendToCourse (注意：這裡傳入的是當前頁面的 row_idx)
                attendToCourse(self.browser, course['row_idx'], {'courseName': course['name']}, 
                               refreshSecs=self.refresh_secs, neededSecs=target_secs, 
                               pause_check=lambda: self.is_paused)
                
                if not self.is_running: break
                self.log_to_ui(f"✓ 課程『{course['name']}』完成！回到課程列表...")
                
                # 回到課程列表首頁
                gotoChoosedCourseAndFilter(self.browser)
                time.sleep(2)

            self.log_to_ui("🎉 所有課程上課完成！")
            messagebox.showinfo("完成", "所有課程上課完成！")

        except Exception as e:
            logger.error(f"執行出錯: {str(e)}", exc_info=True)
            self.log_to_ui(f"[錯誤] 執行出錯，詳情請查看日誌檔案: {str(e)}")
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

    def collect_all_courses(self):
        """爬取所有分頁的課程資訊"""
        all_courses = []
        page_num = 1
        global_idx = 1
        total_cert_hours = 0
        
        # 重置總時數顯示
        self.total_hours_label.configure(text="(總選修時數: 0 小時)")
        
        while True:
            if not self.is_running: break
            
            # 等待表格載入
            time.sleep(2)
            
            # 抓取當前頁面課程
            courseTrList = self.browser.execute_script('return document.querySelectorAll(".table__accordion-head");')
            
            if len(courseTrList) == 0:
                break
                
            for row_idx, tr in enumerate(courseTrList):
                try:
                    text_parts = tr.text.split("\n")
                    # 假設格式：[0]狀態, [1]名稱, [2]時數
                    c_name = text_parts[1] if len(text_parts) > 1 else "Unknown"
                    c_hours = text_parts[2] if len(text_parts) > 2 else "0"
                    
                    course_data = {
                        'page': page_num,
                        'row_idx': row_idx,
                        'global_idx': global_idx,
                        'name': c_name,
                        'hours': c_hours
                    }
                    all_courses.append(course_data)
                    
                    # 累計時數
                    digits_only = "".join(filter(str.isdigit, str(c_hours)))
                    if digits_only:
                        total_cert_hours += int(digits_only)
                    
                    # 更新 UI Treeview 與總時數
                    self.course_tree.insert("", "end", values=(page_num, global_idx, c_name, c_hours))
                    self.course_tree.yview_moveto(1) # 自動捲動到底部
                    self.total_hours_label.configure(text=f"(總選修時數: {total_cert_hours} 小時)")
                    
                    global_idx += 1
                except Exception as e:
                    self.log_to_ui(f"[警告] 解析課程資料失敗: {str(e)}")

            # 檢查下一頁
            try:
                # 檢查 Next 按鈕是否禁用
                next_btn_disabled_count = self.browser.execute_script(
                    'return document.querySelectorAll("button.mat-paginator-navigation-next[disabled]").length;')
                
                # 注意：MatPaginator 的 disabled 屬性有時是透過 class 'mat-button-disabled' 或屬性 'disabled'
                # 這裡檢查 disabled 屬性
                if next_btn_disabled_count > 0:
                    self.log_to_ui("已到達最後一頁。")
                    break
                
                # 嘗試點擊下一頁
                next_btns = self.browser.find_elements(By.CSS_SELECTOR, "button.mat-paginator-navigation-next")
                if next_btns:
                    next_btn = next_btns[0]
                    # 再次確認 class 是否包含 disabled 樣式
                    if "mat-button-disabled" in next_btn.get_attribute("class"):
                         self.log_to_ui("已到達最後一頁 (Disabled Class)。")
                         break
                         
                    self.log_to_ui(f"前往第 {page_num + 1} 頁...")
                    next_btn.click()
                    page_num += 1
                    time.sleep(1) # 等待切換
                else:
                    break
            except Exception as e:
                self.log_to_ui(f"[訊息] 無法搜尋下一頁 ({str(e)})，停止掃描。")
                break
                
        return all_courses

    def go_to_page(self, target_page):
        """跳轉到指定分頁"""
        try:
            # 簡單實作：目前我們都在第1頁 (因為每次都回到 filters)，所以需要點擊 Next (target_page - 1) 次
            # 改進：檢查當前頁碼比較好，但這裡先假設每次都從頭開始
            current_page = 1
            
            if target_page == 1:
                return True
                
            for _ in range(target_page - 1):
                if not self.is_running: return False
                
                next_btns = self.browser.find_elements(By.CSS_SELECTOR, "button.mat-paginator-navigation-next")
                if next_btns:
                    next_btns[0].click()
                    time.sleep(0.5)
                else:
                    return False
            
            time.sleep(1)
            return True
        except Exception as e:
            self.log_to_ui(f"[錯誤] 分頁導航失敗: {str(e)}")
            return False

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
