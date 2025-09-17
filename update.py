import platform
import sys
import os
from tufup.client import Client
from bomiot import version  # 导入当前应用版本

app_name = "Bomiot"

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

def run_update():
    try:
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
            current_version='1.0.0',          # 当前应用版本（需确保 bomiot.version 存在且格式正确）
            metadata_dir=metadata_dir,
            metadata_base_url=metadata_base_url,
            target_base_url=target_base_url
        )
        
        # 检查更新并执行（根据 tufup 文档补充更新逻辑）
        update_available = client.check_for_updates()
        if update_available:
            print("发现更新，正在下载并安装...")
            client.download_and_apply_update()
            return True  # 表示需要重启应用
        else:
            print("当前已是最新版本")
            return False

    except Exception as e:
        print(f"自动更新失败：{e}")
        return False