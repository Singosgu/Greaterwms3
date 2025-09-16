import os
from time import sleep
import sys
import os
import uvicorn
import time
from bomiot import version
import socket
import webbrowser
from bomiot_token import encrypt_info
from bomiot.cmd.killport import kill_process_on_port
from os.path import join, exists 
from os import getcwd
import platform
import importlib.resources
from os.path import join
from pathlib import Path
from configparser import ConfigParser
from update import run_update



if __name__ == "__main__":
    # ... 生成 auth_key.py 和 workspace.ini 的代码 ...
    
    # ================== 自动更新逻辑 ==================
    # 运行更新检查
    needs_restart = run_update()
    
    # 如果更新成功，退出当前进程以允许外部脚本或用户重启
    print('是否更新成功', needs_restart)
    if needs_restart:
        sys.exit(0)
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
        f.close()

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

    # 初始化管理员
    User = get_user_model()

    try:
        User.objects.get(username='admin', is_superuser=True)
        print('Admin user already exists, you can use admin to login:')
    except:
        username = 'admin'
        email = f'{username}@bomiot.com'
        password = username
        admin, created = User.objects.update_or_create(email=email, username=username)
        admin.set_password(password)
        admin.is_active = True
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        print('%s admin account: %s(%s), initial password: %s, just use it temporarily '
              'and change the password for safety' % \
              ('Created' if created else 'Reset', username, email, password))
        
    # 启动 Django 开发服务器
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    baseurl = "http://" + ip + ":8008"
    webbrowser.open(baseurl)