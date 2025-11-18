"""
Bomiot 增量自动更新模块
基于 tufup 确保更新安全性，bsdiff4 减少更新体积，watchdog 实现实时触发
"""

import os
import logging
import shutil
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional
import bsdiff4
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tufup.client import Client


# 导入更新配置
from .update_config import DYNAMIC_UPDATE_CONFIG_FILE, APP_NAME, CURRENT_VERSION

# 导入跨平台更新支持
from .cross_platform_updater import CrossPlatformUpdater

# 导入TUF仓库支持
from tufup.repo import Repository

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 定义常量
CURRENT_DIR = Path(__file__).parent.parent
UPDATE_DIR = CURRENT_DIR / "updates"
CACHE_DIR = CURRENT_DIR / "cache"
METADATA_DIR = UPDATE_DIR / "metadata"
TARGETS_DIR = UPDATE_DIR / "targets"

# 创建必要的目录
for directory in [UPDATE_DIR, CACHE_DIR, METADATA_DIR, TARGETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 创建跨平台更新器实例
cross_platform_updater = CrossPlatformUpdater()


class BomiotUpdater:
    """Bomiot 增量更新器"""

    def __init__(self, app_name: str = APP_NAME, current_version: str = CURRENT_VERSION):
        self.app_name = app_name
        self.current_version = current_version
        self.client = None  # TUF客户端实例
        self.observer = None  # 文件监视器实例
        self.update_available = False
        self.latest_version = current_version
        self.platform_info = cross_platform_updater.get_platform_info()

    def get_dynamic_update_server_url(self, default_url: str) -> str:
        """
        获取动态更新服务器地址
        
        Args:
            default_url: 默认服务器地址
            
        Returns:
            str: 动态服务器地址或默认地址
        """
        try:
            # 首先尝试获取平台特定的URL
            platform_specific_url = self._get_platform_specific_url(default_url)
            
            if DYNAMIC_UPDATE_CONFIG_FILE.exists():
                with open(DYNAMIC_UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    dynamic_url = config.get('update_server_url')
                    if dynamic_url:
                        logger.info(f"使用动态更新服务器地址: {dynamic_url}")
                        return dynamic_url
            # 如果没有动态配置文件，使用平台特定的默认地址
            logger.info(f"使用平台特定的更新服务器地址: {platform_specific_url}")
            return platform_specific_url
        except Exception as e:
            logger.error(f"读取动态更新配置时出错: {e}")
            return default_url
    
    def _get_platform_specific_url(self, base_url: str) -> str:
        """
        获取平台特定的更新服务器URL
        
        Args:
            base_url: 基础URL
            
        Returns:
            str: 平台特定的URL
        """
        try:
            # 使用跨平台更新器获取平台特定的URL
            return cross_platform_updater.get_platform_specific_url(base_url)
        except Exception as e:
            logger.error(f"获取平台特定URL时出错: {e}")
            # 如果无法获取平台特定的URL，则返回基础URL加上平台路径
            if not base_url.endswith('/'):
                base_url += '/'
            return f"{base_url}{self.platform_info['platform_name']}/"

    def save_dynamic_update_server_url(self, new_url: str, app_name: Optional[str] = None, current_version: Optional[str] = None):
        """
        保存动态更新服务器地址和应用信息
        
        Args:
            new_url: 新的服务器地址
            app_name: 应用名称（可选）
            current_version: 当前版本号（可选）
        """
        try:
            # 读取现有配置（如果存在）
            config = {}
            if DYNAMIC_UPDATE_CONFIG_FILE.exists():
                with open(DYNAMIC_UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 更新配置
            config['update_server_url'] = new_url
            if app_name is not None:
                config['app_name'] = app_name
            if current_version is not None:
                config['current_version'] = current_version
                
            with open(DYNAMIC_UPDATE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"动态更新配置已保存: {new_url}")
        except Exception as e:
            logger.error(f"保存动态更新配置时出错: {e}")

    def initialize_client(self, repository_url: str) -> bool:
        """
        初始化 TUF 客户端
        
        Args:
            repository_url: 更新仓库的 URL
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 确保 repository_url 以斜杠结尾
            if not repository_url.endswith('/'):
                repository_url += '/'
                
            self.client = Client(
                app_name=self.app_name,
                app_install_dir=CURRENT_DIR,
                current_version=self.current_version,
                metadata_dir=METADATA_DIR,
                metadata_base_url=repository_url + "metadata/",
                target_dir=TARGETS_DIR,
                target_base_url=repository_url + "targets/",
                refresh_required=False,
            )
            logger.info("TUF 客户端初始化成功")
            return True
        except Exception as e:
            logger.error(f"TUF 客户端初始化失败: {e}")
            return False

    def check_for_updates(self) -> bool:
        """
        检查是否有可用更新
        
        Returns:
            bool: 是否有可用更新
        """
        if not self.client:
            logger.error("客户端未初始化")
            return False

        try:
            # 刷新元数据
            self.client.refresh()
            
            # 检查更新
            if self.client.updates_available:
                self.update_available = True
                # 注意：latest_version将在下载更新时确定
                logger.info("发现新版本可用")
                return True
            else:
                logger.info("当前已是最新版本")
                return False
        except Exception as e:
            logger.error(f"检查更新时出错: {e}")
            return False

    def download_update(self, target_name: str) -> Optional[Path]:
        """
        下载更新包
        
        Args:
            target_name: 目标文件名
            
        Returns:
            Path: 下载文件的路径，如果失败则返回 None
        """
        if not self.client:
            logger.error("客户端未初始化")
            return None

        try:
            # 获取目标文件信息
            target_info = self.client.get_targetinfo(target_name)
            if not target_info:
                logger.error(f"未找到目标文件: {target_name}")
                return None
            
            # 下载目标文件
            target_path_str = self.client.download_target(target_info)
            if target_path_str:
                target_path = Path(target_path_str)
                if target_path.exists():
                    logger.info(f"更新包下载成功: {target_path}")
                    return target_path
                else:
                    logger.error("更新包下载失败")
                    return None
            else:
                logger.error("更新包下载失败")
                return None
        except Exception as e:
            logger.error(f"下载更新包时出错: {e}")
            return None

    def verify_update_integrity(self, file_path: Path, expected_hash: str) -> bool:
        """
        验证更新包完整性
        
        Args:
            file_path: 文件路径
            expected_hash: 预期的 SHA256 哈希值
            
        Returns:
            bool: 验证是否通过
        """
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            if file_hash.lower() == expected_hash.lower():
                logger.info("更新包完整性验证通过")
                return True
            else:
                logger.error("更新包完整性验证失败")
                return False
        except Exception as e:
            logger.error(f"验证更新包完整性时出错: {e}")
            return False

    def apply_incremental_update(self, old_file: Path, patch_file: Path, new_file: Path) -> bool:
        """
        应用增量更新补丁
        
        Args:
            old_file: 旧文件路径
            patch_file: 补丁文件路径
            new_file: 新文件路径
            
        Returns:
            bool: 应用是否成功
        """
        try:
            # 读取旧文件和补丁
            with open(old_file, "rb") as f:
                old_data = f.read()
            
            with open(patch_file, "rb") as f:
                patch_data = f.read()
            
            # 应用补丁
            new_data = bsdiff4.patch(old_data, patch_data)
            
            # 写入新文件
            with open(new_file, "wb") as f:
                f.write(new_data)
            
            logger.info("增量更新应用成功")
            return True
        except Exception as e:
            logger.error(f"应用增量更新时出错: {e}")
            return False

    def backup_current_version(self, backup_dir: Path) -> bool:
        """
        备份当前版本
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            bool: 备份是否成功
        """
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份主要文件和目录
            items_to_backup = [
                "launcher.py",
                "main",
                "requirements.txt",
                # 可以根据需要添加更多需要备份的文件
            ]
            
            for item in items_to_backup:
                src = CURRENT_DIR / item
                dst = backup_dir / item
                
                if src.exists():
                    if src.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            logger.info(f"当前版本已备份到: {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"备份当前版本时出错: {e}")
            return False

    def install_update(self, update_file: Path) -> bool:
        """
        安装更新
        
        Args:
            update_file: 更新文件路径
            
        Returns:
            bool: 安装是否成功
        """
        try:
            # 创建备份
            backup_dir = CACHE_DIR / f"backup_{self.current_version}"
            if not self.backup_current_version(backup_dir):
                logger.error("创建备份失败，取消更新")
                return False
            
            # 解压更新包（假设是 zip 格式）
            import zipfile
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(CURRENT_DIR)
            
            logger.info("更新安装成功")
            return True
        except Exception as e:
            logger.error(f"安装更新时出错: {e}")
            return False

    def rollback_update(self) -> bool:
        """
        回滚更新
        
        Returns:
            bool: 回滚是否成功
        """
        try:
            backup_dir = CACHE_DIR / f"backup_{self.current_version}"
            if not backup_dir.exists():
                logger.error("未找到备份目录，无法回滚")
                return False
            
            # 恢复备份的文件
            for item in backup_dir.iterdir():
                dst = CURRENT_DIR / item.name
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                
                if item.is_dir():
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)
            
            logger.info("更新回滚成功")
            return True
        except Exception as e:
            logger.error(f"回滚更新时出错: {e}")
            return False

    def start_file_watcher(self, watch_directory: Path = CURRENT_DIR):
        """
        启动文件监视器，实现实时触发更新检查
        
        Args:
            watch_directory: 要监视的目录
        """
        class UpdateEventHandler(FileSystemEventHandler):
            def __init__(self, updater):
                self.updater = updater
            
            def on_modified(self, event):
                if not event.is_directory:
                    # 文件修改时触发更新检查
                    logger.info(f"检测到文件变更: {event.src_path}")
                    self.updater.check_for_updates()
        
        try:
            event_handler = UpdateEventHandler(self)
            self.observer = Observer()
            if self.observer is not None:
                self.observer.schedule(event_handler, str(watch_directory), recursive=True)
                self.observer.start()
            logger.info(f"文件监视器已启动，监视目录: {watch_directory}")
        except Exception as e:
            logger.error(f"启动文件监视器时出错: {e}")

    def stop_file_watcher(self):
        """停止文件监视器"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("文件监视器已停止")

    def auto_update(self, repository_url: str) -> bool:
        """
        自动更新流程
        
        Args:
            repository_url: 更新仓库 URL
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取动态更新服务器地址（如果有的话）
            dynamic_url = self.get_dynamic_update_server_url(repository_url)
            
            # 初始化客户端
            if not self.initialize_client(dynamic_url):
                return False
            
            # 检查更新
            if not self.check_for_updates():
                return False
            
            # 获取目标文件信息
            target_name = None
            try:
                # 尝试从客户端获取目标文件信息
                if self.client is not None:
                    # 使用TUF客户端的API获取目标文件信息
                    # 注意：具体的API可能因tufup版本而异
                    try:
                        # 尝试获取目标文件信息的不同方法
                        if hasattr(self.client, 'get_targetinfo'):
                            # 如果有get_targetinfo方法，我们可以用它来获取信息
                            # 但我们需要知道目标文件名才能调用它
                            pass
                    except:
                        pass
                    
                    # 作为后备方案，使用基于应用名和当前版本的文件名
                    file_extension = cross_platform_updater.get_update_file_extension()
                    target_name = f"{self.app_name}-{self.current_version}{file_extension}"
                    
                    # 检查是否有更新可用，如果有，尝试获取最新版本的目标文件
                    if self.update_available:
                        # 这里我们假设目标文件名遵循一定的命名约定
                        # 在实际应用中，可能需要从元数据中获取确切的文件名
                        target_name = f"{self.app_name}-{self.current_version}{file_extension}"
            except Exception as e:
                logger.warning(f"获取目标文件信息时出错: {e}")
                # 作为后备方案，使用基于应用名和当前版本的文件名
                file_extension = cross_platform_updater.get_update_file_extension()
                target_name = f"{self.app_name}-{self.current_version}{file_extension}"
            
            if not target_name:
                logger.error("未找到目标文件")
                return False
            
            # 下载更新
            update_file = self.download_update(target_name)
            
            if not update_file:
                return False
            
            # 安装更新
            if self.install_update(update_file):
                logger.info("自动更新完成")
                # 检查更新包中是否包含新的服务器地址配置
                self._check_and_update_server_url_from_update(update_file)
                return True
            else:
                # 更新失败，尝试回滚
                self.rollback_update()
                return False
                
        except Exception as e:
            logger.error(f"自动更新过程中出错: {e}")
            return False

    def _check_and_update_server_url_from_update(self, update_file: Path):
        """
        检查更新包中是否包含新的服务器地址配置
        
        Args:
            update_file: 更新文件路径
        """
        try:
            import zipfile
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                # 检查更新包中是否包含服务器配置文件
                server_config_files = [f for f in zip_ref.namelist() if 'server_config.json' in f]
                if server_config_files:
                    # 读取服务器配置文件
                    with zip_ref.open(server_config_files[0]) as config_file:
                        import json
                        config_data = json.load(config_file)
                        new_server_url = config_data.get('update_server_url')
                        new_app_name = config_data.get('app_name')
                        new_version = config_data.get('current_version')
                        
                        if new_server_url:
                            # 保存新的服务器地址和应用信息
                            self.save_dynamic_update_server_url(
                                new_url=new_server_url,
                                app_name=new_app_name,
                                current_version=new_version
                            )
                            logger.info(f"从更新包中获取新的配置: server={new_server_url}, app={new_app_name}, version={new_version}")
        except Exception as e:
            logger.error(f"检查更新包中的服务器配置时出错: {e}")

    def restart_application(self) -> bool:
        """
        重启应用程序（跨平台支持）
        
        Returns:
            bool: 重启是否成功启动
        """
        return cross_platform_updater.restart_application()

    def cleanup(self):
        """清理临时文件"""
        try:
            if CACHE_DIR.exists():
                shutil.rmtree(CACHE_DIR)
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"清理临时文件时出错: {e}")


def create_update_repository(repo_dir: Path, app_name: str = APP_NAME):
    """
    创建更新仓库（供服务器端使用）
    
    Args:
        repo_dir: 仓库目录
        app_name: 应用名称
    """
    try:
        # 创建仓库
        repo = Repository(
            app_name=app_name,
            repo_dir=repo_dir,
            keys_dir=repo_dir / "keys",
        )
        
        # 初始化仓库
        repo.initialize()
        
        logger.info(f"更新仓库创建成功: {repo_dir}")
        return repo
    except Exception as e:
        logger.error(f"创建更新仓库时出错: {e}")
        return None


# 示例用法
if __name__ == "__main__":
    # 创建更新器实例
    updater = BomiotUpdater()
    
    # 示例：检查更新
    # updater.auto_update("http://your-update-server.com/repository")
    
    # 示例：启动文件监视器
    # updater.start_file_watcher()