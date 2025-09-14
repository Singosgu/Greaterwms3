import os
from time import sleep

if __name__ == "__main__":
    # 设置 Django 环境变量
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bomiot.server.server.settings")
    os.environ.setdefault("RUN_MAIN", "true")

    # 初始化 Django
    import django
    django.setup()

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
    sleep(20000000)