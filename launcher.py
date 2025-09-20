import os
from time import sleep
import sys
import uvicorn
import time
import socket
import webbrowser
import threading
from bomiot_token import encrypt_info
from bomiot.cmd.killport import kill_process_on_port
from os.path import join, exists 
from os import getcwd
import platform
import importlib.resources
from pathlib import Path
from configparser import ConfigParser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from tufup.client import Client

app_name = "Bomiot"
version = "1.0.1"

def get_update_server_url():
    """根据操作系统返回不同的更新 URL"""
    system = platform.system()
    base_url = "http://3.135.61.8:8008/media/update/"
    if system == 'Windows':
        return f"{base_url}releases/windows/"
    elif system == 'Darwin':  # macOS
        return f"{base_url}releases/macos/"
    elif system == 'Linux':
        return f"{base_url}releases/linux/"
    else:
        raise ValueError(f"Unsupported operating system: {system}")

def progress_callback(progress_bar, status_label, total_bytes, downloaded_bytes):
    if total_bytes > 0:
        percent = int(downloaded_bytes * 100 / total_bytes)
        progress_bar['value'] = percent
        status_label.config(text=f"下载中: {percent}% ({downloaded_bytes}/{total_bytes} bytes)")
        progress_bar.update()
        status_label.update()

def run_update(progress_bar, status_label):
    try:
        status_label.config(text="正在检查更新...")
        # 获取应用安装目录（打包后可执行文件所在目录）
        if getattr(sys, 'frozen', False):
            # 打包后的环境（如 Nuitka 生成的可执行文件）
            app_install_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境（脚本运行目录）
            app_install_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 更新目标目录（通常与安装目录相同）
        target_dir = app_install_dir
        metadata_dir = os.path.join(app_install_dir, 'metadata')

        # 获取特定于当前系统的更新 URL
        target_base_url = get_update_server_url()
        metadata_base_url = "http://3.135.61.8:8008/media/update/metadata/"
        
        # 实例化 tufup 客户端（补充必填参数）
        client = Client(
            app_name=app_name,              # 应用名称
            app_install_dir=app_install_dir,  # 应用安装目录
            target_dir=target_dir,            # 更新目标目录
            current_version=version,          # 当前应用版本（需确保 bomiot.version 存在且格式正确）
            metadata_dir=metadata_dir,
            metadata_base_url=metadata_base_url,
            target_base_url=target_base_url
        )
        
        # 检查更新并执行（根据 tufup 文档补充更新逻辑）
        update_available = client.check_for_updates()
        if update_available:
            status_label.config(text="发现更新，正在下载并安装...")
            # 传递一个 lambda 函数作为回调，将进度条和标签传递进去
            result = client.update(progress=lambda total, downloaded: progress_callback(progress_bar, status_label, total, downloaded))
            if result:
                new_version = result.get('new_version')
                status_label.config(text=f"更新成功！已更新到版本：{new_version}")
                print(f"\n更新成功！已更新到版本：{new_version}")
                print("请重新启动应用程序以应用更新。")
                return True
            else:
                status_label.config(text="没有可用的新版本。")
                print("\n没有可用的新版本。")
                return False
        else:
            status_label.config(text="当前已是最新版本。")
            print("当前已是最新版本")
            return False

    except Exception as e:
        status_label.config(text=f"自动更新失败：{e}")
        print(f"自动更新失败：{e}")
        return False


if __name__ == "__main__":
    # ================== 自动更新逻辑 ==================
    update_root = tk.Tk()
    update_root.title("自动更新中...")
    window_width = 400
    window_height = 120
    screen_width = update_root.winfo_screenwidth()
    screen_height = update_root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    update_root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    update_root.overrideredirect(True)  # 无边框显示
    update_root.resizable(False, False)

    status_label = tk.Label(update_root, text="正在初始化...", pady=10)
    status_label.pack()

    progress_bar = ttk.Progressbar(update_root, orient="horizontal", length=350, mode="determinate")
    progress_bar.pack(pady=5)

    # 启动一个新线程来执行更新任务，以免阻塞 UI
    update_thread = threading.Thread(target=lambda: run_update(progress_bar, status_label), daemon=True)
    update_thread.start()

    # 等待更新线程完成
    while update_thread.is_alive():
        update_root.update()
        time.sleep(0.1)

    needs_restart = run_update(progress_bar, status_label)
    
    # 销毁更新窗口
    update_root.destroy()

    # 如果更新成功，退出当前进程以允许外部脚本或用户重启
    print('是否更新成功', needs_restart)
    if needs_restart:
        print("更新完成，正在重启...")
        os.execv(sys.executable, ['python'] + sys.argv)
    
    # 欢迎页
    splash = tk.Tk()
    window_width = 675
    window_height = 329
    x = int(splash.winfo_screenwidth() / 2 - window_width / 2)
    y = int(splash.winfo_screenheight() / 2 - window_height / 2)
    canvas = tk.Canvas(splash, width=window_width, height=window_height, bg='white', highlightthickness=0)
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
    from django.contrib.auth import get_user_model

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
                response = requests.get(url=baseurl, timeout=1)
                print(response.status_code)
                sleep(1)
                webbrowser.open(baseurl)
                break 
            except requests.exceptions.ReadTimeout:
                print("服务器尚未准备好，正在重试...")
                sleep(1)
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
            proxy_headers="store_true",
            http="httptools",
            server_header=False,
            limit_concurrency=1000,
            backlog=128,
            timeout_keep_alive=5,
            timeout_graceful_shutdown=30,
            loop="auto",
        )
    
    
    