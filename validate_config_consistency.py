#!/usr/bin/env python3
"""
验证配置文件一致性
"""

import json
from pathlib import Path

def validate_config_consistency():
    """验证配置文件一致性"""
    print("=== 验证配置文件一致性 ===")
    
    # 读取 server_config.json
    server_config_path = Path('main/server_config.json')
    if not server_config_path.exists():
        print("错误: server_config.json 文件不存在")
        return False
    
    with open(server_config_path, 'r', encoding='utf-8') as f:
        server_config = json.load(f)
    
    server_app_name = server_config.get('app_name')
    server_version = server_config.get('current_version')
    
    print(f"server_config.json 应用名: {server_app_name}")
    print(f"server_config.json 版本: {server_version}")
    
    # 读取 .tufup-repo-config
    tufup_config_path = Path('.tufup-repo-config')
    if not tufup_config_path.exists():
        print("错误: .tufup-repo-config 文件不存在")
        return False
    
    with open(tufup_config_path, 'r', encoding='utf-8') as f:
        tufup_config = json.load(f)
    
    tufup_app_name = tufup_config.get('app_name')
    
    print(f".tufup-repo-config 应用名: {tufup_app_name}")
    
    # 验证应用名一致性
    if server_app_name != tufup_app_name:
        print(f"警告: 应用名不一致! server_config.json: {server_app_name}, .tufup-repo-config: {tufup_app_name}")
        return False
    
    print("✓ 配置文件一致性验证通过")
    return True

if __name__ == "__main__":
    if validate_config_consistency():
        print("\n🎉 配置文件一致性验证成功!")
    else:
        print("\n❌ 配置文件一致性验证失败!")
        exit(1)