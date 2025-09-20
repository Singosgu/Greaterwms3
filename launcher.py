import os
from time import sleep
import uvicorn
import socket
import webbrowser
import threading
from bomiot_token import encrypt_info
from os.path import join, exists 
from os import getcwd
import tkinter as tk
from PIL import Image, ImageTk
import requests

app_name = "Bomiot"
version = "1.0.1"

if __name__ == "__main__":
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
                response = requests.get(url=baseurl + '/test/', timeout=1)
                print(response.status_code)
                if response.status_code == 200:
                    print("服务器尚未准备好，正在重试...")
                    sleep(1)
                    webbrowser.open(baseurl)
                    break
                else:
                    print("服务器尚未准备好，正在重试...")
                    sleep(1)
                    continue
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
            proxy_headers=True,
            http="httptools",
            server_header=False,
            limit_concurrency=1000,
            backlog=128,
            timeout_keep_alive=5,
            timeout_graceful_shutdown=30,
            loop="auto",
        )
    
    
    