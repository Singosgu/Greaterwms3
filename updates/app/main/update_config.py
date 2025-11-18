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

# 从server_config.json读取配置
try:
    if SERVER_CONFIG_FILE.exists():
        with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            server_config = json.load(f)
            APP_NAME = server_config.get('app_name')
            CURRENT_VERSION = server_config.get('current_version')
            
            # 根据平台获取特定的更新服务器URL
            platform_specific_urls = server_config.get('platform_specific_urls', {})
            if CURRENT_PLATFORM in platform_specific_urls:
                UPDATE_SERVER_URL = platform_specific_urls[CURRENT_PLATFORM]
            else:
                # 如果没有平台特定的URL，则使用通用URL
                UPDATE_SERVER_URL = server_config.get('update_server_url')
            
            # 获取更新检查间隔（秒）
            UPDATE_CHECK_INTERVAL = server_config.get('update_check_interval')
    else:
        # 如果配置文件不存在，设置为None
        APP_NAME = None
        CURRENT_VERSION = None
        UPDATE_SERVER_URL = None
        UPDATE_CHECK_INTERVAL = None
        print("警告: server_config.json 文件不存在")

except Exception as e:
    print(f"读取 server_config.json 时出错: {e}")
    # 出错时设置为None
    APP_NAME = None
    CURRENT_VERSION = None
    UPDATE_SERVER_URL = None
    UPDATE_CHECK_INTERVAL = None

# 允许环境变量覆盖配置值
env_update_url = os.getenv("BOMIOT_UPDATE_URL")
if env_update_url:
    UPDATE_SERVER_URL = env_update_url

env_update_interval = os.getenv("BOMIOT_UPDATE_INTERVAL")
if env_update_interval:
    UPDATE_CHECK_INTERVAL = int(env_update_interval)

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

# 环境变量说明:
# BOMIOT_UPDATE_URL: 更新服务器URL
# BOMIOT_UPDATE_INTERVAL: 更新检查间隔（秒），默认3600秒（1小时）
# BOMIOT_AUTO_UPDATE: 是否启用自动更新，默认true
# BOMIOT_INCREMENTAL_UPDATE: 是否启用增量更新，默认true
# BOMIOT_FILE_WATCHER: 是否启用文件监控，默认false
# BOMIOT_VERIFY_SIGNATURE: 是否验证更新签名，默认true
# BOMIOT_VERIFY_HASH: 是否验证更新哈希，默认true
# BOMIOT_REQUEST_TIMEOUT: 请求超时时间（秒），默认30秒
# BOMIOT_MAX_RETRIES: 最大重试次数，默认3次
# BOMIOT_LOG_LEVEL: 日志级别，默认INFO
