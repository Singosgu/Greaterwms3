import os
import json
from pathlib import Path

# 设置编码环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 读取 server_config.json
server_config_path = Path('main/server_config.json')
if server_config_path.exists():
    with open(server_config_path, 'r', encoding='utf-8') as f:
        server_config = json.load(f)
        server_version = server_config.get('current_version', 'unknown')
        print(f'server_config.json 版本: {server_version}')

# 读取 .tufup-repo-config
tufup_config_path = Path('.tufup-repo-config')
if tufup_config_path.exists():
    with open(tufup_config_path, 'r', encoding='utf-8') as f:
        tufup_config = json.load(f)
        app_name = tufup_config.get('app_name', 'unknown')
        print(f'.tufup-repo-config 应用名: {app_name}')

# 检查环境变量版本
env_version = os.environ.get('BASE_VERSION', 'unknown')
print(f'环境变量版本: {env_version}')

print('配置文件一致性检查完成')