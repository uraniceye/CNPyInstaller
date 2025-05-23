import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import queue
import sys
import shlex # 用于更安全地处理命令行参数（虽然此示例中直接构建列表）
import traceback

# --- 全局常量 ---
PYINSTALLER_CMD = "pyinstaller" # 或者指定完整路径，例如 sys.executable -m PyInstaller

# --- 帮助文本/提示信息 (部分更新/新增) ---
HELP_TEXTS = {
    "main": "欢迎使用中文 PyInstaller 图形工具！\n请填写以下选项并开始打包您的 Python 应用程序。",
    "script_path": "选择您要打包的主 Python 脚本 (.py 文件)。",
    "app_name": "打包后应用程序的名称 (例如: 我的应用)。",
    "one_file": "将所有内容打包成一个单独的可执行文件。启动可能稍慢。",
    "one_dir": "打包成一个包含可执行文件和所有依赖的文件夹。启动较快。",
    "windowed": "适用于 GUI 应用程序，运行时不显示黑色控制台窗口。",
    "console": "适用于命令行/控制台应用程序。",
    "icon_path": "(可选) 为您的应用程序选择一个图标文件 (.ico 适用于 Windows, .icns 适用于 macOS)。",
    "output_dir": "(可选) 指定打包后文件输出的目录。默认为脚本所在目录下的 'dist' 文件夹。",
    # 高级选项卡
    "hidden_imports": "(高级) 如果 PyInstaller 未能自动检测到某些模块，请在此处手动添加，每行一个模块名 (例如: my_hidden_module)。",
    "additional_files_tab": "(高级) 管理需要捆绑到应用程序中的额外数据文件或文件夹。",
    "clean_build": "(高级) 在打包前清理 PyInstaller 的缓存和临时文件 (build/ 和 *.spec)。",
    "noconfirm_overwrite": "(高级) 如果输出目录已存在，直接覆盖而不进行确认 (PyInstaller默认行为)。",
    "upx_dir": "(高级, 可选) 指定 UPX 工具所在的文件夹路径，用于压缩可执行文件。",
    "runtime_tmpdir": "(高级, 仅限单文件模式) 指定程序运行时文件解压到的临时目录路径。",
    "exclude_modules": "(高级) 需要从打包中排除的模块，每行一个 (例如: tkinter.test)。",
}


class PyInstallerGUI_CN_Advanced:
    def __init__(self, root):
        self.root = root
        self.root.title("中文 PyInstaller 打包工具 v1.1 (高级版)")
        self.root.geometry("850x750") # 调整窗口大小

        # --- Tkinter 变量 ---
        self.script_path_var = tk.StringVar()
        self.app_name_var = tk.StringVar()
        self.package_mode_var = tk.StringVar(value="onefile")
        self.app_type_var = tk.StringVar(value="windowed")
        self.icon_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()

        # 高级选项变量
        self.clean_build_var = tk.BooleanVar(value=True) # 默认清理
        self.noconfirm_var = tk.BooleanVar(value=True)   # 默认不确认
        self.upx_dir_var = tk.StringVar()
        self.runtime_tmpdir_var = tk.StringVar()
        # self.hidden_imports_var # 将使用Text控件
        # self.exclude_modules_var # 将使用Text控件
        self.additional_files_list = [] # 存储附加文件 {src: ..., dst: ...} 字典

        # --- 进程通信队列 ---
        self.log_queue = queue.Queue()
        self.gui_state_queue = queue.Queue() # 用于线程安全地更新GUI状态

        # --- 创建主界面 ---
        self.create_widgets()
        self.check_pyinstaller_installed()

        # --- 启动队列处理 ---
        self.root.after(100, self.process_ui_queues)


    def check_pyinstaller_installed(self):
        try:
            process = subprocess.Popen([PYINSTALLER_CMD, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            stdout, stderr = process.communicate(timeout=5)
            if process.returncode == 0 and stdout:
                self.log_message(f"PyInstaller 版本: {stdout.strip()}", "info")
            else:
                self.log_message("警告: 未能成功获取 PyInstaller 版本。请确保已正确安装并配置到系统路径。", "warning")
                messagebox.showwarning("PyInstaller 未找到", "可能未安装 PyInstaller，或者其未被添加到系统环境变量 (PATH) 中。\n请先安装 PyInstaller: pip install pyinstaller", parent=self.root)
        except FileNotFoundError:
            self.log_message("错误: PyInstaller 命令未找到。请确保已安装并配置到系统路径。", "error")
            messagebox.showerror("PyInstaller 未找到", "未找到 PyInstaller 命令。\n请确保您已经通过 'pip install pyinstaller' 安装了它，并且它在系统的 PATH 环境变量中。", parent=self.root)
        except subprocess.TimeoutExpired:
            self.log_message("警告: 检查 PyInstaller 版本超时。", "warning")
        except Exception as e:
            self.log_message(f"检查 PyInstaller 时发生错误: {e}", "error")


    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 帮助信息 ---
        help_label = ttk.Label(main_frame, text=HELP_TEXTS["main"], wraplength=800, justify=tk.LEFT)
        help_label.pack(pady=(0, 10), anchor="w")

        # --- 创建标签页控件 ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- 标签页1: 基本选项 ---
        basic_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_tab, text='基本选项')
        self.create_basic_options_tab(basic_tab)

        # --- 标签页2: 高级选项 ---
        advanced_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_tab, text='高级选项')
        self.create_advanced_options_tab(advanced_tab)

        # --- 标签页3: 附加文件 ---
        files_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(files_tab, text='附加文件')
        self.create_additional_files_tab(files_tab)


        # --- 操作按钮区 ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        self.package_button = ttk.Button(action_frame, text="开始打包", command=self._start_packaging_thread, style="Accent.TButton", width=15)
        self.package_button.pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="清空选项", command=self._clear_options, width=12).pack(side=tk.RIGHT, padx=5)


        # --- 日志输出区 ---
        log_frame = ttk.LabelFrame(main_frame, text="打包日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("cmd", foreground="#555555", font=("Consolas", 9) if "Consolas" in tk.font.families() else ("Courier", 9))


        # --- 样式配置 ---
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure("Accent.TButton", font=("黑体", 10, "bold"), foreground="white", background="#0078D7")
        style.map("Accent.TButton", background=[('active', '#005A9E'), ('disabled', '#A0A0A0')])
        style.configure("Small.TButton", font=("宋体", 8))


    def create_basic_options_tab(self, tab_frame):
        options_frame = ttk.Frame(tab_frame) # 使用普通Frame以便更好地控制布局
        options_frame.pack(fill=tk.X)
        options_frame.columnconfigure(1, weight=1)

        # 1. Python 脚本路径
        ttk.Label(options_frame, text="Python 脚本:").grid(row=0, column=0, sticky=tk.W, pady=3, padx=(0,5))
        script_entry = ttk.Entry(options_frame, textvariable=self.script_path_var, width=65)
        script_entry.grid(row=0, column=1, sticky=tk.EW, pady=3)
        ttk.Button(options_frame, text="浏览...", command=self._browse_script, style="Small.TButton").grid(row=0, column=2, padx=5, pady=3)
        self.add_tooltip(script_entry, HELP_TEXTS["script_path"])

        # 2. 应用程序名称
        ttk.Label(options_frame, text="应用名称:").grid(row=1, column=0, sticky=tk.W, pady=3, padx=(0,5))
        app_name_entry = ttk.Entry(options_frame, textvariable=self.app_name_var, width=65)
        app_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=3)
        self.add_tooltip(app_name_entry, HELP_TEXTS["app_name"])

        # 3. 打包模式
        ttk.Label(options_frame, text="打包模式:").grid(row=2, column=0, sticky=tk.W, pady=3, padx=(0,5))
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        onefile_rb = ttk.Radiobutton(mode_frame, text="单文件 (--onefile)", variable=self.package_mode_var, value="onefile")
        onefile_rb.pack(side=tk.LEFT, padx=(0,15))
        onedir_rb = ttk.Radiobutton(mode_frame, text="文件夹 (--onedir)", variable=self.package_mode_var, value="onedir")
        onedir_rb.pack(side=tk.LEFT)
        self.add_tooltip(onefile_rb, HELP_TEXTS["one_file"])
        self.add_tooltip(onedir_rb, HELP_TEXTS["one_dir"])

        # 4. 应用类型
        ttk.Label(options_frame, text="应用类型:").grid(row=3, column=0, sticky=tk.W, pady=3, padx=(0,5))
        type_frame = ttk.Frame(options_frame)
        type_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W)
        windowed_rb = ttk.Radiobutton(type_frame, text="窗口应用 (--windowed)", variable=self.app_type_var, value="windowed")
        windowed_rb.pack(side=tk.LEFT, padx=(0,15))
        console_rb = ttk.Radiobutton(type_frame, text="控制台应用 (--console)", variable=self.app_type_var, value="console")
        console_rb.pack(side=tk.LEFT)
        self.add_tooltip(windowed_rb, HELP_TEXTS["windowed"])
        self.add_tooltip(console_rb, HELP_TEXTS["console"])

        # 5. 图标路径
        ttk.Label(options_frame, text="图标文件:").grid(row=4, column=0, sticky=tk.W, pady=3, padx=(0,5))
        icon_entry = ttk.Entry(options_frame, textvariable=self.icon_path_var, width=65)
        icon_entry.grid(row=4, column=1, sticky=tk.EW, pady=3)
        ttk.Button(options_frame, text="浏览...", command=self._browse_icon, style="Small.TButton").grid(row=4, column=2, padx=5, pady=3)
        self.add_tooltip(icon_entry, HELP_TEXTS["icon_path"])

        # 6. 输出目录
        ttk.Label(options_frame, text="输出目录:").grid(row=5, column=0, sticky=tk.W, pady=3, padx=(0,5))
        output_dir_entry = ttk.Entry(options_frame, textvariable=self.output_dir_var, width=65)
        output_dir_entry.grid(row=5, column=1, sticky=tk.EW, pady=3)
        ttk.Button(options_frame, text="浏览...", command=self._browse_output_dir, style="Small.TButton").grid(row=5, column=2, padx=5, pady=3)
        self.add_tooltip(output_dir_entry, HELP_TEXTS["output_dir"])


    def create_advanced_options_tab(self, tab_frame):
        adv_frame = ttk.Frame(tab_frame)
        adv_frame.pack(fill=tk.X)
        adv_frame.columnconfigure(1, weight=1) # 让Entry和Text可伸展

        # 1. 隐藏导入
        ttk.Label(adv_frame, text="隐藏导入\n(每行一个):").grid(row=0, column=0, sticky=tk.NW, pady=3, padx=(0,5))
        self.hidden_imports_text = scrolledtext.ScrolledText(adv_frame, height=4, width=60, wrap=tk.WORD)
        self.hidden_imports_text.grid(row=0, column=1, sticky=tk.EW, pady=3)
        self.add_tooltip(self.hidden_imports_text, HELP_TEXTS["hidden_imports"])

        # 2. 排除模块
        ttk.Label(adv_frame, text="排除模块\n(每行一个):").grid(row=1, column=0, sticky=tk.NW, pady=3, padx=(0,5))
        self.exclude_modules_text = scrolledtext.ScrolledText(adv_frame, height=4, width=60, wrap=tk.WORD)
        self.exclude_modules_text.grid(row=1, column=1, sticky=tk.EW, pady=3)
        self.add_tooltip(self.exclude_modules_text, HELP_TEXTS["exclude_modules"])

        # 3. 清理构建
        clean_check = ttk.Checkbutton(adv_frame, text="打包前清理 (--clean)", variable=self.clean_build_var)
        clean_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.add_tooltip(clean_check, HELP_TEXTS["clean_build"])

        # 4. 覆盖时不确认 (PyInstaller默认就是不确认，但可以作为选项给用户)
        # noconfirm_check = ttk.Checkbutton(adv_frame, text="覆盖时不确认 (--noconfirm)", variable=self.noconfirm_var)
        # noconfirm_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        # self.add_tooltip(noconfirm_check, HELP_TEXTS["noconfirm_overwrite"])

        # 5. UPX 目录
        ttk.Label(adv_frame, text="UPX 目录:").grid(row=4, column=0, sticky=tk.W, pady=3, padx=(0,5))
        upx_entry = ttk.Entry(adv_frame, textvariable=self.upx_dir_var, width=60)
        upx_entry.grid(row=4, column=1, sticky=tk.EW, pady=3)
        ttk.Button(adv_frame, text="浏览...", command=lambda: self._browse_generic_dir(self.upx_dir_var, "选择 UPX 工具目录"), style="Small.TButton").grid(row=4, column=2, padx=5, pady=3)
        self.add_tooltip(upx_entry, HELP_TEXTS["upx_dir"])

        # 6. 运行时临时目录
        ttk.Label(adv_frame, text="运行时临时目录\n(--runtime-tmpdir):").grid(row=5, column=0, sticky=tk.W, pady=3, padx=(0,5))
        runtime_tmpdir_entry = ttk.Entry(adv_frame, textvariable=self.runtime_tmpdir_var, width=60)
        runtime_tmpdir_entry.grid(row=5, column=1, sticky=tk.EW, pady=3)
        ttk.Button(adv_frame, text="浏览...", command=lambda: self._browse_generic_dir(self.runtime_tmpdir_var, "选择运行时临时目录"), style="Small.TButton").grid(row=5, column=2, padx=5, pady=3)
        self.add_tooltip(runtime_tmpdir_entry, HELP_TEXTS["runtime_tmpdir"])


    def create_additional_files_tab(self, tab_frame):
        files_outer_frame = ttk.Frame(tab_frame)
        files_outer_frame.pack(fill=tk.BOTH, expand=True)

        # --- 文件/文件夹列表区 ---
        list_frame = ttk.LabelFrame(files_outer_frame, text="已添加文件/文件夹列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        self.additional_files_listbox = tk.Listbox(list_frame, height=8, selectmode=tk.SINGLE)
        list_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.additional_files_listbox.yview)
        list_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.additional_files_listbox.xview)
        self.additional_files_listbox.config(yscrollcommand=list_scrollbar_y.set, xscrollcommand=list_scrollbar_x.set)

        list_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        list_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.additional_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.add_tooltip(self.additional_files_listbox, "显示已添加的附加文件/文件夹。\n源路径 -> 目标路径 (在包内, '.' 表示根目录)")

        # --- 操作按钮区 ---
        buttons_frame = ttk.Frame(files_outer_frame, padding=(0, 5))
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="添加文件...", command=self._add_file_to_list, style="Small.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="添加文件夹...", command=self._add_folder_to_list, style="Small.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="移除选中", command=self._remove_selected_file, style="Small.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="清空列表", command=self._clear_files_list, style="Small.TButton").pack(side=tk.LEFT, padx=2)

    def _add_file_to_list(self):
        filepath = filedialog.askopenfilename(title="选择要添加的文件", parent=self.root)
        if filepath:
            dst_path = self._ask_destination_path(os.path.basename(filepath))
            if dst_path is not None: # 用户没有取消输入目标路径
                self.additional_files_list.append({"src": filepath, "dst": dst_path, "type": "file"})
                self._update_files_listbox()

    def _add_folder_to_list(self):
        dirpath = filedialog.askdirectory(title="选择要添加的文件夹", parent=self.root)
        if dirpath:
            dst_path = self._ask_destination_path(os.path.basename(dirpath))
            if dst_path is not None:
                self.additional_files_list.append({"src": dirpath, "dst": dst_path, "type": "folder"})
                self._update_files_listbox()

    def _ask_destination_path(self, source_name):
        # 创建一个简单的Toplevel窗口来获取目标路径
        dialog = tk.Toplevel(self.root)
        dialog.title("指定目标路径")
        dialog.geometry("400x150")
        dialog.transient(self.root) # 依赖于主窗口
        dialog.grab_set() # 模态

        ttk.Label(dialog, text=f"源: {source_name}").pack(pady=5)
        ttk.Label(dialog, text="目标路径 (在包内的相对路径, '.' 表示根目录):").pack(pady=5)
        dst_var = tk.StringVar(value=".") # 默认目标是包的根目录
        dst_entry = ttk.Entry(dialog, textvariable=dst_var, width=50)
        dst_entry.pack(pady=5)
        dst_entry.focus_set()

        result = {"dst": None} # 用字典传递结果，以便在取消时区分

        def on_ok():
            result["dst"] = dst_var.get().strip()
            if not result["dst"]: # 如果用户输入空，也视为'.'
                result["dst"] = "."
            dialog.destroy()

        def on_cancel():
            result["dst"] = None # 标记为取消
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=10)
        
        dialog.protocol("WM_DELETE_WINDOW", on_cancel) # 处理关闭按钮
        self.root.wait_window(dialog) # 等待对话框关闭
        return result["dst"]


    def _remove_selected_file(self):
        selected_indices = self.additional_files_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先在列表中选择一个要移除的项目。", parent=self.root)
            return

        # 从后往前删除，避免索引变化问题
        for index in sorted(selected_indices, reverse=True):
            del self.additional_files_list[index]
        self._update_files_listbox()

    def _clear_files_list(self):
        if not self.additional_files_list: return
        if messagebox.askokcancel("确认", "确定要清空所有已添加的附加文件/文件夹吗？", parent=self.root, icon=messagebox.WARNING):
            self.additional_files_list.clear()
            self._update_files_listbox()

    def _update_files_listbox(self):
        self.additional_files_listbox.delete(0, tk.END)
        for item in self.additional_files_list:
            display_text = f"{item['src']}  ->  (包内目标: {item['dst']})"
            self.additional_files_listbox.insert(tk.END, display_text)

    def add_tooltip(self, widget, text):
        tooltip = ToolTip(widget, text) # 已在上一版本中定义

    def _browse_script(self):
        filepath = filedialog.askopenfilename(
            title="选择 Python 脚本",
            filetypes=(("Python 文件", "*.py *.pyw"), ("所有文件", "*.*")),
            parent=self.root
        )
        if filepath:
            self.script_path_var.set(filepath)
            if not self.app_name_var.get():
                app_name = os.path.splitext(os.path.basename(filepath))[0]
                self.app_name_var.set(app_name)

    def _browse_icon(self):
        if os.name == 'nt': filetypes = (("图标文件", "*.ico"), ("所有文件", "*.*"))
        elif sys.platform == 'darwin': filetypes = (("图标文件", "*.icns"), ("所有文件", "*.*"))
        else: filetypes = (("PNG 图片", "*.png"), ("XBM 位图", "*.xbm"),("所有文件", "*.*"))
        filepath = filedialog.askopenfilename(title="选择图标文件", filetypes=filetypes, parent=self.root)
        if filepath: self.icon_path_var.set(filepath)

    def _browse_output_dir(self):
        dirpath = filedialog.askdirectory(title="选择输出目录", parent=self.root)
        if dirpath: self.output_dir_var.set(dirpath)

    def _browse_generic_dir(self, str_var_to_set, title_str):
        dirpath = filedialog.askdirectory(title=title_str, parent=self.root)
        if dirpath: str_var_to_set.set(dirpath)

    def _clear_options(self):
        self.script_path_var.set("")
        self.app_name_var.set("")
        self.package_mode_var.set("onefile")
        self.app_type_var.set("windowed")
        self.icon_path_var.set("")
        self.output_dir_var.set("")
        # 清空高级选项
        self.hidden_imports_text.delete("1.0", tk.END)
        self.exclude_modules_text.delete("1.0", tk.END)
        self.clean_build_var.set(True)
        self.noconfirm_var.set(True)
        self.upx_dir_var.set("")
        self.runtime_tmpdir_var.set("")
        # 清空附加文件列表
        self.additional_files_list.clear()
        self._update_files_listbox()
        self.log_message("所有选项已清空。", "info")


    def _start_packaging_thread(self):
        script_path = self.script_path_var.get()
        if not script_path:
            messagebox.showerror("错误", "请先选择要打包的 Python 脚本！", parent=self.root)
            return
        if not os.path.exists(script_path):
            messagebox.showerror("错误", f"选择的脚本文件不存在：\n{script_path}", parent=self.root)
            return

        self.set_gui_state("packaging_started")
        thread = threading.Thread(target=self._execute_pyinstaller_logic, daemon=True)
        thread.start()

    def _execute_pyinstaller_logic(self): # 重命名以区分
        try:
            cmd = [PYINSTALLER_CMD]
            script_path = self.script_path_var.get()
            script_dir = os.path.dirname(script_path)

            # --- 基本选项 ---
            app_name = self.app_name_var.get()
            if app_name: cmd.extend(['--name', app_name])
            if self.package_mode_var.get() == "onefile": cmd.append('--onefile')
            if self.app_type_var.get() == "windowed": cmd.append('--windowed')
            else: cmd.append('--console')
            icon_path = self.icon_path_var.get()
            if icon_path and os.path.exists(icon_path): cmd.extend(['--icon', icon_path])
            elif icon_path: self.log_message(f"警告: 图标文件 '{icon_path}' 不存在，已忽略。", "warning")

            output_dir = self.output_dir_var.get()
            spec_path_dir = script_dir # 默认 spec 文件在脚本目录
            if output_dir:
                if not os.path.isdir(output_dir):
                    try: os.makedirs(output_dir, exist_ok=True); self.log_message(f"信息: 输出目录 '{output_dir}' 已创建。", "info")
                    except Exception as e: self.log_message(f"警告: 创建输出目录 '{output_dir}' 失败: {e}。将使用默认。", "warning"); output_dir = ""
                if output_dir: # 如果 output_dir 有效
                    cmd.extend(['--distpath', os.path.join(output_dir, "dist")])
                    cmd.extend(['--workpath', os.path.join(output_dir, "build")])
                    spec_path_dir = output_dir # spec 文件也放到输出目录

            # --- 高级选项 ---
            if self.clean_build_var.get(): cmd.append('--clean')
            # if self.noconfirm_var.get(): cmd.append('--noconfirm') # PyInstaller 默认不确认

            upx_dir = self.upx_dir_var.get()
            if upx_dir and os.path.isdir(upx_dir): cmd.extend(['--upx-dir', upx_dir])
            elif upx_dir: self.log_message(f"警告: UPX 目录 '{upx_dir}' 不存在或不是目录，已忽略。", "warning")

            runtime_tmpdir = self.runtime_tmpdir_var.get()
            if runtime_tmpdir and self.package_mode_var.get() == "onefile":
                 if os.path.isdir(runtime_tmpdir): cmd.extend(['--runtime-tmpdir', runtime_tmpdir])
                 else: self.log_message(f"警告: 运行时临时目录 '{runtime_tmpdir}' 不存在或不是目录，已忽略。", "warning")
            elif runtime_tmpdir: self.log_message("信息: 运行时临时目录选项仅在单文件模式下有效。", "info")


            hidden_imports = self.hidden_imports_text.get("1.0", tk.END).strip().splitlines()
            for imp in hidden_imports:
                if imp.strip(): cmd.extend(['--hidden-import', imp.strip()])

            exclude_modules = self.exclude_modules_text.get("1.0", tk.END).strip().splitlines()
            for mod in exclude_modules:
                if mod.strip(): cmd.extend(['--exclude-module', mod.strip()])

            # --- 附加文件 ---
            for item_dict in self.additional_files_list:
                src_abs = os.path.abspath(item_dict["src"]) # 获取源的绝对路径
                dst_in_pkg = item_dict["dst"]
                if os.path.exists(src_abs):
                    # PyInstaller 的路径分隔符是 os.pathsep (通常是 ':' 或 ';')
                    cmd.extend(['--add-data', f'{src_abs}{os.pathsep}{dst_in_pkg}'])
                else:
                    self.log_message(f"警告: 附加文件/目录 '{item_dict['src']}' (解析为 {src_abs}) 未找到，已忽略。", "warning")

            cmd.extend(['--specpath', spec_path_dir])
            cmd.append(script_path)
            cmd = [str(c) for c in cmd if c]

            self.log_message(f"执行 PyInstaller 命令:\n{' '.join(shlex.quote(s) for s in cmd)}", "cmd")

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                bufsize=1, universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                cwd=script_dir # 执行目录保持为脚本所在目录，以处理脚本内部的相对路径
            )
            for line in process.stdout: self.log_message(line.strip())
            process.wait()

            if process.returncode == 0:
                self.log_message("\n打包成功完成！", "success")
                final_dist_path = os.path.join(output_dir, "dist") if output_dir else os.path.join(script_dir, "dist")
                self.gui_state_queue.put(("show_message", ("info", f"应用程序打包成功！\n输出目录: {final_dist_path}")))
            else:
                self.log_message(f"\n打包失败，返回码: {process.returncode}", "error")
                self.gui_state_queue.put(("show_message", ("error", "应用程序打包失败。\n请查看日志获取详细信息。")))

        except FileNotFoundError:
            self.log_message(f"错误: '{PYINSTALLER_CMD}' 命令未找到。", "error")
            self.gui_state_queue.put(("show_message", ("error", f"未能执行 PyInstaller。\n请确保它已安装并且在您的系统 PATH 中。")))
        except Exception as e:
            tb_str = traceback.format_exc()
            self.log_message(f"打包过程中发生意外错误: {e}\n{tb_str}", "error")
            self.gui_state_queue.put(("show_message", ("error", f"打包时发生错误: {e}")))
        finally:
            self.gui_state_queue.put(("packaging_finished", None))


    def log_message(self, message, level="normal"):
        self.log_queue.put((message, level))

    def set_gui_state(self, state):
        self.gui_state_queue.put((state, None))

    def process_ui_queues(self):
        # 处理日志队列
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                if level == "cmd":
                    self.log_text.insert(tk.END, message + "\n", "cmd")
                elif level == "info":
                    self.log_text.insert(tk.END, message + "\n", "info")
                elif level == "error":
                    self.log_text.insert(tk.END, message + "\n", "error")
                elif level == "warning":
                    self.log_text.insert(tk.END, message + "\n", "warning")
                elif level == "success":
                    self.log_text.insert(tk.END, message + "\n", "success")
                else: # normal
                    self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass

        # 处理GUI状态队列
        try:
            while True:
                command, data = self.gui_state_queue.get_nowait()
                if command == "packaging_started":
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.delete("1.0", tk.END) # 清空旧日志
                    self.log_text.config(state=tk.DISABLED)
                    self.log_message("开始准备打包...", "info")
                    self.package_button.config(state=tk.DISABLED, text="打包中...")
                elif command == "packaging_finished":
                    self.package_button.config(state=tk.NORMAL, text="开始打包")
                elif command == "show_message":
                    msg_type, msg_content = data
                    if msg_type == "info": messagebox.showinfo("信息", msg_content, parent=self.root)
                    elif msg_type == "error": messagebox.showerror("错误", msg_content, parent=self.root)
                    elif msg_type == "warning": messagebox.showwarning("警告", msg_content, parent=self.root)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_ui_queues)


# --- Tooltip 实现 (同前) ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
    def showtip(self):
        if self.tooltip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert") if isinstance(self.widget, (tk.Entry, scrolledtext.ScrolledText, tk.Text, tk.Listbox)) else self.widget.bbox()
        x += self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y += self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"), wraplength=350)
        label.pack(ipadx=2, ipady=2)
    def hidetip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw: tw.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    # --- 尝试使用更现代的TTK主题 (如果可用) ---
    if "clam" in ttk.Style().theme_names():
        ttk.Style().theme_use("clam")
    elif "vista" in ttk.Style().theme_names() and os.name == 'nt':
        ttk.Style().theme_use("vista")
    elif "aqua" in ttk.Style().theme_names() and sys.platform == 'darwin':
        ttk.Style().theme_use("aqua")
    # 否则使用默认

    app = PyInstallerGUI_CN_Advanced(root)
    root.mainloop()