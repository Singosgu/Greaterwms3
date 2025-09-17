import platform
import sys
from pathlib import Path
from tufup.client import Client
from os import getcwd


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
        raise ValueError(f"不支持的操作系统: {system}")


def progress_callback(progress: float):
    """更新下载进度回调函数"""
    percentage = int(progress * 100)
    # 简单的进度条显示
    sys.stdout.write(f"\r下载进度: [{'#' * (percentage // 2)}{' ' * (50 - percentage // 2)}] {percentage}%")
    sys.stdout.flush()
    if percentage == 100:
        print("\n下载完成，正在应用更新...")


def run_update() -> bool:
    """
    执行更新检查和应用
    返回值: 是否需要重启应用
    """
    try:
        # 获取当前系统的更新服务器URL
        target_base_url = get_update_server_url()
        metadata_base_url = "http://3.135.61.8:8008/media/update/metadata/"
        
        # 配置更新相关目录（确保存在）
        app_data_dir = Path(getcwd()) / "update_data"
        metadata_dir = app_data_dir / "metadata"
        targets_dir = app_data_dir / "targets"
        app_data_dir.mkdir(exist_ok=True)
        metadata_dir.mkdir(exist_ok=True)
        targets_dir.mkdir(exist_ok=True)

        # 实例化tufup客户端
        client = Client(
            app_name="Bomiot",  # 应用名称，需与服务器端配置一致
            current_version="1.0.0",  # 当前应用版本
            metadata_base_url=metadata_base_url,
            target_base_url=target_base_url,
            metadata_dir=metadata_dir,  # 本地存储元数据的目录
            targets_dir=targets_dir,    # 本地存储更新文件的目录
            verify=True,                # 启用更新验证（安全推荐）
            timeout=30                  # 网络超时时间（秒）
        )

        # 检查是否有可用更新
        print(f"正在检查更新，当前版本: 1.0.0")
        update_info = client.check_for_updates()

        if not update_info:
            print("当前已是最新版本，无需更新")
            return False

        # 显示更新信息
        latest_version = update_info['available_version']
        print(f"发现新版本: {latest_version}")
        if 'release_notes' in update_info:
            print("更新内容:")
            print(update_info['release_notes'])

        # 下载并应用更新
        client.download_and_apply_update(
            progress_callback=progress_callback,
            restart=False  # 不自动重启，由launcher控制
        )

        print(f"更新成功，已升级至版本: {latest_version}")
        return True  # 需要重启

    except Exception as e:
        print(f"\n自动更新失败: {str(e)}")
        return False