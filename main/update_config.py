"""
Bomiot 更新配置文件
"""

import os
from pathlib import Path

# 应用信息
APP_NAME = "bomiot"
CURRENT_VERSION = "0.0.1"

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

# 更新服务器配置
UPDATE_SERVER_URL = os.getenv("BOMIOT_UPDATE_URL", "http://3.135.61.8:8008/media/")
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