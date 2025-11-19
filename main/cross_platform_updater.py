"""
跨平台自动更新支持模块
提供统一的接口来处理不同操作系统的更新和重启操作
"""

import os
import sys
import platform
import subprocess
import logging
import json
from pathlib import Path


logger = logging.getLogger(__name__)

class CrossPlatformUpdater:
    """跨平台更新器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_macos = False  # 移除Mac支持
        self.is_linux = False  # 移除Linux支持
        
        # 设置平台名称
        if self.is_windows:
            self.platform_name = 'windows'
        else:
            self.platform_name = 'windows'  # 默认为Windows
            
    def get_platform_info(self) -> dict:
        """获取平台信息"""
        return {
            'system': self.system,
            'is_windows': self.is_windows,
            'is_macos': self.is_macos,
            'is_linux': self.is_linux,
            'platform_name': self.platform_name,
            'platform_details': platform.platform()
        }
    
    def get_platform_specific_url(self, base_url: str) -> str:
        """
        获取平台特定的更新服务器URL
        
        Args:
            base_url: 基础URL
            
        Returns:
            str: 平台特定的URL
        """
        # 从server_config.json读取平台特定的URL
        try:
            from main.update_config import SERVER_CONFIG_FILE
            if SERVER_CONFIG_FILE.exists():
                with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    server_config = json.load(f)
                    platform_specific_urls = server_config.get('platform_specific_urls', {})
                    if self.platform_name in platform_specific_urls:
                        return platform_specific_urls[self.platform_name]
        except Exception as e:
            logger.error(f"读取平台特定URL时出错: {e}")
        
        # 如果没有找到平台特定的URL，则返回基础URL加上平台路径
        if not base_url.endswith('/'):
            base_url += '/'
        return f"{base_url}{self.platform_name}/"
    
    def restart_application(self) -> bool:
        """
        跨平台重启应用程序
        
        Returns:
            bool: 重启是否成功启动
        """
        try:
            logger.info(f"正在重启应用程序 (平台: {self.system})")
            
            if self.is_windows:
                return self._restart_windows()
            else:
                # 默认重启方式
                return self._restart_default()
                
        except Exception as e:
            logger.error(f"重启应用程序时出错: {e}")
            return False
    
    def _restart_windows(self) -> bool:
        """Windows平台重启"""
        try:
            # Windows使用标准的subprocess方式
            subprocess.Popen([sys.executable] + sys.argv)
            logger.info("Windows平台重启命令已执行")
            return True
        except Exception as e:
            logger.error(f"Windows平台重启失败: {e}")
            return False
    
    def _restart_default(self) -> bool:
        """默认重启方式"""
        try:
            subprocess.Popen([sys.executable] + sys.argv)
            logger.info("默认平台重启命令已执行")
            return True
        except Exception as e:
            logger.error(f"默认平台重启失败: {e}")
            return False
    
    def create_platform_specific_scripts(self, app_dir: Path) -> bool:
        """
        创建平台特定的更新脚本
        
        Args:
            app_dir: 应用程序目录
            
        Returns:
            bool: 脚本创建是否成功
        """
        try:
            if self.is_windows:
                self._create_windows_scripts(app_dir)
            
            logger.info(f"平台特定脚本创建完成 ({self.system})")
            return True
        except Exception as e:
            logger.error(f"创建平台特定脚本时出错: {e}")
            return False
    
    def _create_windows_scripts(self, app_dir: Path):
        """创建Windows脚本"""
        # 创建批处理文件用于更新
        update_script = app_dir / "update.bat"
        update_content = f'''@echo off
REM Bomiot Windows 更新脚本
cd /d "{app_dir}"
echo 正在更新应用程序...
REM 这里可以添加具体的更新命令
echo 更新完成
REM 重启应用程序
"{sys.executable}" {" ".join(sys.argv)}
'''
        update_script.write_text(update_content, encoding='utf-8')
        logger.info(f"Windows更新脚本已创建: {update_script}")
    
    def get_update_file_extension(self) -> str:
        """获取平台特定的更新文件扩展名"""
        if self.is_windows:
            return ".zip"
        else:
            return ".zip"
    
    def get_temp_directory(self) -> Path:
        """获取平台特定的临时目录"""
        if self.is_windows:
            return Path(os.environ.get('TEMP', '/tmp'))
        else:
            return Path('/tmp')

# 全局实例
cross_platform_updater = CrossPlatformUpdater()

def restart_application():
    """重启应用程序的便捷函数"""
    return cross_platform_updater.restart_application()

def get_platform_info():
    """获取平台信息的便捷函数"""
    return cross_platform_updater.get_platform_info()

def get_platform_specific_url(base_url: str) -> str:
    """获取平台特定URL的便捷函数"""
    return cross_platform_updater.get_platform_specific_url(base_url)