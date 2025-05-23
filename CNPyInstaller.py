#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller Studio Pro (增强版) - 超现代化Python打包工具
使用CustomTkinter创建炫酷的现代化界面
版本: 3.1 (代码整理与健壮性增强)
"""

# --- 依赖引导程序 ---
import sys
import os
import subprocess
import importlib

# _RELAUNCH_ENV_VAR 和引导函数的定义... (此处省略以保持简洁)
_RELAUNCH_ENV_VAR = "PYINSTALLER_STUDIO_PRO_RELAUNCHED_FLAG_V3_1" 

def _bootstrap_attempt_install(package_name_on_pypi, import_name_to_check):
    # ... (引导程序代码) ...
    print(f"[引导程序] ⚠️ 未找到核心依赖: {package_name_on_pypi} (应导入为: {import_name_to_check})。")
    user_choice = input(f"是否立即尝试安装 {package_name_on_pypi} (运行本工具所必需)? (y/n): ").strip().lower()
    if user_choice == 'y':
        print(f"[引导程序] 正在尝试使用pip安装 {package_name_on_pypi}...")
        try:
            python_exe = sys.executable
            if sys.platform == "win32" and "pythonw.exe" in python_exe.lower():
                python_console_exe = python_exe.lower().replace("pythonw.exe", "python.exe")
                if os.path.exists(python_console_exe):
                    python_exe = python_console_exe
            subprocess.run(
                [python_exe, "-m", "pip", "install", package_name_on_pypi],
                check=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            print(f"[引导程序] ✅ {package_name_on_pypi} 安装命令已执行。")
            return True 
        except subprocess.CalledProcessError as e:
            print(f"[引导程序] ❌ {package_name_on_pypi} 安装失败。Pip输出:\n{e.stdout}\n{e.stderr}")
            print(f"[引导程序] 请尝试手动安装: pip install {package_name_on_pypi}")
            return False 
        except FileNotFoundError:
            print(f"[引导程序] ❌ 无法找到pip或python。请确保Python已正确安装并添加到PATH。")
            return False
    else:
        print(f"[引导程序] ❌ 用户取消安装。{package_name_on_pypi} 是必需的，程序无法继续。")
        return False

def _bootstrap_check_dependencies_and_relaunch_if_needed():
    # ... (引导程序代码) ...
    if os.environ.get(_RELAUNCH_ENV_VAR) == "1":
        os.environ.pop(_RELAUNCH_ENV_VAR, None) 
        print("[引导程序] 检测到重新启动标记，继续执行...")
        try:
            importlib.import_module("customtkinter")
            importlib.import_module("PIL") 
        except ImportError:
            print("[引导程序] ❌ 重新启动后，核心GUI依赖项仍然缺失。请检查之前的安装错误。")
            input("按回车键退出...")
            sys.exit(1) 
        return 
    core_gui_deps = {"customtkinter": "customtkinter", "Pillow": "PIL"}
    installed_new_package_during_bootstrap = False
    for pypi_name, import_name in core_gui_deps.items():
        try: importlib.import_module(import_name); print(f"[引导程序] ✅ 核心依赖 {pypi_name} (作为 {import_name}) 已存在。")
        except ImportError:
            if _bootstrap_attempt_install(pypi_name, import_name): installed_new_package_during_bootstrap = True
            else: input("按回车键退出..."); sys.exit(1) 
    if installed_new_package_during_bootstrap:
        print("[引导程序] 核心依赖已尝试安装。正在重新启动应用程序以应用更改..."); os.environ[_RELAUNCH_ENV_VAR] = "1"
        python_exe = sys.executable
        if sys.platform == "win32" and "pythonw.exe" in python_exe.lower():
            python_console_exe = python_exe.lower().replace("pythonw.exe", "python.exe")
            if os.path.exists(python_console_exe): python_exe = python_console_exe
        try: os.execv(python_exe, [python_exe] + sys.argv)
        except Exception as e: print(f"[引导程序] ❌ 重新启动失败: {e}\n[引导程序] 请关闭此窗口并手动重新运行脚本。"); input("按回车键退出..."); sys.exit(1)

_bootstrap_check_dependencies_and_relaunch_if_needed()
# --- 依赖引导程序结束 ---

# --- 主要模块导入 (在引导程序之后) ---
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import json
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox 
import webbrowser
import re
import logging # <--- 将 import logging 移到这里（全局导入区域）

# --- 全局外观设置 ---
# ... (ctk.set_appearance_mode 和 ctk.set_default_color_theme)
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue") 

# ==============================================================================
# 主应用程序类
# ==============================================================================
class UltraModernPyInstallerGUI:
    """PyInstaller Studio Pro 的主GUI应用程序类。"""

    def __init__(self):
        """初始化应用程序主窗口、变量、字体和UI组件。"""
        self.root = ctk.CTk()

        self._define_fonts()      # 统一定义字体
        self._setup_window()      # 设置主窗口属性
        self._setup_variables()   # 初始化所有Tkinter变量和内部状态变量
        self._create_widgets()    # 创建所有UI组件
        self.load_config()        # 程序启动时加载上次保存的配置
        self._setup_animations()  # 设置UI动画效果

    def _define_fonts(self):
        """统一定义应用程序中使用的字体对象。"""
        font_family_ui = "Microsoft YaHei UI" # UI元素首选字体 (微软雅黑UI)
        font_family_code = "Consolas"        # 代码/路径等宽字体

        self.font_default = ctk.CTkFont(family=font_family_ui, size=13)
        self.font_default_bold = ctk.CTkFont(family=font_family_ui, size=13, weight="bold")
        self.font_small = ctk.CTkFont(family=font_family_ui, size=11)
        
        self.font_title_main = ctk.CTkFont(family=font_family_ui, size=32, weight="bold")
        self.font_title_sub = ctk.CTkFont(family=font_family_ui, size=14)
        self.font_section_title = ctk.CTkFont(family=font_family_ui, size=18, weight="bold")
        
        self.font_button = ctk.CTkFont(family=font_family_ui, size=13, weight="bold")
        self.font_button_large = ctk.CTkFont(family=font_family_ui, size=16, weight="bold")
        self.font_switch = ctk.CTkFont(family=font_family_ui, size=13, weight="bold")
        
        self.font_input_text = ctk.CTkFont(family=font_family_code, size=13) 
        self.font_log_terminal = ctk.CTkFont(family=font_family_code, size=12)
        
        self.font_status_indicator = ctk.CTkFont(size=20) 
        self.font_status_text = ctk.CTkFont(family=font_family_ui, size=12, weight="bold")
        self.font_tooltip = ctk.CTkFont(family=font_family_ui, size=11)

    # --- UI元素创建辅助方法 ---

    def _create_input_row_helper(self, 
                                 parent_container: ctk.CTkFrame, 
                                 label_text_str: str, 
                                 tkinter_var: tk.StringVar, 
                                 placeholder_text_str: str, 
                                 browse_command_func,
                                 label_font, 
                                 entry_font, 
                                 button_font, 
                                 browse_button_text_str: str = "浏览"):
        """
        (私有辅助方法) 创建一个标准的输入行，包含一个标签、一个输入框和一个浏览按钮。
        用于简化在UI中创建类似表单条目的代码。

        Args:
            parent_container (ctk.CTkFrame): 此输入行将被放置到的父容器Frame。
            label_text_str (str): 显示在输入框上方的标签文本。
            tkinter_var (tk.StringVar): 与输入框绑定的Tkinter字符串变量。
            placeholder_text_str (str): 输入框中显示的占位符文本。
            browse_command_func: 点击浏览按钮时要执行的回调函数。
            label_font: 标签文本的字体对象。
            entry_font: 输入框文本的字体对象。
            button_font: 浏览按钮文本的字体对象。
            browse_button_text_str (str, optional): 浏览按钮上显示的文本。默认为 "浏览"。

        Returns:
            tuple: (ctk.CTkEntry, ctk.CTkButton) 创建的输入框和浏览按钮实例，方便后续可能的操作。
        """
        # 中文注释: 这是一个创建标准“标签-输入框-按钮”组合行的辅助函数，用于减少重复代码。

        # 创建此输入行的容器Frame，使用透明背景以融入父容器
        row_container_frame = ctk.CTkFrame(parent_container, fg_color="transparent")
        row_container_frame.pack(fill="x", padx=20, pady=(7, 12)) # 调整上下间距使布局更舒适

        # 创建并放置标签
        label_widget = ctk.CTkLabel(row_container_frame, text=label_text_str, font=label_font)
        label_widget.pack(anchor="w", pady=(0, 4)) # 标签与输入框之间留出少量垂直间距

        # 创建用于容纳输入框和浏览按钮的内部Frame，使用Grid布局方便对齐
        input_elements_frame = ctk.CTkFrame(row_container_frame, fg_color="transparent")
        input_elements_frame.pack(fill="x")
        input_elements_frame.grid_columnconfigure(0, weight=1) # 让输入框列占据所有可用额外空间

        # 创建输入框 (CTkEntry)
        entry_widget = ctk.CTkEntry(
            input_elements_frame, 
            textvariable=tkinter_var, 
            placeholder_text=placeholder_text_str, 
            font=entry_font,
            corner_radius=6 # 可以给输入框也加点圆角
        )
        entry_widget.grid(row=0, column=0, sticky="ew", padx=(0, 8)) # 输入框右侧留8像素间距

        # 创建浏览按钮 (CTkButton)
        button_widget = ctk.CTkButton(
            input_elements_frame, 
            text=browse_button_text_str, 
            width=80, # 固定按钮宽度
            command=browse_command_func, 
            font=button_font,
            corner_radius=6 # 按钮也使用圆角
        )
        button_widget.grid(row=0, column=1) # 按钮紧随输入框

        return entry_widget, button_widget # 返回创建的控件，以备不时之需

    def _setup_window(self):
        """设置主窗口的标题、大小、图标等。"""
        self.root.title("🚀 PyInstaller Studio Pro (增强版 v3.1)  作者：跳舞的火公子")
        self.root.geometry("1250x850") 
        self.root.minsize(1100, 750)  
        try: 
            # 尝试从脚本同目录加载icon.ico
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except tk.TclError: # 图标加载失败则静默处理
            pass 
        self._center_window() 
        
    def _center_window(self):
        """将主窗口在屏幕上居中显示。"""
        self.root.update_idletasks() # 确保获取到正确的窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def _setup_variables(self):
        """初始化所有Tkinter变量和应用程序内部状态变量。"""
        # --- Tkinter 字符串/布尔/整数/浮点变量 ---
        self.project_root_dir = tk.StringVar() 
        self.script_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.app_name = tk.StringVar()
        self.is_onefile = tk.BooleanVar(value=True)
        self.is_windowed = tk.BooleanVar()
        self.is_debug = tk.BooleanVar()
        self.is_clean = tk.BooleanVar(value=True)
        self.is_upx = tk.BooleanVar()
        self.exclude_modules = tk.StringVar()
        self.hidden_imports = tk.StringVar()
        self.upx_dir = tk.StringVar()
        
        # --- 内部状态变量 ---
        self.add_data_list = []       # 存储 {source: dest} 格式的数据文件条目
        self.is_building = False      # 标记当前是否正在执行构建
        self.status_animation_on = True # 控制状态指示器动画
        self.status_indicator_alt_color_active = False # 动画辅助
        
    def _create_widgets(self):
        """创建应用程序主界面的所有UI组件和布局。"""
        # 主容器
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建头部区域
        self._create_header(main_container)
        
        # 创建内容区域 (选项卡和底部控制栏的父容器)
        content_frame = ctk.CTkFrame(main_container, corner_radius=20, fg_color=("gray90", "gray10"))
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # 创建选项卡视图
        self._create_tabview(content_frame)
        
        # 创建底部控制栏
        self._create_bottom_controls(content_frame)

    # --- 各主要UI区域的创建方法 (细节与之前增强版一致，此处为高层结构展示) ---
    def _create_header(self, parent): # (实现同前，应用字体)
        header_frame = ctk.CTkFrame(parent, height=120, corner_radius=20, fg_color=("gray85", "gray15"))
        header_frame.pack(fill="x", pady=(0, 10)); header_frame.pack_propagate(False)
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(expand=True, fill="both", padx=30, pady=20)
        ctk.CTkLabel(title_frame, text="🚀 PyInstaller Studio Pro", font=self.font_title_main, text_color=("gray10", "#00FF7F")).pack(side="left", pady=10)
        ctk.CTkLabel(title_frame, text="下一代 Python 应用打包工具 • 现代化 • 智能化 • 炫酷界面", font=self.font_title_sub, text_color=("gray40", "gray60")).pack(side="left", padx=(20, 0), pady=10)
        self.status_frame = ctk.CTkFrame(title_frame, width=200, height=60, corner_radius=15, fg_color=("gray80", "gray20"))
        self.status_frame.pack(side="right", padx=(20, 0)); self.status_frame.pack_propagate(False)
        self.status_indicator = ctk.CTkLabel(self.status_frame, text="🟢", font=self.font_status_indicator)
        self.status_indicator.pack(pady=(5,0))
        self.status_text = ctk.CTkLabel(self.status_frame, text="系统就绪", font=self.font_status_text, text_color=("gray10", "#00FF7F"))
        self.status_text.pack()

    def _create_tabview(self, parent): # (实现同前，已移除对tabview的font设置)
        self.tabview = ctk.CTkTabview(parent, corner_radius=15, 
                                     segmented_button_selected_color=("#3B8ED0", "#1F6AA5"),
                                     segmented_button_selected_hover_color=("#36719F", "#144870"))
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.basic_tab = self.tabview.add("🎯 基础配置")
        self.advanced_tab = self.tabview.add("⚙️ 高级设置") 
        self.output_tab = self.tabview.add("📱 构建输出")
        self.tools_tab = self.tabview.add("🛠️ 工具箱")
        self._create_basic_tab_content() # 修改方法名以示区分
        self._create_advanced_tab_content()
        self._create_output_tab_content()
        self._create_tools_tab_content()

    def _create_bottom_controls(self, parent): # (实现同前，应用字体)
        bottom_frame = ctk.CTkFrame(parent, height=80, corner_radius=20, fg_color=("gray85", "gray15"))
        bottom_frame.pack(fill="x", padx=20, pady=20); bottom_frame.pack_propagate(False)
        self.build_button = ctk.CTkButton(bottom_frame, text="🚀 开始构建应用程序", font=self.font_button_large, command=self.start_build, width=250, height=50, corner_radius=15, fg_color=("#FF6B35", "#E65100"), hover_color=("#FF8C42", "#F57C00"))
        self.build_button.pack(side="left", padx=20, pady=15)
        config_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        config_frame.pack(side="right", padx=20, pady=15)
        ctk.CTkButton(config_frame, text="💾 保存", command=self.save_config, width=80, height=35, font=self.font_button).pack(side="left", padx=(0,10))
        ctk.CTkButton(config_frame, text="🔄 重置", command=self.reset_config, width=80, height=35, font=self.font_button).pack(side="left")

    # --- 选项卡内容填充方法 (增强版：确保字体应用、包含新功能、提升UI布局和健壮性) ---

    def _create_basic_tab_content(self):
        """创建“基础配置”选项卡内的所有UI元素，包括项目根目录设置。"""
        # 中文注释: 此方法负责构建“基础配置”页面的所有控件和布局。
        
        # 使用可滚动的Frame，以防内容过多超出显示区域
        scroll_frame = ctk.CTkScrollableFrame(self.basic_tab, corner_radius=10, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- 文件与路径配置区域 ---
        files_config_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        files_config_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(files_config_frame, text="📁 文件与路径配置", font=self.font_section_title).pack(pady=(15,10))

        # 使用辅助方法创建标准的输入行 (标签 + 输入框 + 浏览按钮)
        self._create_input_row_helper(
            parent_container=files_config_frame, 
            label_text_str="🐍 Python 主脚本:", 
            tkinter_var=self.script_path, 
            placeholder_text_str="请选择您的 Python 主程序文件 (.py 或 .pyw)", 
            browse_command_func=self.browse_script,
            label_font=self.font_default_bold, 
            entry_font=self.font_input_text, 
            button_font=self.font_button
        )
        
        # 新增：项目根目录设置
        self._create_input_row_helper(
            parent_container=files_config_frame, 
            label_text_str="🌳 项目根目录 (可选):", 
            tkinter_var=self.project_root_dir, 
            placeholder_text_str="选择项目根文件夹 (用于数据文件相对路径参考)", 
            browse_command_func=self.browse_project_root,
            label_font=self.font_default_bold, 
            entry_font=self.font_input_text, 
            button_font=self.font_button
        )
        # 项目根目录的说明性提示标签
        project_root_hint_label = ctk.CTkLabel(files_config_frame, 
                                               text="提示: 设置项目根目录后，在“高级设置”中添加数据文件或文件夹时，文件选择对话框将默认从此目录开始，并会尝试给出相对于此根目录的目标路径建议。", 
                                               font=self.font_small, 
                                               text_color=("gray50", "gray55"), # 调整颜色使其更易读
                                               justify="left")
        project_root_hint_label.pack(fill="x", padx=25, pady=(0,10))
        # 动态更新提示标签的换行宽度
        files_config_frame.bind("<Configure>", lambda event, lbl=project_root_hint_label, parent=files_config_frame: self._update_label_wraplength(lbl, parent, 50))


        # 输出目录设置
        self._create_input_row_helper(
            parent_container=files_config_frame, 
            label_text_str="📂 构建输出目录:", 
            tkinter_var=self.output_dir, 
            placeholder_text_str="选择打包结果的输出位置 (默认: ./dist)", 
            browse_command_func=self.browse_output,
            label_font=self.font_default_bold, 
            entry_font=self.font_input_text, 
            button_font=self.font_button
        )

        # --- 应用程序配置区域 ---
        app_details_config_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        app_details_config_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(app_details_config_frame, text="🎨 应用程序详情配置", font=self.font_section_title).pack(pady=(15,10))
        
        # 使用Grid布局应用名称和图标输入，使其并排显示
        app_name_icon_grid_frame = ctk.CTkFrame(app_details_config_frame, fg_color="transparent")
        app_name_icon_grid_frame.pack(fill="x", padx=20, pady=10)
        app_name_icon_grid_frame.grid_columnconfigure((0,1), weight=1) # 两列等宽

        # 应用名称输入
        app_name_frame = ctk.CTkFrame(app_name_icon_grid_frame, fg_color="transparent")
        app_name_frame.grid(row=0, column=0, sticky="ew", padx=(0,10))
        ctk.CTkLabel(app_name_frame, text="📝 应用程序名称:", font=self.font_default_bold).pack(anchor="w", pady=(0,5))
        self.name_entry = ctk.CTkEntry(app_name_frame, textvariable=self.app_name, placeholder_text="输入打包后的应用程序名称", font=self.font_default)
        self.name_entry.pack(fill="x")

        # 应用图标选择
        app_icon_frame = ctk.CTkFrame(app_name_icon_grid_frame, fg_color="transparent")
        app_icon_frame.grid(row=0, column=1, sticky="ew", padx=(10,0))
        ctk.CTkLabel(app_icon_frame, text="🎭 应用程序图标:", font=self.font_default_bold).pack(anchor="w", pady=(0,5))
        icon_input_elements_frame = ctk.CTkFrame(app_icon_frame, fg_color="transparent")
        icon_input_elements_frame.pack(fill="x")
        icon_input_elements_frame.grid_columnconfigure(0, weight=1)
        self.icon_entry = ctk.CTkEntry(icon_input_elements_frame, textvariable=self.icon_path, placeholder_text="选择图标文件 (.ico, .png)", font=self.font_input_text)
        self.icon_entry.grid(row=0, column=0, sticky="ew", padx=(0,8))
        ctk.CTkButton(icon_input_elements_frame, text="📁", width=35, command=self.browse_icon, font=self.font_button).grid(row=0, column=1) # 图标按钮略宽一点

        # --- 打包选项区域 ---
        packaging_options_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        packaging_options_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(packaging_options_frame, text="⚡ 主要打包选项", font=self.font_section_title).pack(pady=(15,10))
        
        switches_container_grid = ctk.CTkFrame(packaging_options_frame, fg_color="transparent")
        switches_container_grid.pack(fill="x", padx=20, pady=10)
        switches_container_grid.grid_columnconfigure((0,1), weight=1, uniform="switch_cols") # uniform确保列宽一致

        # 左侧开关列
        left_switches_column = ctk.CTkFrame(switches_container_grid, fg_color="transparent")
        left_switches_column.grid(row=0, column=0, sticky="new", padx=(0,15)) # 增加列间距
        self.onefile_switch = ctk.CTkSwitch(left_switches_column, text="🎯 单文件模式 (OneFile)", variable=self.is_onefile, font=self.font_switch)
        self.onefile_switch.pack(anchor="w", pady=(0,12)) # 增加开关间垂直间距
        self.windowed_switch = ctk.CTkSwitch(left_switches_column, text="🖼️ 窗口模式 (无控制台)", variable=self.is_windowed, font=self.font_switch)
        self.windowed_switch.pack(anchor="w")

        # 右侧开关列
        right_switches_column = ctk.CTkFrame(switches_container_grid, fg_color="transparent")
        right_switches_column.grid(row=0, column=1, sticky="new", padx=(15,0))
        self.debug_switch = ctk.CTkSwitch(right_switches_column, text="🐛 调试模式 (Debug All)", variable=self.is_debug, font=self.font_switch)
        self.debug_switch.pack(anchor="w", pady=(0,12))
        self.clean_switch = ctk.CTkSwitch(right_switches_column, text="🧹 清理上次构建缓存", variable=self.is_clean, font=self.font_switch)
        self.clean_switch.pack(anchor="w")

    def _create_advanced_tab_content(self):
        """创建“高级设置”选项卡内的所有UI元素，包括对隐藏导入和数据文件的说明。"""
        # 中文注释: 此方法构建“高级设置”页面的控件，用于更细致的打包配置。
        scroll_frame = ctk.CTkScrollableFrame(self.advanced_tab, corner_radius=10, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 模块与依赖管理区域 ---
        modules_deps_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        modules_deps_frame.pack(fill="x", pady=(0,20))
        ctk.CTkLabel(modules_deps_frame, text="📦 模块与依赖项管理", font=self.font_section_title).pack(pady=(15,10))
        
        # 排除模块输入
        exclude_modules_subframe = ctk.CTkFrame(modules_deps_frame, fg_color="transparent")
        exclude_modules_subframe.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(exclude_modules_subframe, text="🚫 排除模块 (用英文逗号 ',' 分隔):", font=self.font_default_bold).pack(anchor="w", pady=(0,5))
        self.exclude_entry = ctk.CTkEntry(exclude_modules_subframe, textvariable=self.exclude_modules, placeholder_text="例如: tkinter, matplotlib, pandas", font=self.font_input_text)
        self.exclude_entry.pack(fill="x")
        exclude_hint_label = ctk.CTkLabel(exclude_modules_subframe, text="此选项用于明确从打包结果中排除某些Python模块，以减小最终应用的体积。PyInstaller通常会自动包含脚本中直接import的模块。", 
                                          font=self.font_small, text_color=("gray50", "gray55"), justify="left")
        exclude_hint_label.pack(fill="x", pady=(3,0))
        modules_deps_frame.bind("<Configure>", lambda e, lbl=exclude_hint_label, p=exclude_modules_subframe: self._update_label_wraplength(lbl,p,40))


        # 隐藏导入输入
        hidden_imports_subframe = ctk.CTkFrame(modules_deps_frame, fg_color="transparent")
        hidden_imports_subframe.pack(fill="x", padx=20, pady=(10,15)) # 调整pady
        ctk.CTkLabel(hidden_imports_subframe, text="📥 隐藏导入 (用英文逗号 ',' 分隔):", font=self.font_default_bold).pack(anchor="w", pady=(0,5))
        self.hidden_entry = ctk.CTkEntry(hidden_imports_subframe, textvariable=self.hidden_imports, placeholder_text="例如: requests, openai, PyQt5.QtCore, my_plugin_module", font=self.font_input_text)
        self.hidden_entry.pack(fill="x")
        hidden_hint_label = ctk.CTkLabel(hidden_imports_subframe, text="如果您的脚本通过特殊方式（如字符串名称、插件机制）动态导入了某些模块，或者PyInstaller未能自动检测到某些关键的第三方库（特别是那些包含二进制文件或数据文件的库），请在此处列出它们的模块名。", 
                                         font=self.font_small, text_color=("gray50", "gray55"), justify="left")
        hidden_hint_label.pack(fill="x", pady=(3,0))
        modules_deps_frame.bind("<Configure>", lambda e, lbl=hidden_hint_label, p=hidden_imports_subframe: self._update_label_wraplength(lbl,p,40), add="+")


        # --- 数据文件与资源区域 ---
        data_files_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        data_files_frame.pack(fill="x", pady=(0,20))
        ctk.CTkLabel(data_files_frame, text="📎 附加数据文件与资源", font=self.font_section_title).pack(pady=(15,5)) # 调整pady
        data_files_hint_label = ctk.CTkLabel(data_files_frame, 
                                             text="您可以添加非Python代码文件（如图片、JSON配置文件、文本数据、其他辅助.py脚本等）或整个文件夹到最终的打包结果中。\n“目标路径”是指这些文件/文件夹在打包后的应用程序结构中的相对位置。使用英文句点 '.' 作为目标路径，表示将文件/文件夹直接放在与主可执行文件相同的根目录下。", 
                                             font=self.font_small, text_color=("gray50", "gray55"), justify="left")
        data_files_hint_label.pack(fill="x", padx=20, pady=(0,10))
        data_files_frame.bind("<Configure>", lambda e, lbl=data_files_hint_label, p=data_files_frame: self._update_label_wraplength(lbl,p,40), add="+")
        
        # 数据文件列表显示框
        data_list_display_subframe = ctk.CTkFrame(data_files_frame, fg_color="transparent")
        data_list_display_subframe.pack(fill="x", padx=20, pady=(0,10)) # 调整pady
        self.data_textbox = ctk.CTkTextbox(data_list_display_subframe, height=130, font=self.font_log_terminal, state="disabled", wrap="word") # 增加高度, wrap="word"
        self.data_textbox.pack(fill="x", expand=True) # 让文本框可以扩展
        self.update_data_textbox() # 初始化时填充内容

        # 数据文件操作按钮 (添加文件/文件夹, 清空列表)
        data_file_buttons_subframe = ctk.CTkFrame(data_files_frame, fg_color="transparent")
        data_file_buttons_subframe.pack(fill="x", padx=20, pady=(0,15)) # 调整pady
        ctk.CTkButton(data_file_buttons_subframe, text="📄 添加文件", command=self.add_data_file, font=self.font_button).pack(side="left", padx=(0,10))
        ctk.CTkButton(data_file_buttons_subframe, text="📁 添加文件夹", command=self.add_data_folder, font=self.font_button).pack(side="left", padx=(0,10))
        ctk.CTkButton(data_file_buttons_subframe, text="🗑️ 清空列表", command=self.clear_data_files, font=self.font_button, 
                      fg_color=("#E53935", "#C62828"), hover_color=("#D32F2F", "#B71C1C")).pack(side="left")

        # --- 性能优化区域 (UPX设置) ---
        performance_options_frame = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color=("gray88", "gray12"))
        performance_options_frame.pack(fill="x", pady=(0,20))
        ctk.CTkLabel(performance_options_frame, text="🚀 可执行文件优化", font=self.font_section_title).pack(pady=(15,10))

        upx_config_subframe = ctk.CTkFrame(performance_options_frame, fg_color="transparent")
        upx_config_subframe.pack(fill="x", padx=20, pady=10)
        self.upx_switch = ctk.CTkSwitch(upx_config_subframe, text="🗜️ 启用 UPX 压缩 (如果UPX已安装并配置)", variable=self.is_upx, font=self.font_switch)
        self.upx_switch.pack(anchor="w", pady=(0,10))
        
        upx_path_input_row = ctk.CTkFrame(upx_config_subframe, fg_color="transparent")
        upx_path_input_row.pack(fill="x")
        upx_path_input_row.grid_columnconfigure(1, weight=1) # 让输入框占据更多空间
        ctk.CTkLabel(upx_path_input_row, text="UPX 工具目录 (可选):", font=self.font_default_bold).grid(row=0, column=0, sticky="w", pady=(0,5), padx=(0,8)) # 调整标签和间距
        self.upx_entry = ctk.CTkEntry(upx_path_input_row, textvariable=self.upx_dir, placeholder_text="指定UPX可执行文件所在目录 (留空则从系统PATH查找)", font=self.font_input_text)
        self.upx_entry.grid(row=0, column=1, sticky="ew", padx=(0,8))
        ctk.CTkButton(upx_path_input_row, text="📁", width=35, command=self.browse_upx, font=self.font_button).grid(row=0, column=2)

    def _create_output_tab_content(self): # (实现同前)
        # ... (代码同前，确保应用字体)
        progress_frame = ctk.CTkFrame(self.output_tab, corner_radius=15, fg_color=("gray88", "gray12")); progress_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(progress_frame, text="📊 构建进度", font=self.font_section_title).pack(pady=(15,10))
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400, height=20, corner_radius=10); self.progress_bar.pack(pady=10); self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(progress_frame, text="等待开始构建...", font=self.font_default_bold); self.progress_label.pack(pady=(0,15))
        terminal_frame = ctk.CTkFrame(self.output_tab, corner_radius=15, fg_color=("gray88", "gray12")); terminal_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
        ctk.CTkLabel(terminal_frame, text="💻 构建日志输出", font=self.font_section_title).pack(pady=(15,10)) # 标题微调
        self.terminal_textbox = ctk.CTkTextbox(terminal_frame, font=self.font_log_terminal, fg_color=("gray95", "gray5"), text_color=("SeaGreen3", "PaleGreen1"), state="disabled", wrap="word"); self.terminal_textbox.pack(fill="both", expand=True, padx=20, pady=(0,20))
        # 初始化日志
        self.terminal_textbox.configure(state="normal")
        self.terminal_textbox.insert("0.0", f"🚀 PyInstaller Studio Pro (增强版 v3.1) 已启动\n"); self.terminal_textbox.insert("end", f"🕒 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"); self.terminal_textbox.insert("end", f"📁 当前工作目录: {os.getcwd()}\n"); self.terminal_textbox.insert("end", "💡 系统已就绪，等待您的构建指令...\n"); self.terminal_textbox.insert("end", "=" * 80 + "\n") # 分隔线加长
        self.terminal_textbox.configure(state="disabled")

    def _create_tools_tab_content(self): # (实现同前增强版，包含打开.spec文件，优化布局)
        # ... (代码同前，确保应用字体)
        scroll_frame = ctk.CTkScrollableFrame(self.tools_tab, corner_radius=10, fg_color="transparent"); scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tools_grid_container = ctk.CTkFrame(scroll_frame, fg_color="transparent"); tools_grid_container.pack(fill="x", pady=10)
        # 让列均匀分配空间
        tools_grid_container.grid_columnconfigure((0,1,2), weight=1, uniform="tool_button_col")

        tools_definitions = [
            ("🧹 清理构建文件", self.clean_build_files, "清理所有PyInstaller构建产生的临时文件和输出目录。"),
            ("📁 打开输出目录", self.open_output_dir, "在文件浏览器中快速打开打包结果所在的输出目录。"),
            ("📋 复制构建命令", self.copy_command, "将当前配置生成的完整PyInstaller命令行复制到系统剪贴板。"),
            ("💾 保存当前配置", self.save_config_file, "将当前界面的所有配置参数保存到一个JSON文件中，供以后加载。"),
            ("📂 加载配置文件", self.load_config_file, "从之前保存的JSON文件中加载配置参数到当前界面。"),
            ("🔧 检查依赖环境", self.check_dependencies, "检查PyInstaller、UPX以及项目中可能需要的常用第三方库是否可用。"),
            ("📝 打开 .spec 文件", self.open_spec_file, "在系统默认文本编辑器中打开当前项目生成的.spec配置文件 (高级用户)。"),
            ("📖 查看官方文档", self.open_docs, "在浏览器中打开PyInstaller官方在线文档 (英文)。"),
            ("ℹ️ 关于本软件", self.show_about, "显示本软件的版本信息、特性和开发者信息。"),
            ("🎨 切换界面主题", self.toggle_theme, "在明亮和深色两种界面主题之间进行一键切换。")
        ]
        
        for i, (button_text, action_command, tooltip_description) in enumerate(tools_definitions):
            grid_row, grid_col = divmod(i, 3) # 每行最多3个按钮
            
            # 为每个按钮创建一个独立的Frame容器，以便更好地控制其在Grid中的填充和对齐
            button_wrapper_frame = ctk.CTkFrame(tools_grid_container, fg_color="transparent")
            button_wrapper_frame.grid(row=grid_row, column=grid_col, padx=8, pady=8, sticky="ew") # sticky="ew" 使Frame水平填充
            tools_grid_container.grid_rowconfigure(grid_row, weight=1) # 让行也有权重，有助于垂直对齐（如果行高不同）

            tool_button = ctk.CTkButton(button_wrapper_frame, text=button_text, command=action_command, 
                                        height=48, corner_radius=10, font=self.font_button) # 统一按钮高度和字体
            tool_button.pack(fill=tk.X, expand=True, ipady=3) # 按钮在自己的Frame中填充X方向，并略微增加垂直内边距
            self._create_tooltip(tool_button, tooltip_description) # 为按钮添加工具提示

    def _update_label_wraplength(self, label_widget, parent_reference_widget, horizontal_padding): # 新增辅助方法
        """动态更新Label的wraplength，使其适应父容器宽度。"""
        if not (label_widget.winfo_exists() and parent_reference_widget.winfo_exists()):
            return
        try:
            parent_width = parent_reference_widget.winfo_width()
            available_width = parent_width - horizontal_padding # 减去两边的总padding
            if available_width > 20: # 避免wraplength过小
                label_widget.configure(wraplength=available_width)
        except tk.TclError:
            pass # 组件可能尚未完全映射或已销毁
    
    
    # --- UI动画与工具提示方法 (增强可读性和健壮性) ---

    def _setup_animations(self):
        """初始化并启动应用程序中定义的UI动画效果，例如状态指示器的动画。"""
        # 中文注释: 此方法在GUI初始化时调用，用于启动所有需要持续运行的动画。
        self.status_animation_on = True  # 设置动画总开关为开启
        self.animate_status_indicator()  # 启动状态指示器的动画循环

    def animate_status_indicator(self):
        """
        状态指示器“呼吸灯”效果的动画循环。
        此动画仅在应用程序状态为“系统就绪”且未进行构建时激活。
        通过 self.root.after() 周期性调用自身以实现动画。
        """
        # 中文注释: 实现顶部状态栏指示器的闪烁/呼吸效果。

        # 检查动画是否应继续执行的条件：
        # 1. 主窗口 (self.root) 是否仍然存在。
        # 2. 全局动画开关 (self.status_animation_on) 是否为True。
        # 如果任一条件不满足，则直接返回，不再调度下一次动画。
        if not (hasattr(self, 'root') and self.root.winfo_exists() and self.status_animation_on):
            return

        # 如果当前正在构建 (self.is_building is True)，则暂停此特定动画的视觉变化，
        # 但仍然调度下一次检查，以便在构建结束后能自动恢复。
        if self.is_building:
            self.root.after(1500, self.animate_status_indicator) # 1.5秒后再次检查
            return

        # 确保状态指示器和状态文本组件都已创建且存在
        if hasattr(self, 'status_indicator') and self.status_indicator.winfo_exists() and \
           hasattr(self, 'status_text') and self.status_text.winfo_exists():
            
            current_status_message = self.status_text.cget("text")
            current_indicator_symbol = self.status_indicator.cget("text")

            # 仅当系统状态为“系统就绪”时，才执行图标的交替显示
            if current_status_message == "系统就绪":
                # 通过 self.status_indicator_alt_color_active 标志来切换图标
                if current_indicator_symbol == "🟢":
                    self.status_indicator.configure(text="●") # 从实心圆点切换到空心圆点 (或任何其他交替符号)
                else: # 如果是 "●" 或其他非 "🟢" 的符号 (且状态是就绪)
                    self.status_indicator.configure(text="🟢") # 切换回实心绿色圆点
            elif current_indicator_symbol == "●": # 如果状态不再是“系统就绪”，但图标仍是“●”
                # 则强制将其恢复为默认的绿色实心圆点，以匹配非就绪状态的默认显示
                self.status_indicator.configure(text="🟢")
        
        # 调度下一次动画帧 (大约1.2秒后)
        if hasattr(self, 'root') and self.root.winfo_exists(): # 再次检查root，因为configure可能耗时
            self.root.after(1200, self.animate_status_indicator)

    def _create_tooltip(self, target_widget: ctk.CTkBaseClass, tooltip_text_str: str):
        """
        为给定的CustomTkinter控件创建一个自定义的工具提示。
        当鼠标悬停在控件上时显示，移开时消失。使用CTkToplevel以保持风格统一。

        Args:
            target_widget (ctk.CTkBaseClass): 要为其添加工具提示的CustomTkinter控件。
            tooltip_text_str (str): 工具提示中要显示的文本。
        """
        # 中文注释: 为UI元素（如按钮）创建鼠标悬停时显示的提示信息。

        tooltip_window_instance = None # 用于存储当前活动的CTkToplevel提示窗口实例

        def _show_tooltip_on_mouse_enter(event_details):
            """鼠标进入控件区域时触发，显示工具提示。"""
            nonlocal tooltip_window_instance # 允许修改外部作用域的变量
            
            # 如果已存在提示窗口，或者提示文本为空，则不执行任何操作
            if tooltip_window_instance or not tooltip_text_str:
                return

            # 创建一个新的CTkToplevel窗口作为提示框
            tooltip_window_instance = ctk.CTkToplevel(self.root)
            tooltip_window_instance.wm_overrideredirect(True) # 移除窗口边框和标题栏

            # --- 动态确定提示框的背景色和文本色，以适应当前主题 ---
            try:
                # 尝试获取目标控件的前景色(fg_color)作为提示背景的基准
                # CTk控件的fg_color通常是一个元组 (light_mode_color, dark_mode_color)
                host_widget_fg_color_tuple = target_widget.cget("fg_color")
                current_theme_mode = ctk.get_appearance_mode() # "Light" 或 "Dark"
                
                # 根据当前主题选择颜色
                base_bg_color_hex = host_widget_fg_color_tuple[1] if current_theme_mode == "Dark" else host_widget_fg_color_tuple[0]
                
                # 简单的亮度计算来决定文本颜色，以确保可读性
                # (这是一个简化的方法，实际的色彩对比度计算可能更复杂)
                r_val, g_val, b_val = int(base_bg_color_hex[1:3],16), int(base_bg_color_hex[3:5],16), int(base_bg_color_hex[5:7],16)
                # W3C推荐的亮度计算公式: Y = 0.2126 R + 0.7152 G + 0.0722 B
                # (或者可以使用更简单的平均值，但前者更准确地反映人眼感知)
                perceived_brightness = 0.2126 * r_val + 0.7152 * g_val + 0.0722 * b_val
                
                # 根据背景亮度选择对比强烈的文本颜色
                tooltip_text_color_hex = "#101010" if perceived_brightness > 128 else "#DCE4EE" # 暗背景用亮字，亮背景用暗字
                tooltip_bg_color_hex = base_bg_color_hex
            except (IndexError, ValueError, TypeError, AttributeError): 
                # 如果获取或解析颜色失败，使用通用的默认值
                tooltip_bg_color_hex = "#333333" if ctk.get_appearance_mode() == "Dark" else "#FFFFE0" # 深灰或淡黄
                tooltip_text_color_hex = "#DCE4EE" if ctk.get_appearance_mode() == "Dark" else "#101010" # 亮白或深黑
            
            # 创建显示提示文本的CTkLabel
            tooltip_label = ctk.CTkLabel(
                tooltip_window_instance, 
                text=tooltip_text_str, 
                corner_radius=3,          # 小圆角
                font=self.font_tooltip,   # 使用预定义的工具提示字体
                fg_color=tooltip_bg_color_hex,  # 计算得到的背景色
                text_color=tooltip_text_color_hex, # 计算得到的文本色
                padx=7, pady=4            # 内部边距，让文本不贴边
            )
            tooltip_label.pack() # Label会自动适应文本内容大小
            
            # --- 计算并设置提示窗口的位置 ---
            tooltip_window_instance.update_idletasks() # 确保窗口尺寸已计算完毕
            
            widget_root_x = target_widget.winfo_rootx() # 目标控件左上角X坐标 (屏幕绝对坐标)
            widget_root_y = target_widget.winfo_rooty() # 目标控件左上角Y坐标
            widget_height = target_widget.winfo_height()  # 目标控件高度
            widget_width = target_widget.winfo_width()    # 目标控件宽度
            
            tooltip_width = tooltip_window_instance.winfo_width() # 提示窗口宽度
            tooltip_height = tooltip_window_instance.winfo_height()# 提示窗口高度
            
            # 默认将提示窗口置于目标控件下方，并水平居中对齐
            tooltip_pos_x = widget_root_x + (widget_width - tooltip_width) // 2
            tooltip_pos_y = widget_root_y + widget_height + 6 # 在控件下方留出一点间隙 (6像素)
            
            # 获取屏幕尺寸，以防止提示窗口超出屏幕边界
            screen_total_width = self.root.winfo_screenwidth()
            screen_total_height = self.root.winfo_screenheight()
            
            # 调整X坐标，防止超出屏幕左右边界
            if tooltip_pos_x + tooltip_width > screen_total_width: # 如果右边界超出
                tooltip_pos_x = screen_total_width - tooltip_width - 5 # 靠右对齐，并留5像素边距
            if tooltip_pos_x < 0: # 如果左边界超出
                tooltip_pos_x = 5 # 靠左对齐，并留5像素边距
            
            # 调整Y坐标，如果下方空间不足，则尝试在目标控件上方显示
            if tooltip_pos_y + tooltip_height > screen_total_height: # 如果下边界超出
                tooltip_pos_y = widget_root_y - tooltip_height - 6 # 移到控件上方，并留6像素间隙
            if tooltip_pos_y < 0: # 如果上方也超出（例如控件非常靠上且提示很高）
                tooltip_pos_y = widget_root_y + widget_height + 6 # 迫不得已还是放下方（可能部分被遮挡）

            tooltip_window_instance.wm_geometry(f"+{tooltip_pos_x}+{tooltip_pos_y}") # 设置窗口位置
            tooltip_window_instance.attributes("-topmost", True) # 确保提示窗口在最顶层显示

        def _hide_tooltip_on_mouse_leave(event_details=None): # event参数可选，方便直接调用
            """鼠标移开控件区域或控件被点击时触发，销毁工具提示窗口。"""
            nonlocal tooltip_window_instance
            if tooltip_window_instance:
                try:
                    if tooltip_window_instance.winfo_exists(): # 再次检查，防止重复销毁
                        tooltip_window_instance.destroy()
                except tk.TclError: # 组件可能已被Tkinter层销毁
                    pass 
                tooltip_window_instance = None # 重置实例变量
        
        # 为目标控件绑定鼠标进入和移开事件
        target_widget.bind("<Enter>", _show_tooltip_on_mouse_enter, add="+") # add="+" 确保不覆盖控件已有的其他绑定
        target_widget.bind("<Leave>", _hide_tooltip_on_mouse_leave, add="+")
        # 当鼠标点击控件时，也隐藏提示（可选，但通常是好的用户体验）
        target_widget.bind("<Button-1>", lambda event: _hide_tooltip_on_mouse_leave(), add="+")

    # --- 文件/目录浏览方法 (增强版：包含项目根目录处理，并确保对话框父窗口) ---

    def browse_script(self):
        """
        (UI回调) 用户点击“浏览”按钮选择Python主脚本文件。
        选择后，如果应用名称为空，则自动填充；如果项目根目录为空，则自动设为脚本所在目录。
        """
        # 中文注释: 打开文件选择对话框让用户选择主Python脚本。
        selected_file_path = filedialog.askopenfilename(
            title="请选择您的Python主脚本文件", 
            filetypes=[("Python脚本文件", "*.py;*.pyw"), ("所有文件", "*.*")],
            parent=self.root # 指定父窗口，确保模态和焦点正确
        )
        
        if selected_file_path: # 如果用户成功选择了一个文件
            self.script_path.set(selected_file_path) # 更新Tkinter变量
            self._log_to_terminal(f"✅ 已选择主脚本: {selected_file_path}", "SUCCESS")
            
            # 自动填充应用名称 (如果为空)
            if not self.app_name.get():
                app_name_suggestion = Path(selected_file_path).stem # 使用文件名（不含扩展名）作为建议
                self.app_name.set(app_name_suggestion)
                self._log_to_terminal(f"ℹ️ 应用名称已自动填充为: {app_name_suggestion}", "INFO")
            
            # 自动设置项目根目录 (如果为空)
            if not self.project_root_dir.get():
                project_root_suggestion = str(Path(selected_file_path).parent) # 使用脚本所在目录作为建议
                self.project_root_dir.set(project_root_suggestion)
                self._log_to_terminal(f"ℹ️ 项目根目录已自动设置为脚本所在目录: {project_root_suggestion}", "INFO")
        else:
            self._log_to_terminal("ℹ️ 用户取消了选择主脚本文件。", "INFO")

    def browse_project_root(self):
        """
        (UI回调) 用户点击“浏览”按钮选择项目根目录。
        此目录将用于数据文件/文件夹选择时的相对路径参考。
        """
        # 中文注释: 打开目录选择对话框让用户选择项目的根目录。
        selected_directory_path = filedialog.askdirectory(
            title="请选择您的项目根目录 (用于数据文件相对路径参考)",
            parent=self.root 
        )
        
        if selected_directory_path: # 如果用户成功选择了一个目录
            self.project_root_dir.set(selected_directory_path) # 更新Tkinter变量
            self._log_to_terminal(f"✅ 项目根目录已成功设置为: {selected_directory_path}", "SUCCESS")
        else:
            self._log_to_terminal("ℹ️ 用户取消了选择项目根目录。", "INFO")
            
    def browse_output(self):
        """(UI回调) 用户点击“浏览”按钮选择构建输出目录。"""
        # 中文注释: 打开目录选择对话框让用户选择打包结果的输出位置。
        selected_directory_path = filedialog.askdirectory(
            title="请选择构建输出目录 (例如: dist)",
            parent=self.root
        )
        
        if selected_directory_path:
            self.output_dir.set(selected_directory_path)
            self._log_to_terminal(f"✅ 构建输出目录已成功设置为: {selected_directory_path}", "SUCCESS")
        else:
            self._log_to_terminal("ℹ️ 用户取消了选择构建输出目录。", "INFO")
            
    def browse_icon(self):
        """(UI回调) 用户点击“浏览”按钮选择应用程序的图标文件。"""
        # 中文注释: 打开文件选择对话框让用户选择.ico或.png等格式的图标文件。
        selected_file_path = filedialog.askopenfilename(
            title="请选择应用程序的图标文件", 
            filetypes=[
                ("图标文件", "*.ico"), 
                ("PNG 图片", "*.png"), 
                ("所有支持的图片", "*.ico;*.png"), # 方便用户
                ("所有文件", "*.*")
            ],
            parent=self.root
        )
        
        if selected_file_path:
            # 可以在此添加对文件类型的进一步校验，例如检查扩展名是否真的是.ico或.png
            # 但通常filedialog的filetypes已经做了初步筛选
            self.icon_path.set(selected_file_path)
            self._log_to_terminal(f"✅ 应用程序图标已成功选择: {selected_file_path}", "SUCCESS")
        else:
            self._log_to_terminal("ℹ️ 用户取消了选择应用程序图标文件。", "INFO")
            
    def browse_upx(self):
        """(UI回调) 用户点击“浏览”按钮选择UPX工具所在的目录。"""
        # 中文注释: 打开目录选择对话框让用户指定UPX可执行文件所在的文件夹。
        selected_directory_path = filedialog.askdirectory(
            title="请选择UPX工具所在的目录 (包含upx.exe或upx文件)",
            parent=self.root
        )
        
        if selected_directory_path:
            # (可选) 可以在此校验所选目录下是否真的存在 upx.exe (Windows) 或 upx (其他系统)
            # upx_exe_path = Path(selected_directory_path) / ('upx.exe' if sys.platform == "win32" else 'upx')
            # if not upx_exe_path.is_file():
            #     self.show_warning("UPX未找到", f"在目录 '{selected_directory_path}' 中未找到UPX可执行文件。请确保选择正确的目录。")
            # else:
            #     self.upx_dir.set(selected_directory_path)
            #     self._log_to_terminal(f"✅ UPX工具目录已成功设置为: {selected_directory_path}", "SUCCESS")
            # 为简化，此处直接设置
            self.upx_dir.set(selected_directory_path)
            self._log_to_terminal(f"✅ UPX工具目录已成功设置为: {selected_directory_path}", "SUCCESS")
        else:
            self._log_to_terminal("ℹ️ 用户取消了选择UPX工具目录。", "INFO")

    # --- 数据文件管理 (增强版：使用项目根目录，优化用户体验和路径处理) ---

    def _get_data_source_path_helper(self, dialog_title_str: str, is_folder_selection: bool = False) -> str | None:
        """
        辅助方法：弹出文件或文件夹选择对话框，并优先使用项目根目录作为初始路径。
        Args:
            dialog_title_str (str): 对话框的标题。
            is_folder_selection (bool, optional): True表示选择文件夹，False表示选择文件。默认为False。
        Returns:
            str | None: 用户选择的完整路径字符串，如果用户取消则返回None。
        """
        # 中文注释: 统一的文件/文件夹选择逻辑，如果设置了项目根目录，则默认从那里开始浏览。
        initial_directory_to_show = None
        project_root_path_str = self.project_root_dir.get()
        if project_root_path_str and Path(project_root_path_str).is_dir(): # 确保项目根目录有效
            initial_directory_to_show = project_root_path_str
        
        selected_path = None
        if is_folder_selection:
            selected_path = filedialog.askdirectory(title=dialog_title_str, initialdir=initial_directory_to_show, parent=self.root)
        else:
            selected_path = filedialog.askopenfilename(title=dialog_title_str, initialdir=initial_directory_to_show, parent=self.root)
        
        return selected_path if selected_path else None #确保返回None如果用户取消

    def _generate_relative_path_suggestion(self, absolute_source_path_str: str) -> str:
        """
        辅助方法：如果源路径在项目根目录下，则生成相对于项目根的路径作为建议。
        Args:
            absolute_source_path_str (str): 数据源的绝对路径。
        Returns:
            str: 计算出的相对路径建议字符串，如果无法计算或项目根目录未设置则返回空字符串。
        """
        # 中文注释: 用于在用户添加数据文件/夹时，智能推荐打包后的目标相对路径。
        project_root_path_str = self.project_root_dir.get()
        relative_path_suggestion_str = ""
        if project_root_path_str: # 仅当项目根目录已设置时尝试
            try:
                source_path_obj = Path(absolute_source_path_str)
                project_root_path_obj = Path(project_root_path_str)
                
                # 确保两个路径都是绝对路径以便正确比较和计算相对路径
                if not source_path_obj.is_absolute(): source_path_obj = source_path_obj.resolve()
                if not project_root_path_obj.is_absolute(): project_root_path_obj = project_root_path_obj.resolve()

                if source_path_obj.is_relative_to(project_root_path_obj): # Python 3.9+
                    relative_path_suggestion_str = str(source_path_obj.relative_to(project_root_path_obj))
                # Python < 3.9 的回退（或通用）检查方式：
                elif str(source_path_obj).startswith(str(project_root_path_obj)):
                    relative_path_suggestion_str = os.path.relpath(str(source_path_obj), str(project_root_path_obj))
            except (AttributeError, ValueError, TypeError) as e_relpath: 
                # AttributeError: is_relative_to 可能不存在 (Python < 3.9)
                # ValueError/TypeError: 路径类型或格式问题
                self._log_to_terminal(f"调试: 计算相对路径建议时出错 - {e_relpath}", "DEBUG")
                pass # 计算相对路径失败，静默处理，不提供建议
        return relative_path_suggestion_str

    def add_data_file(self):
        """(UI回调) 添加单个数据文件到打包列表。路径选择会优先从项目根目录开始。"""
        # 中文注释: 用户点击“添加文件”按钮时调用，处理文件选择和目标路径设置。
        selected_file_path_str = self._get_data_source_path_helper(
            "请选择要添加的数据文件 (可从您设置的项目根目录开始浏览)", 
            is_folder_selection=False
        )
        
        if selected_file_path_str: # 如果用户选择了文件
            relative_path_suggestion = self._generate_relative_path_suggestion(selected_file_path_str)
            
            # 构建提示用户的对话框文本
            prompt_message = (
                f"请输入此文件打包后在应用程序内的目标相对路径。\n"
                f"源文件: {Path(selected_file_path_str).name}\n\n"
                f"例如: 'assets/images/{Path(selected_file_path_str).name}' 或直接 'data.json'\n"
            )
            if relative_path_suggestion:
                prompt_message += f"建议的目标路径 (相对于项目根): {relative_path_suggestion}\n"
            prompt_message += "留空或输入 '.' 表示将文件直接放在应用程序的根目录下 (使用原文件名)。"

            # 弹出对话框让用户输入目标路径
            input_dialog = ctk.CTkInputDialog(
                title="设置文件目标路径", 
                text=prompt_message, 
                font=self.font_default # 确保对话框字体与UI一致
            )
            destination_path_input_str = input_dialog.get_input() # 获取用户输入

            if destination_path_input_str is None: # 用户取消了输入对话框
                self._log_to_terminal("ℹ️ 用户取消了设置文件目标路径。", "INFO")
                return

            # 处理用户输入的目标路径
            cleaned_destination_path_str = destination_path_input_str.strip()
            # 如果用户留空或输入'.'，则目标路径是文件名本身（放在根目录）
            # 否则，使用用户输入的值（去除了首尾空格）
            final_destination_in_package = cleaned_destination_path_str if cleaned_destination_path_str and cleaned_destination_path_str != "." else Path(selected_file_path_str).name
            
            # PyInstaller的 --add-data 参数期望源路径是绝对路径
            absolute_source_file_path = str(Path(selected_file_path_str).resolve())
            
            # 构造并添加数据文件条目 (格式：源路径;目标路径)
            data_file_entry_str = f"{absolute_source_file_path}{os.pathsep}{final_destination_in_package}"
            self.add_data_list.append(data_file_entry_str)
            
            self.update_data_textbox() # 更新UI上数据文件列表的显示
            self._log_to_terminal(f"✅ 已添加数据文件: {Path(selected_file_path_str).name}  ➔  打包后路径: {final_destination_in_package}", "SUCCESS")
            
    def add_data_folder(self):
        """(UI回调) 添加整个数据文件夹到打包列表。路径选择会优先从项目根目录开始。"""
        # 中文注释: 用户点击“添加文件夹”按钮时调用，处理文件夹选择和目标路径设置。
        selected_folder_path_str = self._get_data_source_path_helper(
            "请选择要添加的数据文件夹 (可从您设置的项目根目录开始浏览)", 
            is_folder_selection=True
        )
        
        if selected_folder_path_str: # 如果用户选择了文件夹
            relative_path_suggestion = self._generate_relative_path_suggestion(selected_folder_path_str)

            prompt_message = (
                f"请输入此文件夹打包后在应用程序内的目标相对路径。\n"
                f"源文件夹: {Path(selected_folder_path_str).name}\n\n"
                f"例如: 'assets/my_data_folder' 或 'resources'\n"
            )
            if relative_path_suggestion:
                prompt_message += f"建议的目标路径 (相对于项目根): {relative_path_suggestion}\n"
            prompt_message += ("留空表示将此文件夹及其内容原样放在应用程序根目录下 (使用原文件夹名)。\n"
                               "输入 '.' 表示将此文件夹内的所有内容直接合并到应用程序的根目录 (不创建父文件夹)。")
            
            input_dialog = ctk.CTkInputDialog(
                title="设置文件夹目标路径", 
                text=prompt_message, 
                font=self.font_default
            )
            destination_path_input_str = input_dialog.get_input()

            if destination_path_input_str is None: 
                self._log_to_terminal("ℹ️ 用户取消了设置文件夹目标路径。", "INFO")
                return

            cleaned_destination_path_str = destination_path_input_str.strip()
            # 如果用户留空，则目标是原文件夹名 (放在根目录)
            # 如果用户输入'.'，则目标是'.' (表示内容合并到根)
            # 否则，使用用户输入的值
            if not cleaned_destination_path_str: # 用户留空
                final_destination_in_package = Path(selected_folder_path_str).name 
            elif cleaned_destination_path_str == ".":
                final_destination_in_package = "."
            else:
                final_destination_in_package = cleaned_destination_path_str
            
            absolute_source_folder_path = str(Path(selected_folder_path_str).resolve())
            data_folder_entry_str = f"{absolute_source_folder_path}{os.pathsep}{final_destination_in_package}"
            self.add_data_list.append(data_folder_entry_str)
            
            self.update_data_textbox()
            self._log_to_terminal(f"✅ 已添加数据文件夹: {Path(selected_folder_path_str).name}  ➔  打包后路径: {final_destination_in_package}", "SUCCESS")
            
    def clear_data_files(self):
        """(UI回调) 清空已添加的所有数据文件和文件夹列表。"""
        # 中文注释: 移除所有已配置的附加数据项。
        if messagebox.askyesno("确认清空列表", 
                              "您确定要从列表中移除所有已添加的数据文件和文件夹吗？", 
                              icon='warning', parent=self.root):
            self.add_data_list.clear() # 清空内部列表
            self.update_data_textbox() # 更新UI显示
            self._log_to_terminal("🗑️ 数据文件/文件夹列表已成功清空。", "INFO")
            
    def update_data_textbox(self):
        """更新高级设置中显示已添加数据文件/文件夹列表的文本框内容。"""
        # 中文注释: 刷新UI上的列表，显示当前所有配置的附加数据。
        
        # 确保UI组件存在且有效
        if not (hasattr(self, 'data_textbox') and self.data_textbox.winfo_exists()):
            # 如果组件不存在，可能是在UI尚未完全初始化时调用，或者UI已销毁
            # 此时可以记录一个调试信息，但不应继续操作UI
            print("[DEBUG - update_data_textbox]: data_textbox not found or not existing.")
            return

        try:
            self.data_textbox.configure(state="normal") # 临时设置为可编辑
            self.data_textbox.delete("1.0", "end")    # 清空现有内容 (从第一行第一列到末尾)
            
            if not self.add_data_list: # 如果列表为空
                self.data_textbox.insert("1.0", "当前没有添加任何数据文件或文件夹...")
            else:
                # 遍历列表，格式化并插入每个条目
                for index, data_item_str in enumerate(self.add_data_list, 1):
                    try:
                        source_path_str, destination_in_pkg_str = data_item_str.split(os.pathsep, 1)
                        source_path_obj = Path(source_path_str)
                        
                        # 判断是文件还是文件夹，并设置相应图标
                        item_type_icon = "📁" if source_path_obj.is_dir() else "📄"
                        
                        # 显示源路径的文件名/文件夹名
                        source_display_name = source_path_obj.name 
                        
                        # 格式化显示字符串
                        display_entry_str = (
                            f"{index}. {item_type_icon} {source_display_name}\n"
                            f"   源路径: {source_path_str}\n" # (可选)显示完整源路径以供参考
                            f"   打包到 (目标相对路径): {destination_in_pkg_str}\n\n"
                        )
                        self.data_textbox.insert("end", display_entry_str)
                    except ValueError: # 如果split失败 (格式不符)
                        self.data_textbox.insert("end", f"{index}. [格式错误] 无效条目: {data_item_str}\n\n")
                    except Exception as e_format: # 其他可能的格式化错误
                         self.data_textbox.insert("end", f"{index}. [显示错误] 处理条目时出错: {data_item_str} ({e_format})\n\n")
        except tk.TclError as e_tcl:
            print(f"[ERROR - update_data_textbox UI Update]: TclError: {e_tcl}")
        except Exception as e_update_list:
            print(f"[ERROR - update_data_textbox UI Update]: Unexpected error: {e_update_list}")
        finally:
            if hasattr(self, 'data_textbox') and self.data_textbox.winfo_exists():
                 self.data_textbox.configure(state="disabled") # 恢复为只读

    # --- 构建相关方法 (增强版：包含预构建检查、日志缓冲、错误提取和UI状态管理) ---

    def _pre_build_checks(self) -> bool:
        """
        在开始实际构建操作之前，执行一系列的有效性检查和用户提示。
        返回:
            bool: True 如果所有检查通过或用户选择继续，False 如果检查失败且用户选择中止。
        """
        # 中文注释: 构建前的检查，如主脚本是否存在，并对可能的隐藏导入依赖给出警告。
        self._log_to_terminal("ℹ️ 正在执行构建前检查...", "INFO")

        # 1. 检查主脚本路径是否有效
        script_file_path_str = self.script_path.get()
        if not script_file_path_str or not Path(script_file_path_str).is_file(): # Path.is_file() 检查路径是否为文件
            self.show_error("主脚本错误", 
                            f"请首先选择一个有效存在的Python主脚本文件。\n当前路径 '{script_file_path_str}' 无效。")
            self._log_to_terminal("❌ 构建前检查失败：主脚本路径无效或文件不存在。", "ERROR")
            return False
        
        # 2. 检查输出目录是否与脚本或项目根目录冲突 (可选，但有时有用)
        #    例如，避免将输出目录设置在源文件目录中，导致混淆或循环依赖。
        #    (此检查较为复杂，此处简化或省略，具体实现可根据需求添加)

        # 3. 提示潜在缺失的隐藏导入 (基于经验和常见库)
        current_hidden_imports_set = {item.strip() for item in self.hidden_imports.get().split(',') if item.strip()}
        
        # 获取已作为数据文件添加的.py文件名 (不含路径)
        added_python_files_as_data = {
            Path(item.split(os.pathsep)[0]).name.lower() # 转为小写以不区分大小写比较
            for item in self.add_data_list 
            if item.split(os.pathsep)[0].lower().endswith(".py")
        }
        
        # 定义一些常见且PyInstaller有时可能遗漏的第三方库
        # 特别是当这些库在被作为数据添加的脚本(如tools.py, orchestrator.py)中被导入时
        common_third_party_deps_to_warn_about = {
            'requests', 'openai', 'duckduckgo_search', 'tiktoken',
            'numpy', 'pandas', 'matplotlib' 
            # 'PyQt5' # PyQt5比较特殊，如果主应用是Tkinter，一般不应直接打包它
        }
        
        potential_missing_hidden_imports = []
        # 如果用户添加了像 "tools.py" 或 "orchestrator.py" 这样的脚本作为数据文件
        if "tools.py" in added_python_files_as_data or "orchestrator.py" in added_python_files_as_data:
            for lib_name in common_third_party_deps_to_warn_about:
                # 如果这个常用库没有在用户已声明的隐藏导入中，则加入警告列表
                if lib_name not in current_hidden_imports_set:
                    potential_missing_hidden_imports.append(lib_name)
        
        if potential_missing_hidden_imports:
            warning_message = (
                f"检测到您可能添加了包含特定第三方库依赖的Python脚本\n"
                f"(例如: {', '.join(fn for fn in ['tools.py', 'orchestrator.py'] if fn in added_python_files_as_data) or '自定义脚本'}) "
                f"作为数据文件。\n\n"
                f"为了确保打包成功，建议检查以下常用模块是否已在\n"
                f"“高级设置”->“隐藏导入”中声明 (如果它们被间接使用且\n"
                f"PyInstaller可能无法自动发现)：\n\n"
                f"  • {', '.join(potential_missing_hidden_imports)}\n\n"
                f"忽略此警告可能会导致打包后的应用程序因找不到模块而运行失败。\n\n"
                f"是否仍然继续构建？"
            )
            if not messagebox.askyesno("潜在依赖警告", warning_message, icon='warning', parent=self.root):
                self._log_to_terminal("⚠️ 用户在预构建检查后选择中止构建，以检查隐藏导入。", "WARNING")
                return False # 用户选择中止

        self._log_to_terminal("✅ 构建前检查通过。", "SUCCESS")
        return True # 所有检查通过或用户选择继续

    def start_build(self):
        """
        开始构建应用程序的入口方法。
        执行预构建检查，设置UI状态，并启动后台构建线程。
        """
        # 中文注释: 用户点击“开始构建”按钮后调用的方法。
        if self.is_building: # 防止重复点击
            self._log_to_terminal("ℹ️ 当前已有构建任务正在进行中。", "INFO")
            return
        
        # 执行预构建检查
        if not self._pre_build_checks():
            self._reset_build_button_ui_state() # 如果检查不通过，重置UI状态
            return
            
        # 设置状态为“正在构建”
        self.is_building = True
        if hasattr(self, 'build_button') and self.build_button.winfo_exists():
            self.build_button.configure(text="🔄 构建中,请稍候...", state="disabled")
        self.update_status("🟡", "正在构建...") # 更新顶部状态指示器
        
        # 切换到“构建输出”选项卡并清空之前的日志
        if hasattr(self, 'tabview'): self.tabview.set("📱 构建输出") 
        if hasattr(self, 'terminal_textbox') and self.terminal_textbox.winfo_exists():
            self.terminal_textbox.configure(state="normal")
            self.terminal_textbox.delete("0.0", "end") 
            self.terminal_textbox.configure(state="disabled")
        
        # 创建并启动后台线程来执行实际的PyInstaller构建过程
        # daemon=True 确保当主程序退出时，此线程也会被终止
        build_process_thread = threading.Thread(target=self._execute_build_process_in_thread, daemon=True) # 方法名更清晰
        build_process_thread.start()

    def _reset_build_button_ui_state(self):
        """辅助方法：重置构建按钮的文本和状态，并将is_building标志设为False。"""
        # 中文注释: 用于在构建完成、失败或取消后恢复UI的构建按钮状态。
        self.is_building = False # 重置构建状态标志
        
        # 确保UI组件仍然存在再操作
        if hasattr(self,'build_button') and self.build_button.winfo_exists():
            self.build_button.configure(text="🚀 开始构建应用程序", state="normal")
        
        # 如果构建未真正开始或已结束，且顶部状态不是明确的成功/失败，则恢复“系统就绪”
        if hasattr(self, 'status_text') and self.status_text.winfo_exists():
            current_status_msg = self.status_text.cget("text")
            if "构建中..." not in current_status_msg and \
               "构建成功" not in current_status_msg and \
               "构建失败" not in current_status_msg:
                self.update_status("🟢", "系统就绪")


    def _execute_build_process_in_thread(self):
        """
        在单独的后台线程中执行PyInstaller构建命令，并处理其输出和结果。
        此方法不直接操作UI，而是通过 self._log_to_terminal 和 self._update_progress_ui 调度UI更新。
        """
        # 中文注释: 这是实际执行PyInstaller命令的核心逻辑，运行在后台线程。
        
        log_buffer_for_error_analysis = [] # 用于存储完整日志，以便在失败时分析具体错误
        
        # 内部辅助函数，用于同时记录到UI日志文本框和本地日志缓冲区
        def _log_and_buffer_build_output(log_line_str):
            self._log_to_terminal(log_line_str.strip(), "BUILD") # 使用特定级别记录构建日志
            log_buffer_for_error_analysis.append(log_line_str.strip())

        try:
            pyinstaller_command_list = self.generate_command() # 获取根据UI配置生成的命令列表
            
            _log_and_buffer_build_output("🚀 PyInstaller Studio Pro 开始执行构建...")
            _log_and_buffer_build_output(f"🛠️ 完整执行命令: {' '.join(pyinstaller_command_list)}")
            _log_and_buffer_build_output("=" * 80) # 日志分隔线
            
            self._update_progress_ui(0.05, "正在准备PyInstaller环境...") 
            
            # 确定PyInstaller命令的执行工作目录 (通常是主脚本所在的目录)
            script_file_full_path = self.script_path.get()
            command_execution_cwd = str(Path(script_file_full_path).parent) if script_file_full_path else os.getcwd()

            # 启动PyInstaller子进程
            pyinstaller_process = subprocess.Popen(
                pyinstaller_command_list, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, # 将标准错误合并到标准输出
                text=True,                # 以文本模式处理输出
                universal_newlines=True,  # 确保换行符在各平台一致
                encoding='utf-8',         # 指定UTF-8编码
                errors='replace',         # 替换无法解码的字符
                cwd=command_execution_cwd, # 设置工作目录
                # 在Windows上不创建额外的命令行窗口
                creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0) 
            )
            
            # 定义一些用于估算进度的关键词和对应的进度值
            # 这些是基于典型PyInstaller输出的经验值，可能不完全精确
            progress_estimation_keywords = {
                "INFO: PyInstaller:": 0.10, 
                "INFO: Extending PYTHONPATH": 0.15,
                "INFO: Analyzing": 0.20,        # 开始分析依赖
                "INFO: Building PYZ": 0.40,     # 开始构建PYZ压缩包
                "INFO: Building PKG": 0.60,     # 开始构建PKG包
                "INFO: Building EXE": 0.75,     # 开始构建EXE
                "INFO: Appending archive to EXE": 0.90,
                "INFO: Building EXE from EXE-00.toc completed successfully.": 0.98, # EXE构建完成
            }

            # 实时读取并处理PyInstaller的输出
            for output_line_from_pyi in pyinstaller_process.stdout:
                _log_and_buffer_build_output(output_line_from_pyi) # 记录到UI和缓冲区
                
                # 根据输出内容估算并更新进度条
                for keyword, progress_val in progress_estimation_keywords.items():
                    if keyword in output_line_from_pyi:
                        # 尝试提取 "INFO: " 后面的部分作为进度条旁边的状态文本
                        status_text_candidate = output_line_from_pyi.strip()
                        info_prefix = "INFO: "
                        if status_text_candidate.startswith(info_prefix):
                            status_text_candidate = status_text_candidate[len(info_prefix):]
                        
                        self._update_progress_ui(progress_val, status_text_candidate)
            
            pyinstaller_process.wait() # 等待PyInstaller进程执行完毕
            
            # --- 处理构建结果 ---
            if pyinstaller_process.returncode == 0: # 返回码为0表示成功
                self._update_progress_ui(1.0, "构建成功完成！")
                _log_and_buffer_build_output("\n" + "=" * 80)
                _log_and_buffer_build_output("✅ 构建成功完成！")
                
                output_directory_str = self.output_dir.get() or str(Path(command_execution_cwd) / 'dist')
                app_name_final = self.app_name.get() or Path(script_file_full_path).stem
                final_output_location = Path(output_directory_str) / app_name_final
                
                _log_and_buffer_build_output(f"📁 输出文件应位于 (或其子目录内): {final_output_location.resolve()}")
                _log_and_buffer_build_output(f"⏰ 构建完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.update_status("🟢", "构建成功")
                if self.root.winfo_exists(): # 确保主窗口存在再弹窗
                    self.root.after(0, lambda: self.show_success("构建成功", "应用程序已成功构建！"))
            else: # 构建失败
                # 获取当前的进度条值（如果有的话），或者设一个接近完成但未完成的值
                current_progress_val = self.progress_bar.get() if hasattr(self,'progress_bar') and self.progress_bar.winfo_exists() else 0.95
                self._update_progress_ui(current_progress_val, "构建失败") 
                
                _log_and_buffer_build_output("\n" + "=" * 80)
                _log_and_buffer_build_output(f"❌ 构建失败！PyInstaller 返回代码: {pyinstaller_process.returncode}。")
                self.update_status("🔴", "构建失败")
                
                # --- 从日志缓冲区中尝试提取更具体的错误原因 ---
                extracted_error_cause = "未知错误，请仔细查看上面的完整构建日志。" # 默认错误信息
                for log_entry_str in reversed(log_buffer_for_error_analysis): # 从后向前查找错误信息
                    log_entry_lower = log_entry_str.lower() # 转为小写方便匹配
                    if log_entry_str.startswith("ERROR:") or \
                       "modulenotfounderror" in log_entry_lower or \
                       "filenotfounderror" in log_entry_lower or \
                       "importerror" in log_entry_lower:
                        extracted_error_cause = log_entry_str # 使用找到的第一个错误行
                        break 
                    elif "is not empty. please remove all its contents" in log_entry_lower:
                        extracted_error_cause = "目标输出目录非空。请手动清空该目录或其子目录后重试。"
                        break
                
                if self.root.winfo_exists():
                    self.root.after(0, lambda err_cause=extracted_error_cause: self.show_error(
                        "构建失败", 
                        f"应用程序构建过程中发生错误。\n\n"
                        f"可能的主要原因:\n{err_cause}\n\n"
                        f"请查看“构建输出”选项卡中的完整日志以获取详细信息。"
                    ))
                
        except FileNotFoundError as e_pyinstaller_not_found: 
            # 特别处理 PyInstaller 命令本身找不到的情况
            self._log_to_terminal(f"❌ 严重错误: 无法找到 PyInstaller 命令。错误详情: {e_pyinstaller_not_found}", "ERROR")
            self.update_status("🔴", "PyInstaller未找到")
            if self.root.winfo_exists(): 
                self.root.after(0, lambda err=e_pyinstaller_not_found: self.show_error(
                    "PyInstaller命令错误",
                    f"无法执行 PyInstaller: {err}.\n\n请确保 PyInstaller 已正确安装并且其路径已添加到系统的 PATH 环境变量中。")
                )
            self._update_progress_ui(0, "PyInstaller未找到") # 重置进度
        except Exception as e_build_unknown: # 捕获所有其他未预料的异常
            self._log_to_terminal(f"❌ 构建过程中发生未处理的严重异常: {str(e_build_unknown)}", "ERROR")
            import traceback # 导入traceback模块以获取详细的错误堆栈信息
            self._log_to_terminal(traceback.format_exc(), "DEBUG") # 将完整堆栈记录到日志（级别设为DEBUG）
            
            self.update_status("🔴", "构建严重出错")
            current_progress_val_on_exc = self.progress_bar.get() if hasattr(self,'progress_bar') and self.progress_bar.winfo_exists() else 0.90
            self._update_progress_ui(current_progress_val_on_exc, "构建时发生严重错误")
            
            if self.root.winfo_exists():
                self.root.after(0, lambda err_unknown=e_build_unknown: self.show_error(
                    "构建过程异常", f"应用程序构建时发生了一个未预料的严重错误:\n{str(err_unknown)}")
                )
            
        finally:
            # 无论构建成功与否，最终都需要重置UI的构建按钮状态
            self._reset_build_button_ui_state()
        
    # --- UI界面更新与日志记录辅助方法 (规范化，增加winfo_exists检查以增强稳定性) ---

    def _log_to_terminal(self, text_message: str, message_level: str = "INFO"):
        """
        安全地向“构建输出”选项卡中的日志文本框追加文本，并根据级别添加简单前缀。
        此方法设计为可在任何线程中调用，它会将UI更新操作调度到主UI线程。

        Args:
            text_message (str): 要记录到日志的文本消息。
            message_level (str, optional): 消息的级别，用于前缀和可能的未来格式化。
                                         默认为 "INFO"。可选值如 "ERROR", "WARNING", "DEBUG", "SUCCESS"。
        """
        # 中文注释: 统一的日志记录方法，确保在UI线程更新文本框，并添加时间戳和级别指示。

        # 检查日志文本框是否存在且有效，如果UI已关闭或组件未创建，则回退到控制台打印
        if not hasattr(self, 'terminal_textbox') or \
           not self.terminal_textbox.winfo_exists(): # winfo_exists() 检查组件是否还存在于Tkinter层
            
            # UI回退：如果日志文本框不可用，则将消息打印到标准输出
            timestamp_fallback = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp_fallback} {message_level} - UI_LOG_FALLBACK]: {text_message}")
            return

        # 准备在UI线程中执行的更新函数
        def _update_terminal_ui():
            # 在实际更新前再次检查组件是否存在，因为after调用是异步的
            if not (hasattr(self, 'terminal_textbox') and self.terminal_textbox.winfo_exists()):
                return 

            try:
                self.terminal_textbox.configure(state="normal") # 临时设置为可编辑状态
                
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] # 格式: HH:MM:SS.mmm
                level_prefix_map = {
                    "ERROR":   "❌", "WARNING": "⚠️", "SUCCESS": "✅",
                    "DEBUG":   "🐞", "INFO":    "ℹ️", "CMD":     "⚙️",
                    "BUILD":   "🚀" 
                }
                prefix_char = level_prefix_map.get(message_level.upper(), "💬") # 默认为普通消息图标
                
                # 插入带时间戳和级别前缀的日志行
                full_log_line = f"[{timestamp} {prefix_char} {message_level.upper()}]: {str(text_message)}\n"
                self.terminal_textbox.insert("end", full_log_line) 
                
                self.terminal_textbox.see("end") # 自动滚动到日志末尾
            except tk.TclError as e_tcl: # 捕获可能的Tcl错误，例如组件已销毁
                print(f"[ERROR - _log_to_terminal UI Update]: TclError occurred: {e_tcl}")
            except Exception as e_log_update: # 捕获其他未知错误
                print(f"[ERROR - _log_to_terminal UI Update]: Unexpected error: {e_log_update}")
            finally:
                if hasattr(self, 'terminal_textbox') and self.terminal_textbox.winfo_exists():
                     self.terminal_textbox.configure(state="disabled") # 恢复为只读状态
        
        # 确保UI更新操作在主线程中执行
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(0, _update_terminal_ui) 
        else: # 如果根窗口也不存在了，直接控制台打印
            timestamp_fallback = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp_fallback} {message_level.upper()} - ROOT_GONE_LOG]: {text_message}")


    def _update_progress_ui(self, progress_value: float, status_text: str):
        """
        安全地更新构建进度条和进度标签的文本。
        此方法将UI更新操作调度到主UI线程。

        Args:
            progress_value (float): 进度条的新值 (0.0 到 1.0 之间)。
            status_text (str): 要在进度标签上显示的文本。
        """
        # 中文注释: 更新界面上的进度条和相关的状态文本。

        # 检查进度条和标签组件是否存在且有效
        if not (hasattr(self, 'progress_bar') and hasattr(self, 'progress_label') and \
                self.progress_bar.winfo_exists() and self.progress_label.winfo_exists()):
            print(f"[PROGRESS_UI_FALLBACK] Value: {progress_value*100:.0f}%, Status: {status_text}")
            return

        def _update_progress_bar_and_label_ui():
            if not (hasattr(self, 'progress_bar') and hasattr(self, 'progress_label') and \
                    self.progress_bar.winfo_exists() and self.progress_label.winfo_exists()):
                return
            try:
                # 确保进度值在0.0到1.0之间
                clamped_progress_value = max(0.0, min(float(progress_value), 1.0))
                self.progress_bar.set(clamped_progress_value) 
                
                # 更新进度标签文本，并使用预定义的字体
                self.progress_label.configure(text=str(status_text), font=self.font_default_bold) 
            except tk.TclError as e_tcl:
                print(f"[ERROR - _update_progress_ui UI Update]: TclError: {e_tcl}")
            except Exception as e_prog_update:
                print(f"[ERROR - _update_progress_ui UI Update]: Unexpected error: {e_prog_update}")

        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(0, _update_progress_bar_and_label_ui)
        else:
             print(f"[PROGRESS_UI_FALLBACK - ROOT_GONE] Value: {progress_value*100:.0f}%, Status: {status_text}")


    def update_status(self, indicator_symbol: str, status_message_text: str):
        """
        安全地更新应用程序顶部的状态指示器图标和状态文本。
        此方法将UI更新操作调度到主UI线程。

        Args:
            indicator_symbol (str): 要显示的状态图标 (例如 "🟢", "🟡", "🔴", "ℹ️")。
            status_message_text (str): 要显示的状态描述文本。
        """
        # 中文注释: 更新主界面顶部的全局状态指示信息。

        if not (hasattr(self, 'status_indicator') and hasattr(self, 'status_text') and \
                self.status_indicator.winfo_exists() and self.status_text.winfo_exists()):
            print(f"[STATUS_UI_FALLBACK] Indicator: {indicator_symbol}, Message: {status_message_text}")
            return

        def _update_status_indicator_and_text_ui():
            if not (hasattr(self, 'status_indicator') and hasattr(self, 'status_text') and \
                    self.status_indicator.winfo_exists() and self.status_text.winfo_exists()):
                return
            try:
                self.status_indicator.configure(text=str(indicator_symbol))
                self.status_text.configure(text=str(status_message_text)) # 字体已在创建时设置
                
                # 如果当前状态不是“系统就绪”的绿色状态，则确保动画辅助标志被重置
                # 以便在状态恢复到“系统就绪”时，动画可以正确重新开始或保持其循环。
                is_ready_state = (indicator_symbol == "🟢" and status_message_text == "系统就绪")
                if not is_ready_state and hasattr(self, 'status_indicator_alt_color_active'):
                    self.status_indicator_alt_color_active = False 
            except tk.TclError as e_tcl:
                print(f"[ERROR - update_status UI Update]: TclError: {e_tcl}")
            except Exception as e_status_update:
                print(f"[ERROR - update_status UI Update]: Unexpected error: {e_status_update}")

        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(0, _update_status_indicator_and_text_ui)
        else:
            print(f"[STATUS_UI_FALLBACK - ROOT_GONE] Indicator: {indicator_symbol}, Message: {status_message_text}")

    # --- 工具箱功能方法 (增强版) ---

    def clean_build_files(self):
        """(工具箱) 清理构建过程中产生的临时文件和目录。"""
        # 中文注释: 清理 'build', 'dist', '*.spec' 和 '__pycache__' 等。
        self._log_to_terminal("🧹 正在执行清理构建文件操作...")
        
        # 确定清理操作的基础目录，优先使用脚本所在目录，否则使用当前工作目录
        script_file_path = self.script_path.get()
        base_dir_to_clean_from = Path(script_file_path).parent if script_file_path and Path(script_file_path).exists() else Path.cwd()
        self._log_to_terminal(f"   清理基准目录: {base_dir_to_clean_from}")

        paths_to_potentially_clean = [
            base_dir_to_clean_from / 'build', # PyInstaller的build目录
        ]
        # 处理输出目录：如果指定了，则清理指定的；如果未指定，则清理默认的 'dist'
        output_dir_path_str = self.output_dir.get()
        if output_dir_path_str and Path(output_dir_path_str).is_absolute(): # 如果是绝对路径
            # 如果应用名也设置了，目标通常是 output_dir/app_name
            app_name_str = self.app_name.get()
            actual_output_target = Path(output_dir_path_str) / app_name_str if app_name_str else Path(output_dir_path_str)
            paths_to_potentially_clean.append(actual_output_target)
        elif output_dir_path_str: # 如果是相对路径
            actual_output_target = base_dir_to_clean_from / output_dir_path_str
            app_name_str = self.app_name.get()
            if app_name_str : actual_output_target = actual_output_target / app_name_str
            paths_to_potentially_clean.append(actual_output_target)
        else: # 未指定输出目录，使用默认的 dist
            paths_to_potentially_clean.append(base_dir_to_clean_from / 'dist')
        
        # 添加当前基准目录下的所有 .spec 文件
        paths_to_potentially_clean.extend(list(base_dir_to_clean_from.glob('*.spec')))
        # 添加当前基准目录及其子目录下的所有 __pycache__ 目录
        paths_to_potentially_clean.extend(list(base_dir_to_clean_from.rglob('__pycache__')))

        cleaned_items_count = 0
        import shutil # 导入shutil用于删除目录

        for item_to_clean_path in paths_to_potentially_clean:
            if item_to_clean_path.exists(): # 确保路径存在
                try:
                    if item_to_clean_path.is_file():
                        item_to_clean_path.unlink() # 删除文件
                        self._log_to_terminal(f"   已删除文件: {item_to_clean_path}")
                        cleaned_items_count += 1
                    elif item_to_clean_path.is_dir():
                        shutil.rmtree(item_to_clean_path) # 删除目录及其所有内容
                        self._log_to_terminal(f"   已删除目录: {item_to_clean_path}")
                        cleaned_items_count += 1
                except Exception as e_clean:
                    self._log_to_terminal(f"   ⚠️ 清理 '{item_to_clean_path}' 时发生错误: {e_clean}")
        
        if cleaned_items_count > 0:
            self.show_success("清理完成", f"成功清理了 {cleaned_items_count} 个构建相关的文件和/或目录。\n详情请查看日志。")
        else:
            self.show_info("提示", "未找到符合默认清理规则的构建文件或目录。")
        self._log_to_terminal("🧹 清理操作执行完毕。")
            
    def open_output_dir(self):
        """(工具箱) 在系统文件浏览器中打开应用程序的输出目录。"""
        # 中文注释: 根据配置的输出目录和应用名称确定最终路径并打开。
        self._log_to_terminal("📁 正在尝试打开输出目录...")
        
        output_dir_base_str = self.output_dir.get()
        app_name_str = self.app_name.get()
        
        # 确定最终的输出路径
        final_output_path = None
        if output_dir_base_str: # 如果用户指定了distpath
            path_obj = Path(output_dir_base_str)
            if app_name_str: # 如果也指定了应用名，PyInstaller通常会在distpath下创建以应用名命名的子目录
                final_output_path = path_obj / app_name_str
            else: # 只指定了distpath，未指定应用名，则distpath本身是目标
                final_output_path = path_obj
        else: # 用户未指定distpath，使用默认行为
            # 默认distpath是相对于.spec文件所在目录的'dist'文件夹
            # .spec文件通常与主脚本在同一目录，或在PyInstaller执行的CWD下
            script_file_path = self.script_path.get()
            base_for_default_dist = Path(script_file_path).parent if script_file_path and Path(script_file_path).exists() else Path.cwd()
            default_dist_dir = base_for_default_dist / 'dist'
            if app_name_str:
                final_output_path = default_dist_dir / app_name_str
            else: # 如果连应用名也没有，就尝试打开dist目录本身
                final_output_path = default_dist_dir
        
        if final_output_path and final_output_path.exists() and final_output_path.is_dir():
            try:
                self._log_to_terminal(f"   打开路径: {final_output_path.resolve()}")
                if sys.platform == "win32":
                    os.startfile(final_output_path.resolve()) # 使用resolve获取绝对路径
                elif sys.platform == "darwin": # macOS
                    subprocess.run(["open", str(final_output_path.resolve())], check=True)
                else: # Linux and other POSIX
                    subprocess.run(["xdg-open", str(final_output_path.resolve())], check=True)
            except Exception as e_open_dir:
                error_msg = f"无法自动打开目录 '{final_output_path.resolve()}':\n{e_open_dir}"
                self._log_to_terminal(f"   ❌ 打开输出目录失败: {error_msg}")
                self.show_error("打开失败", error_msg)
        else:
            warning_msg = f"输出目录 '{final_output_path if final_output_path else '未知'}' 不存在或不是一个有效的目录。"
            self._log_to_terminal(f"   ⚠️ {warning_msg}")
            self.show_warning("目录无效", warning_msg)
            
    def copy_command(self):
        """(工具箱) 复制当前配置生成的PyInstaller构建命令到系统剪贴板。"""
        # 中文注释: 生成命令字符串并复制，方便用户在终端手动执行或记录。
        self._log_to_terminal("📋 正在准备复制构建命令...")
        if not self.script_path.get(): # 检查主脚本是否已选择
            self.show_error("操作无效", "请先选择一个主脚本并配置好相关参数，才能生成并复制构建命令。")
            return
        try:
            command_list = self.generate_command() # 获取命令列表
            # 为了在命令行中粘贴时能正确处理带空格的路径，给每个参数加上引号（如果需要）
            command_string_parts_for_clipboard = []
            for part_of_command in command_list:
                if " " in part_of_command and not (part_of_command.startswith('"') and part_of_command.endswith('"')):
                    command_string_parts_for_clipboard.append(f'"{part_of_command}"')
                else:
                    command_string_parts_for_clipboard.append(part_of_command)
            final_command_string_for_clipboard = ' '.join(command_string_parts_for_clipboard)
            
            # 清空并添加到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(final_command_string_for_clipboard)
            
            self.show_success("复制成功", "PyInstaller 构建命令已成功复制到剪贴板！")
            self._log_to_terminal(f"   命令已复制: {final_command_string_for_clipboard}")
        except Exception as e_copy_cmd:
            error_msg = f"生成或复制构建命令时发生错误: {str(e_copy_cmd)}"
            self._log_to_terminal(f"   ❌ 复制命令失败: {error_msg}")
            self.show_error("复制失败", error_msg)
            
    def check_dependencies(self):
        """(工具箱) 检查PyInstaller、UPX及常用第三方库的状态，并记录到日志。"""
        # 中文注释: 检查环境依赖，给用户参考。
        self._log_to_terminal("🔍 正在执行依赖环境检查 (增强版)...")
        self._log_to_terminal(f"   🐍 Python 版本: {sys.version.splitlines()[0].strip()}")
        
        # 1. 检查 PyInstaller
        try: 
            result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
            self._log_to_terminal(f"   ✅ PyInstaller: {result.stdout.strip()} (已安装)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log_to_terminal("   ❌ PyInstaller: 未安装或未在系统PATH中找到。")
            self._log_to_terminal("      提示: 您可以尝试通过 'pip install pyinstaller' 命令进行安装。")
            
        # 2. 检查 UPX
        upx_is_enabled_in_config = self.is_upx.get()
        upx_status_config_text = "已在当前配置中启用" if upx_is_enabled_in_config else "已在当前配置中禁用"
        self._log_to_terminal(f"   ℹ️ 检查 UPX (压缩工具，{upx_status_config_text})...")
        
        upx_command_to_try = 'upx' # 默认从PATH查找
        upx_custom_dir_str = self.upx_dir.get()
        if upx_custom_dir_str: # 如果用户指定了UPX目录
            # 构建在Windows和非Windows系统上可能的UPX可执行文件路径
            custom_upx_executable_path = Path(upx_custom_dir_str) / ('upx.exe' if sys.platform == "win32" else 'upx')
            if custom_upx_executable_path.is_file() and os.access(custom_upx_executable_path, os.X_OK):
                upx_command_to_try = str(custom_upx_executable_path)
                self._log_to_terminal(f"      (将尝试从指定目录使用UPX: {upx_command_to_try})")
            else:
                self._log_to_terminal(f"      (警告: 在指定的UPX目录 '{upx_custom_dir_str}' 未找到有效的UPX可执行文件, 将回退尝试从系统PATH调用'upx')")
        try:
            result_upx = subprocess.run([upx_command_to_try, '--version'], capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
            self._log_to_terminal(f"   ✅ UPX: 检测到版本 - {result_upx.stdout.splitlines()[0].strip()}")
            if not upx_is_enabled_in_config:
                self._log_to_terminal("      (提示: 尽管UPX已检测到，但当前配置中UPX压缩已禁用，打包时不会使用。)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log_to_terminal(f"   ❌ UPX: 未找到 (尝试的命令: '{upx_command_to_try}')。")
            if upx_is_enabled_in_config:
                self._log_to_terminal("      (警告: 当前配置中UPX压缩已启用，但未能找到UPX。打包时可能无法进行UPX压缩。)")
        except Exception as e_upx_check: # 其他检查UPX时发生的错误
             self._log_to_terminal(f"   ❌ 检查UPX时发生错误: {e_upx_check}")


        # 3. 检查其他常用第三方库 (提示用户是否需要添加到隐藏导入)
        self._log_to_terminal("   ℹ️ 检查其他常用第三方库 (用于“隐藏导入”建议)...")
        # 基于之前您提供的tools.py和orchestrator.py中可能涉及的库
        common_third_party_libraries_to_check = [
            "requests", "openai", "duckduckgo_search", "tiktoken", 
            "numpy", "pandas", "matplotlib", "Pillow" # Pillow (PIL) 已在引导程序中检查
            # "PyQt5" # 暂时不主动检查PyQt5，因为它引入了复杂性
        ]
        
        found_installed_libraries = []
        potentially_missing_for_hidden_import = []

        for library_name in common_third_party_libraries_to_check:
            try:
                # 尝试导入模块来判断是否已安装且可用
                importlib.import_module(library_name)
                self._log_to_terminal(f"      ✅ {library_name}: 已安装。")
                found_installed_libraries.append(library_name)
            except ImportError:
                self._log_to_terminal(f"      ⚠️ {library_name}: 未安装或无法导入。")
                potentially_missing_for_hidden_import.append(library_name)
        
        # 根据检查结果给出建议
        if potentially_missing_for_hidden_import:
             self._log_to_terminal(f"\n   [重要提示] 如果您的项目间接使用了以下一个或多个未检测到/未安装的库，\n"
                               f"   并且PyInstaller可能未能自动将它们打包，您可能需要：\n"
                               f"     1. 确保这些库已在您的Python环境中正确安装 (例如：pip install ...)。\n"
                               f"     2. 将它们的模块名添加到“高级设置”->“隐藏导入”列表中。\n"
                               f"   可能需要检查的库: {', '.join(potentially_missing_for_hidden_import)}")
        else:
            self._log_to_terminal("      所有列出的常用第三方库均已检测到安装。如果您的项目有其他特殊依赖，仍需手动检查。")
        
        self.show_info("依赖检查完成", 
                       "依赖环境检查已完成（增强版）。\n\n"
                       "请仔细查看“构建输出”选项卡中的日志了解详细信息，特别是关于PyInstaller、UPX以及其他可能需要的第三方库的提示。")
        if hasattr(self, 'tabview'): self.tabview.set("📱 构建输出") # 自动切换到输出标签页

    def open_spec_file(self):
        """(工具箱) 在系统默认文本编辑器中打开当前项目生成的.spec文件。"""
        # 中文注释: 方便高级用户直接编辑PyInstaller的配置文件。
        self._log_to_terminal("📝 正在尝试打开 .spec 文件...")
        current_script_path_str = self.script_path.get()
        if not current_script_path_str: # 检查是否已选择主脚本
            self.show_warning("操作无效", "请先选择一个主脚本。\n.spec 文件通常在第一次成功构建后，与主脚本在同一目录生成。")
            return

        # .spec 文件名通常与主脚本名（如果未指定应用名）或 --name 参数指定的应用名相同
        app_name_for_spec_file = self.app_name.get() if self.app_name.get() else Path(current_script_path_str).stem
        # .spec 文件通常生成在主脚本所在的目录
        spec_file_full_path = Path(current_script_path_str).parent / f"{app_name_for_spec_file}.spec"

        if spec_file_full_path.exists() and spec_file_full_path.is_file():
            try:
                self._log_to_terminal(f"   正在打开: {spec_file_full_path}")
                if sys.platform == "win32":
                    os.startfile(spec_file_full_path) # Windows 使用默认程序打开
                elif sys.platform == "darwin": # macOS
                    subprocess.run(["open", str(spec_file_full_path)], check=True)
                else: # Linux and other POSIX systems
                    subprocess.run(["xdg-open", str(spec_file_full_path)], check=True)
                self.show_info("操作成功", f".spec 文件 ({spec_file_full_path.name})\n应已在您的系统默认文本编辑器中打开。")
            except Exception as e_open_spec:
                error_msg = f"无法自动打开 .spec 文件: {spec_file_full_path}\n错误详情: {e_open_spec}"
                self._log_to_terminal(f"   ❌ 打开 .spec 文件失败: {error_msg}")
                self.show_error("打开 .spec 文件失败", f"{error_msg}\n\n请尝试手动导航到该路径并打开文件。")
        else:
            log_msg_spec_not_found = f"   ⚠️ .spec 文件未找到于预期路径: {spec_file_full_path}。"
            self._log_to_terminal(log_msg_spec_not_found)
            self.show_warning(".spec 文件未找到",
                              f"{log_msg_spec_not_found}\n\n"
                              "请确保您已为当前选择的主脚本和应用名称成功执行过至少一次构建操作，"
                              "PyInstaller 通常在此时生成 .spec 文件。")

    def open_docs(self):
        """(工具箱) 在默认网页浏览器中打开PyInstaller官方文档网站。"""
        # 中文注释: 提供快速访问官方文档的入口。
        docs_url = "https://pyinstaller.readthedocs.io/en/stable/"
        try:
            webbrowser.open(docs_url)
            self._log_to_terminal(f"📖 已在浏览器中尝试打开PyInstaller官方文档: {docs_url}")
        except Exception as e_open_docs:
            self._log_to_terminal(f"❌ 打开官方文档失败: {e_open_docs}")
            self.show_error("打开文档失败", f"无法自动打开浏览器访问文档。\n请尝试手动访问：{docs_url}")
        
    def show_about(self):
        """(工具箱) 显示“关于本软件”的信息对话框。"""
        # 中文注释: 展示软件版本、作者等信息。
        about_dialog_text = f"""PyInstaller Studio Pro v3.1 (代码整理与健壮性增强)

🚀 下一代Python应用打包工具 (基于CustomTkinter)

主要特性:
• ✨ 现代化的用户界面 (Material Design 风格)
• 📦 对 PyInstaller 核心功能的全面图形化支持
     - 项目根目录设置，方便管理数据文件相对路径
     - 增强的依赖项检查与智能提示 (针对隐藏导入)
• 💾 智能配置管理 (支持自动保存和加载用户配置)
• 📊 实时构建进度显示和详细的构建日志输出
     - 构建失败时尝试提取关键错误信息
• 🛠️ 实用的集成工具箱，包括：
     - 构建文件清理
     - 快速打开输出目录或 .spec 文件 (高级用户)
     - 一键复制生成的PyInstaller构建命令
     - 界面主题切换 (明亮/深色)
• 🔗 依赖项自动检查与安装引导 (针对核心GUI库和PyInstaller本身)


作者: 跳舞的火公子

"""
        # 使用一个CTkToplevel来显示“关于”信息，以保持UI风格的统一性
        about_dialog_top_level = ctk.CTkToplevel(self.root)
        about_dialog_top_level.title("关于 PyInstaller Studio Pro")
        about_dialog_top_level.geometry("620x480") # 调整对话框大小以适应更多内容
        about_dialog_top_level.transient(self.root) # 使其成为主窗口的瞬态窗口
        about_dialog_top_level.grab_set() # 实现模态对话框效果，阻止与主窗口交互

        about_text_area = ctk.CTkTextbox(about_dialog_top_level, font=self.font_default, wrap="word", activate_scrollbars=True)
        about_text_area.pack(fill="both", expand=True, padx=15, pady=(15,10))
        about_text_area.insert("0.0", about_dialog_text) # 插入文本内容
        about_text_area.configure(state="disabled") # 设置为只读

        close_button = ctk.CTkButton(about_dialog_top_level, text="确定关闭", command=about_dialog_top_level.destroy, width=120, font=self.font_button)
        close_button.pack(pady=(0,15)) # 底部按钮的边距
        
        # 确保对话框在所有其他窗口之上，并获得焦点
        about_dialog_top_level.after(100, about_dialog_top_level.lift) 
        about_dialog_top_level.after(150, about_dialog_top_level.focus_set)
        
    def toggle_theme(self):
        """(工具箱) 在明亮模式和深色界面主题之间进行切换。"""
        # 中文注释: 一键切换UI的明暗风格。
        current_theme_mode = ctk.get_appearance_mode()
        new_theme_mode = "Light" if current_theme_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme_mode) # 应用新的主题模式
        
        log_message = f"🎨 界面主题已切换到: {'☀️ 明亮模式' if new_theme_mode == 'Light' else '🌙 深色模式'}"
        self._log_to_terminal(log_message)
        self.update_status("🎨" if new_theme_mode == "Light" else "🌙", f"主题已切换为{new_theme_mode}") # 更新状态栏


    # --- 配置管理 (增强版：包含项目根目录处理，增加健壮性) ---

    def _get_config_data_for_saving(self): # 方法名更清晰
        """收集当前所有UI配置项到一个字典中，专用于保存到文件。"""
        # 中文注释: 将界面上的所有配置值收集到一个字典，以便序列化和保存。
        return {
            'app_version_config_saved_with': "3.1", # 新增：记录保存此配置的应用版本
            'project_root_dir': self.project_root_dir.get(), 
            'script_path': self.script_path.get(), 
            'output_dir': self.output_dir.get(),
            'icon_path': self.icon_path.get(), 
            'app_name': self.app_name.get(),
            'is_onefile': self.is_onefile.get(), 
            'is_windowed': self.is_windowed.get(),
            'is_debug': self.is_debug.get(), 
            'is_clean': self.is_clean.get(),
            'is_upx': self.is_upx.get(), 
            'exclude_modules': self.exclude_modules.get(),
            'hidden_imports': self.hidden_imports.get(), 
            'upx_dir': self.upx_dir.get(),
            'add_data_list': self.add_data_list # 直接保存列表
        }

    def _apply_config_data_from_loaded_file(self, loaded_config_data): # 方法名更清晰
        """将从文件加载的配置字典应用到UI控件和内部变量上。"""
        # 中文注释: 将从JSON文件加载的配置数据，安全地设置回界面的各个输入框和变量。
        # 使用 .get(key, default_value) 来安全地获取配置项，防止KeyError
        
        # 记录一下加载的配置版本，用于未来可能的兼容性处理
        loaded_config_version = loaded_config_data.get('app_version_config_saved_with', '未知')
        self._log_to_terminal(f"ℹ️ 正在应用版本 '{loaded_config_version}' 的配置...")

        self.project_root_dir.set(loaded_config_data.get('project_root_dir', ''))
        self.script_path.set(loaded_config_data.get('script_path', ''))
        self.output_dir.set(loaded_config_data.get('output_dir', ''))
        self.icon_path.set(loaded_config_data.get('icon_path', ''))
        self.app_name.set(loaded_config_data.get('app_name', ''))
        
        # 布尔值通常有默认值，确保类型正确
        self.is_onefile.set(bool(loaded_config_data.get('is_onefile', True)))
        self.is_windowed.set(bool(loaded_config_data.get('is_windowed', False)))
        self.is_debug.set(bool(loaded_config_data.get('is_debug', False)))
        self.is_clean.set(bool(loaded_config_data.get('is_clean', True)))
        self.is_upx.set(bool(loaded_config_data.get('is_upx', False)))
        
        self.exclude_modules.set(loaded_config_data.get('exclude_modules', ''))
        self.hidden_imports.set(loaded_config_data.get('hidden_imports', ''))
        self.upx_dir.set(loaded_config_data.get('upx_dir', ''))
        
        # add_data_list 应为一个列表
        loaded_data_list = loaded_config_data.get('add_data_list', [])
        if isinstance(loaded_data_list, list):
            self.add_data_list = loaded_data_list
        else:
            self.add_data_list = [] # 如果格式不对，则重置为空列表
            self._log_to_terminal("⚠️ 配置文件中的 'add_data_list' 格式不正确，已重置。")
            
        self.update_data_textbox() # 更新UI上数据文件列表的显示

    def save_config(self, show_success_message_box=False): 
        """
        保存当前配置到应用程序默认的自动保存文件路径。
        Args:
            show_success_message_box (bool): 是否在成功保存后弹出消息框提示用户。
        """
        # 中文注释: 将当前所有UI配置保存到用户目录下的特定JSON文件，通常在程序退出或用户点击“保存”时调用。
        config_data_to_save = self._get_config_data_for_saving() # 获取要保存的数据
        
        # 定义配置文件保存的目录和文件名 (版本化)
        config_directory = Path.home() / '.pyinstaller_studio_pro_v3_1' 
        config_directory.mkdir(parents=True, exist_ok=True) # 确保目录存在
        config_file_path = config_directory / 'autosave_config_v3_1.json'
        
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data_to_save, f, indent=2, ensure_ascii=False) # indent美化JSON输出
            self._log_to_terminal(f"💾 配置已自动保存到: {config_file_path}")
            if show_success_message_box: # 仅当显式要求时才弹窗
                self.show_success("保存成功", f"配置已成功保存到:\n{config_file_path}")
        except IOError as e_io: # 更具体的IO错误捕获
            self._log_to_terminal(f"❌ 自动保存配置时发生IO错误: {e_io}")
            print(f"Error saving config (IOError): {e_io}") # 打印到控制台供调试
            if show_success_message_box: 
                self.show_error("保存失败", f"无法写入配置文件 (IO错误):\n{e_io}")
        except Exception as e_general: # 捕获其他可能的错误
            self._log_to_terminal(f"❌ 自动保存配置时发生未知错误: {e_general}")
            print(f"Error saving config (General): {e_general}")
            if show_success_message_box: 
                self.show_error("保存失败", f"保存配置时发生未知错误:\n{e_general}")
            
    def save_config_file(self): 
        """
        通过文件对话框，允许用户选择路径并将当前配置保存到指定的JSON文件。
        这是“另存为”的功能。
        """
        # 中文注释: 弹出文件保存对话框，让用户选择保存配置文件的位置和名称。
        file_path_to_save_as = filedialog.asksaveasfilename(
            title="选择配置保存路径", 
            defaultextension=".json", # 默认文件扩展名
            filetypes=[("JSON配置文件", "*.json"), ("所有文件", "*.*")],
            parent=self.root #确保对话框是主窗口的模态子窗口
        )
        
        if file_path_to_save_as: # 如果用户选择了路径并没有取消
            config_data_to_save = self._get_config_data_for_saving()
            try:
                with open(file_path_to_save_as, 'w', encoding='utf-8') as f:
                    json.dump(config_data_to_save, f, indent=2, ensure_ascii=False)
                self.show_success("保存成功", f"配置已成功保存到:\n{file_path_to_save_as}")
                self._log_to_terminal(f"💾 配置已通过“另存为”保存到: {file_path_to_save_as}")
            except IOError as e_io:
                self.show_error("保存失败", f"无法将配置写入文件 '{Path(file_path_to_save_as).name}' (IO错误):\n{e_io}")
            except Exception as e_general:
                self.show_error("保存失败", f"保存配置文件时发生未知错误:\n{e_general}")
                
    def load_config_file(self, file_path_to_load_from=None): 
        """
        从用户选择的或指定的JSON文件加载配置，并应用到UI。
        Args:
            file_path_to_load_from (str, optional): 要加载的配置文件的完整路径。
                                                  如果为None，则会弹出文件选择对话框。
        """
        # 中文注释: 如果未提供文件路径，则弹出文件选择对话框让用户选择。然后读取JSON并应用配置。
        if not file_path_to_load_from: # 如果没有直接提供路径，则让用户选择
            file_path_to_load_from = filedialog.askopenfilename(
                title="选择要加载的配置文件", 
                filetypes=[("JSON配置文件", "*.json"), ("所有文件", "*.*")],
                parent=self.root
            )
        
        if file_path_to_load_from and Path(file_path_to_load_from).exists(): # 确保路径有效且文件存在
            try:
                with open(file_path_to_load_from, 'r', encoding='utf-8') as f:
                    loaded_config_data = json.load(f) # 解析JSON文件
                
                if not isinstance(loaded_config_data, dict): # 确保解析出来的是字典
                    self.show_error("加载失败", f"配置文件 '{Path(file_path_to_load_from).name}' 内容格式不正确 (非JSON对象)。")
                    return

                self._apply_config_data_from_loaded_file(loaded_config_data) # 应用配置
                self.show_success("加载成功", f"已从文件成功加载配置:\n{file_path_to_load_from}")
                self._log_to_terminal(f"📂 配置已从文件加载: {file_path_to_load_from}")
            except json.JSONDecodeError as e_json:
                self.show_error("加载失败", f"文件 '{Path(file_path_to_load_from).name}' 不是有效的JSON格式。\n错误: {e_json}")
            except IOError as e_io:
                self.show_error("加载失败", f"读取配置文件时发生IO错误:\n{e_io}")
            except Exception as e_general:
                self.show_error("加载失败", f"加载配置文件时发生未知错误:\n{e_general}")
        elif file_path_to_load_from: # 如果提供了文件名但文件不存在
             self.show_warning("文件未找到", f"无法找到指定的配置文件:\n{file_path_to_load_from}")
                
    def load_config(self): 
        """应用程序启动时，自动加载上次保存的默认配置文件。"""
        # 中文注释: 查找并加载默认的自动保存配置文件。
        config_file_path = Path.home() / '.pyinstaller_studio_pro_v3_1' / 'autosave_config_v3_1.json'
        if config_file_path.exists():
            self._log_to_terminal(f"ℹ️ 正在尝试从 {config_file_path} 加载上次保存的配置...")
            self.load_config_file(file_path_to_load_from=str(config_file_path)) # 调用通用加载方法
        else:
            self._log_to_terminal(f"ℹ️ 未找到上次保存的配置文件 ({config_file_path})。将使用默认设置。")
            # （可选）可以在这里调用 self.reset_config(ask_confirmation=False) 来确保应用一套干净的默认值
            
    def reset_config(self, ask_confirmation_for_reset=True): # 参数名更清晰
        """将所有UI配置项重置为应用程序的初始默认值。"""
        # 中文注释: 重置所有配置为预设的默认状态，通常在用户请求或初始化失败时使用。
        perform_actual_reset = False
        if ask_confirmation_for_reset: # 是否需要弹窗确认
            if messagebox.askyesno("确认重置", 
                                  "您确定要将所有配置项恢复到初始默认值吗？\n此操作不可撤销。", 
                                  icon='question', parent=self.root):
                perform_actual_reset = True
        else: # 无需确认，直接执行重置
            perform_actual_reset = True

        if perform_actual_reset:
            # 定义一套干净的默认配置值
            default_configuration_values = {
                'project_root_dir':'', 
                'script_path': '', 
                'output_dir': '', 
                'icon_path': '', 
                'app_name': '',
                'is_onefile': True, 
                'is_windowed': False,
                'is_debug': False, 
                'is_clean': True,
                'is_upx': False, 
                'exclude_modules': '', 
                'hidden_imports': '', 
                'upx_dir': '',
                'add_data_list': []
            }
            self._apply_config_data_from_loaded_file(default_configuration_values) # 应用这些默认值
            
            if ask_confirmation_for_reset: # 仅在用户主动请求重置时显示成功消息
                self.show_success("重置完成", "所有配置项已成功恢复为默认设置。")
            self._log_to_terminal("🔄 配置已重置为默认值。")

    # --- 消息框封装 (确保parent是self.root，使其成为模态对话框，并进行存在性检查) ---
    def show_success(self, title_str, message_str):
        """显示一个成功信息的消息框。"""
        if hasattr(self, 'root') and self.root.winfo_exists(): # 检查主窗口是否存在
            messagebox.showinfo(title_str, message_str, parent=self.root)
        else:
            print(f"[SUCCESS INFO - UI Fallback] {title_str}: {message_str}") # UI不存在时的回退

    def show_error(self, title_str, message_str):
        """显示一个错误信息的消息框。"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            messagebox.showerror(title_str, message_str, parent=self.root)
        else:
            print(f"[ERROR - UI Fallback] {title_str}: {message_str}")

    def show_warning(self, title_str, message_str):
        """显示一个警告信息的消息框。"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            messagebox.showwarning(title_str, message_str, parent=self.root)
        else:
            print(f"[WARNING - UI Fallback] {title_str}: {message_str}")

    def show_info(self, title_str, message_str):
        """显示一个一般信息的消息框。"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            messagebox.showinfo(title_str, message_str, parent=self.root)
        else:
            print(f"[INFO - UI Fallback] {title_str}: {message_str}")

    def on_closing(self): # 确保 on_closing 方法在 run 方法之前定义
        # ... (您的 on_closing 实现) ...
        self.status_animation_on = False; self.save_config(show_success_message_box=False) 
        if self.root.winfo_exists(): self.root.destroy()

    def run(self):
        """
        启动并运行Tkinter主事件循环。
        此方法会绑定窗口关闭事件和一些全局快捷键。
        """
        # 中文注释: 这是应用程序的启动入口，负责显示窗口并处理事件。

        # 确保主窗口存在
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            self._log_to_terminal("❌ 错误：无法启动GUI，主窗口对象不存在。", "ERROR")
            # 也可以在这里尝试更优雅地退出或显示错误
            # messagebox.showerror("严重错误", "应用程序主窗口未能正确初始化，无法启动。") # 如果messagebox可用
            print("严重错误: 应用程序主窗口未能正确初始化，无法启动。") # 控制台回退
            return

        # 绑定窗口关闭事件到 self.on_closing 方法
        # 当用户点击窗口的关闭按钮时，会调用 self.on_closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) 
        
        # --- 定义并绑定全局快捷键 ---
        try:
            # Ctrl+S: 弹出“另存为”对话框保存当前配置
            self.root.bind("<Control-s>", lambda event: self.save_config_file())      
            # Ctrl+Alt+S: 快速保存当前配置到默认路径
            self.root.bind("<Control-Alt-s>", lambda event: self.save_config(show_success_message_box=True))   
            # Ctrl+O: 弹出“打开文件”对话框加载配置
            self.root.bind("<Control-o>", lambda event: self.load_config_file())      
            # Ctrl+Enter: 如果当前未在构建，则开始构建
            self.root.bind("<Control-Return>", lambda event: self.start_build() if not self.is_building else None) 
            # F1: 显示“关于本软件”对话框
            self.root.bind("<F1>", lambda event: self.show_about())                    
            # F5: 执行“检查依赖环境”工具
            self.root.bind("<F5>", lambda event: self.check_dependencies())            
            
            self._log_to_terminal("ℹ️ 全局快捷键已成功绑定。", "INFO")
        except Exception as e_bind_keys:
            # 如果绑定快捷键时发生错误（虽然不常见），记录下来但不中断程序启动
            self._log_to_terminal(f"⚠️ 绑定全局快捷键时发生错误: {e_bind_keys}", "WARNING")

        # 启动Tkinter的主事件循环
        # 程序将在此处暂停，等待用户交互和事件发生
        self._log_to_terminal("ℹ️ 应用程序图形界面已准备就绪，正在启动主事件循环...", "INFO")
        self.root.mainloop()



# --- 主程序入口与依赖检查 ---

def _main_install_pyinstaller_if_needed():
    """
    (主程序启动时调用) 检查系统中是否已安装PyInstaller。
    如果未安装，则提示用户是否立即使用pip尝试安装。
    返回:
        bool: True 如果PyInstaller已安装或成功安装提示已给出，False 如果用户拒绝安装或安装失败。
    """
    # 这里需要 logging 模块，确保它在使用前已被导入 (在 main 函数中导入)
    logger = logging.getLogger(__name__) # 获取此函数的logger (如果希望与main的logger区分)
                                        # 或者直接使用在main中配置好的根logger (通过logging.info等)
    logger.info("🔎 正在检查 PyInstaller 是否已安装...")
    try:
        # 尝试运行 'pyinstaller --version' 命令来判断是否已安装且可用
        result = subprocess.run(
            ['pyinstaller', '--version'], 
            capture_output=True, text=True, check=True, 
            encoding='utf-8', errors='ignore'
        )
        logger.info(f"✅ PyInstaller 已找到: {result.stdout.strip()}")
        return True # PyInstaller已安装
    except (subprocess.CalledProcessError, FileNotFoundError):
        # PyInstaller命令执行失败或未找到，说明未安装或未在PATH中
        logger.warning("⚠️ PyInstaller 未安装或未在系统PATH中。")
        
        # 提示用户是否安装
        user_choice = input("是否立即尝试使用pip安装 PyInstaller (这是打包所必需的)? (y/n): ").strip().lower()
        if user_choice == 'y':
            logger.info("用户选择安装PyInstaller，正在尝试...")
            print("正在尝试安装 PyInstaller，请稍候...") # 给用户即时反馈
            try:
                python_exe = sys.executable # 获取当前Python解释器路径
                # 在Windows上，如果当前是pythonw.exe，尝试用python.exe执行pip以看到输出
                if sys.platform == "win32" and "pythonw.exe" in python_exe.lower():
                    python_console_exe = python_exe.lower().replace("pythonw.exe", "python.exe")
                    if Path(python_console_exe).exists(): # 确保 python.exe 存在
                        python_exe = python_console_exe

                # 执行pip安装命令，不捕获输出，让用户直接在控制台看到pip的安装过程
                subprocess.run([python_exe, "-m", "pip", "install", "pyinstaller"], check=True) 
                
                logger.info("✅ PyInstaller 安装命令已成功执行。")
                print("\n✅ PyInstaller 安装命令已执行。")
                print("   为了确保新安装的 PyInstaller 能够被正确识别，请您手动重新运行本程序。")
                input("按回车键退出后，请重新启动 PyInstaller Studio Pro。")
                sys.exit(0) # 正常退出，提示用户重启
            except subprocess.CalledProcessError as e_pip_install:
                logger.error(f"❌ PyInstaller 安装过程中发生错误 (pip返回非零): {e_pip_install}")
                print(f"\n❌ PyInstaller 安装失败 (pip命令执行出错)。错误详情请查看上述pip输出。")
                print("   请尝试手动在您的Python环境中运行命令: pip install pyinstaller")
                return False # 安装失败
            except Exception as e_pip_unknown: # 捕获其他可能的安装错误
                logger.error(f"❌ PyInstaller 安装过程中发生未知错误: {e_pip_unknown}", exc_info=True)
                print(f"\n❌ PyInstaller 安装时发生未知错误: {e_pip_unknown}")
                print("   请尝试手动在您的Python环境中运行命令: pip install pyinstaller")
                return False # 安装失败
        else:
            # 用户选择不安装
            logger.info("❌ 用户取消安装PyInstaller。")
            print("用户已取消PyInstaller的安装。请注意，没有PyInstaller将无法执行核心的打包功能。")
            return False # 用户拒绝安装
    except Exception as e_check_pyi: # 捕获检查PyInstaller版本时可能发生的其他错误
        logger.error(f"检查PyInstaller版本时发生意外错误: {e_check_pyi}", exc_info=True)
        print(f"检查PyInstaller状态时发生错误: {e_check_pyi}。假定未安装。")
        return False # 检查出错，保守处理为未安装

def main():
    """主函数：初始化日志、检查依赖并启动应用程序GUI。"""
    import logging # <--- 在这里或更早导入 logging 模块
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO, # 日志级别
        format='%(asctime)s - %(name)s [%(levelname)s] (%(threadName)s) %(module)s.%(funcName)s: %(message)s', # 日志格式
        handlers=[
            logging.StreamHandler(sys.stdout), # 日志输出到控制台
            logging.FileHandler("pyinstaller_studio_pro_v3_1.log", encoding='utf-8', mode='a') # 日志追加到文件
        ]
    )
    main_logger = logging.getLogger() # 获取根logger

    main_logger.info("🚀 正在启动 PyInstaller Studio Pro (增强版 v3.1)...")
    
    # 检查PyInstaller是否已安装，并在需要时提示用户安装
    if not _main_install_pyinstaller_if_needed():
        main_logger.warning("PyInstaller 未安装或安装失败。应用程序的构建功能将不可用，但配置界面仍可尝试使用。")

    # 尝试创建并运行应用程序主GUI
    try:
        app = UltraModernPyInstallerGUI() # 创建GUI实例
        app.run() # 启动GUI主循环
    except tk.TclError as e_tcl: # 捕获Tkinter/Tcl相关的底层GUI错误
        main_logger.critical(f"启动GUI时发生Tcl错误: {e_tcl}", exc_info=True)
        error_details_lower = str(e_tcl).lower()
        user_friendly_message = f"启动图形界面时发生Tcl错误: {e_tcl}\n\n"
        
        if "image" in error_details_lower and ("no such file" in error_details_lower or "doesn't exist" in error_details_lower):
             user_friendly_message += "可能原因：应用程序图标文件 (icon.ico) 未找到或路径不正确。\n请确保 'icon.ico' 与脚本在同一目录，或检查其有效性。"
        elif "font" in error_details_lower:
             user_friendly_message += "可能原因：系统字体配置问题或所需字体缺失。\n请检查系统字体或尝试更新Tk/Tcl库。"
        else:
            user_friendly_message += "这通常与图形界面的底层库 (Tk/Tcl) 有关。请检查您的Python环境和依赖项。"
        
        print(user_friendly_message) 
        try:
            messagebox.showerror("GUI启动严重错误", user_friendly_message) 
        except Exception: 
            pass 
        input("按回车键退出...") 
    except Exception as e_main_fatal: 
        main_logger.critical(f"启动GUI时发生未处理的严重错误: {e_main_fatal}", exc_info=True)
        
        error_message_for_user = (f"应用程序启动失败，发生严重错误：\n\n"
                                  f"错误类型： {type(e_main_fatal).__name__}\n"
                                  f"错误信息： {str(e_main_fatal)}\n\n"
                                  f"详细错误信息已记录到日志文件和控制台。\n"
                                  f"请查看 'pyinstaller_studio_pro_v3_1.log' 获取技术细节。")
        
        print(error_message_for_user) 
        import traceback
        traceback.print_exc() 

        try:
            messagebox.showerror("应用程序启动失败", error_message_for_user) 
        except Exception:
            pass
        input("按回车键退出...") 
    
    main_logger.info("👋 PyInstaller Studio Pro 应用程序已关闭。")

if __name__ == "__main__":
    main()