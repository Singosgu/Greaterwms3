import os
from time import sleep
import uvicorn
import socket
import webbrowser
import threading
from os.path import join, exists 
from os import getcwd
import tkinter as tk
from PIL import Image, ImageTk
import requests
import json

# 导入统一配置
from main.update_config import APP_NAME as CONFIG_APP_NAME, CURRENT_VERSION as CONFIG_CURRENT_VERSION, UPDATE_SERVER_URL, ENABLE_AUTO_UPDATE

# 使用配置文件中的默认值
APP_NAME = CONFIG_APP_NAME
CURRENT_VERSION = CONFIG_CURRENT_VERSION

# 尝试从动态配置文件中读取应用信息
def load_dynamic_app_info():
    """从动态配置文件中加载应用信息"""
    global APP_NAME, CURRENT_VERSION
    try:
        # 导入更新配置以获取统一的配置文件路径
        from main.update_config import DYNAMIC_UPDATE_CONFIG_FILE
        if DYNAMIC_UPDATE_CONFIG_FILE.exists():
            with open(DYNAMIC_UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'app_name' in config:
                    APP_NAME = config['app_name']
                if 'current_version' in config:
                    CURRENT_VERSION = config['current_version']
    except Exception as e:
        print(f"读取动态配置文件时出错: {e}")

# 在导入更新模块之前加载动态配置
load_dynamic_app_info()

# 导入更新模块
UPDATER_AVAILABLE = False
BomiotUpdater = None
try:
    from main.updater import BomiotUpdater
    UPDATER_AVAILABLE = True
except ImportError:
    print("警告: 更新模块不可用")

# 定义 encrypt_info 函数
def default_encrypt_info():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# 使用默认的加密函数
encrypt_info = default_encrypt_info

def check_and_apply_updates():
    """检查并应用更新"""
    if not UPDATER_AVAILABLE or BomiotUpdater is None:
        return False
    
    try:
        # 创建更新器实例
        updater = BomiotUpdater(APP_NAME, CURRENT_VERSION)
        
        # 获取动态更新服务器地址（如果有的话）
        dynamic_url = updater.get_dynamic_update_server_url(UPDATE_SERVER_URL)
        
        # 如果启用了自动更新，则执行自动更新
        if ENABLE_AUTO_UPDATE:
            print("正在检查更新...")
            success = updater.auto_update(dynamic_url)
            if success:
                print("更新完成，请重启应用程序")
                return True
            else:
                print("无可用更新或更新失败")
                return False
        return False
    except Exception as e:
        print(f"检查更新时出错: {e}")
        return False

if __name__ == "__main__":
    # 检查并应用更新（在欢迎页面显示期间）
    update_applied = check_and_apply_updates()
    if update_applied:
        # 如果应用了更新，自动重启程序
        print("程序已更新，正在自动重启...")
        # 使用跨平台重启功能
        try:
            from main.updater import BomiotUpdater
            updater = BomiotUpdater()
            if updater.restart_application():
                print("重启命令已发送")
            else:
                print("重启失败，使用备用方法")
                # 备用重启方法
                import subprocess
                import sys
                subprocess.Popen([sys.executable] + sys.argv)
        except Exception as e:
            print(f"重启时出错: {e}")
            # 最后的备用重启方法
            import subprocess
            import sys
            subprocess.Popen([sys.executable] + sys.argv)
        exit(0)

    # 欢迎页
    splash = tk.Tk()
    window_width = 675
    window_height = 329
    x = int(splash.winfo_screenwidth() / 2 - window_width / 2)
    y = int(splash.winfo_screenheight() / 2 - window_height / 2)

    canvas = tk.Canvas(splash, width=window_width, height=window_height, highlightthickness=0)
    canvas.configure(bg='')
    splash.wm_attributes('-transparentcolor', '')
    canvas.pack()

    splash.title("Welcome to Bomiot")
    splash.geometry(f'675x329+{x}+{y}')
    splash.overrideredirect(True)  # 无边框显示
    # 加载并缩放图片（保持长宽比）
    try:
        # 使用PIL加载图片
        image_path = join(getcwd(), 'splash.png')
        pil_img = Image.open(image_path)
        
        # 获取原始图片尺寸
        img_width, img_height = pil_img.size
        
        # 计算缩放比例（保持长宽比）
        scale_width = window_width / img_width
        scale_height = window_height / img_height
        scale = min(scale_width, scale_height)  # 取最小比例，确保图片完全显示在窗口内
        
        # 计算缩放后的尺寸
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 缩放图片
        resized_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # 高质量缩放
        img = ImageTk.PhotoImage(resized_img)
        
        # 计算图片居中位置
        x_pos = (window_width - new_width) // 2
        y_pos = (window_height - new_height) // 2
        
        # 在画布上显示图片（居中）
        canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=img)
    except Exception as e:
        print(f"图片加载失败: {e}")
        # 显示错误文本
        canvas.create_text(window_width/2, window_height/2, text="加载图片失败", font=("Arial", 12))

    # 强制刷新窗口，确保splash在后续操作前显示
    splash.update()
    
    # 设置 Django 环境变量
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bomiot.server.server.settings")
    os.environ.setdefault("RUN_MAIN", "true")
    import django
    django.setup()
    
    # 生成auth_key.py
    path = join(getcwd(), 'auth_key.py')
    if not exists(join(path)):
        while True:
            key_code = encrypt_info()
            if '/' in key_code:
                continue
            else:
                break
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'KEY = "{key_code}"\n')

    from django.core.management import call_command
    from django.apps import apps

    # 准备 makemigrations 命令参数
    cmd_args = ["makemigrations"]

    # 自动检测所有包含模型的应用
    apps_with_models = []
    for app_config in apps.get_app_configs():
        try:
            if app_config.models_module:
                models = apps.get_app_config(app_config.label).get_models()
                if models:
                    apps_with_models.append(app_config.label)
        except Exception:
            continue

    if apps_with_models:
        cmd_args.extend(apps_with_models)

    # 执行 makemigrations 命令
    try:
        call_command(*cmd_args)
        print("Migrations created successfully.")
    except Exception as e:
        print(f"Error creating migrations: {e}")
    
    # 执行 migrate 命令
    try:
        call_command('migrate')
    except Exception as e:
        print(f"Error during migration: {e}")
    
    # 保持欢迎页显示一段时间（原逻辑的10秒）
    print('正在启动系统')
    
    # 启动 Django 开发服务器
    os.environ.setdefault("IS_LAN", "true")
    print('系统启动成功')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    print('本机IP地址为:', ip)
    s.close()
    baseurl = "http://" + ip + ":8008"
    print('浏览器正在打开:', baseurl)
    def run_server():
        while True:
            try:
                response = requests.get(url=baseurl, timeout=2)
                print(response.status_code)
                sleep(2)
                webbrowser.open(baseurl)
                break 
            except:
                print("服务器尚未准备好，正在重试...")
                sleep(0.5)
                continue
    run_server_thread = threading.Thread(target=run_server, daemon=True)
    run_server_thread.start()

    # 在启动uvicorn前手动销毁欢迎页
    splash.destroy()

    uvicorn.run(
            "bomiot_asgi:application",
            host='0.0.0.0',
            port=8008,
            workers=1,
            log_level="info",
            uds=None,
            ssl_keyfile=None,
            ssl_certfile=None,
            proxy_headers=True,
            http="httptools",
            server_header=False,
            limit_concurrency=1000,
            backlog=128,
            timeout_keep_alive=5,
            timeout_graceful_shutdown=30,
            loop="auto",
        )