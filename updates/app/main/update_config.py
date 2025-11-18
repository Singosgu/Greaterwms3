"""
Bomiot 更新配置文件
"""

import os
import json
import platform
from pathlib import Path

# 本地路径配置
BASE_DIR = Path(__file__).parent.parent
UPDATE_DIR = BASE_DIR / "updates"
CACHE_DIR = BASE_DIR / "cache"
BACKUP_DIR = CACHE_DIR / "backups"

# 动态更新服务器地址配置文件路径
DYNAMIC_UPDATE_CONFIG_FILE = CACHE_DIR / "dynamic_update_config.json"

# 创建必要的目录
for directory in [UPDATE_DIR, CACHE_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 获取当前平台
def get_platform_name():
    """获取当前平台名称"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'mac'
    elif system == 'linux':
        return 'linux'
    else:
        return 'windows'  # 默认为Windows

CURRENT_PLATFORM = get_platform_name()

# 从 server_config.json 读取配置
SERVER_CONFIG_FILE = BASE_DIR / "main" / "server_config.json"
APP_NAME = "Bomiot"
CURRENT_VERSION = "1.1.1"
UPDATE_SERVER_URL = "http://3.135.61.8:8008/media/"

try:
    if SERVER_CONFIG_FILE.exists():
        with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            server_config = json.load(f)
            APP_NAME = server_config.get('app_name', APP_NAME)
            CURRENT_VERSION = server_config.get('current_version', CURRENT_VERSION)
            
            # 根据平台获取特定的更新服务器URL
            platform_specific_urls = server_config.get('platform_specific_urls', {})
            if CURRENT_PLATFORM in platform_specific_urls:
                UPDATE_SERVER_URL = platform_specific_urls[CURRENT_PLATFORM]
            else:
                # 如果没有平台特定的URL，则使用通用URL
                UPDATE_SERVER_URL = server_config.get('update_server_url', UPDATE_SERVER_URL)
except Exception as e:
    print(f"读取 server_config.json 时出错: {e}")

# 更新服务器配置
UPDATE_SERVER_URL = os.getenv("BOMIOT_UPDATE_URL", UPDATE_SERVER_URL)
UPDATE_CHECK_INTERVAL = int(os.getenv("BOMIOT_UPDATE_INTERVAL", "360"))  # 默认1小时检查一次

# 更新策略配置
ENABLE_AUTO_UPDATE = os.getenv("BOMIOT_AUTO_UPDATE", "true").lower() == "true"
ENABLE_INCREMENTAL_UPDATE = os.getenv("BOMIOT_INCREMENTAL_UPDATE", "true").lower() == "true"
ENABLE_FILE_WATCHER = os.getenv("BOMIOT_FILE_WATCHER", "false").lower() == "true"

# 安全配置
VERIFY_UPDATE_SIGNATURE = os.getenv("BOMIOT_VERIFY_SIGNATURE", "true").lower() == "true"
VERIFY_UPDATE_HASH = os.getenv("BOMIOT_VERIFY_HASH", "true").lower() == "true"

# 网络配置
REQUEST_TIMEOUT = int(os.getenv("BOMIOT_REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("BOMIOT_MAX_RETRIES", "3"))

# 日志配置
LOG_LEVEL = os.getenv("BOMIOT_LOG_LEVEL", "INFO")
LOG_FILE = CACHE_DIR / "update.log"