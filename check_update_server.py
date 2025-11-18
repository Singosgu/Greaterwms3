#!/usr/bin/env python3
"""
检查更新服务器状态
"""

import requests
import json
from urllib.parse import urljoin

def check_update_server():
    """检查更新服务器状态"""
    base_url = "http://3.135.61.8:8008/media/update/win/"
    
    # 检查元数据文件
    metadata_files = ["root.json", "targets.json", "snapshot.json", "timestamp.json"]
    
    print(f"使用更新服务器地址: {base_url}")
    print("正在检查元数据文件...")
    
    for file_name in metadata_files:
        url = urljoin(base_url, f"metadata/{file_name}")
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✓ {file_name} - 可访问")
            else:
                print(f"  ✗ {file_name} - HTTP {response.status_code}")
        except Exception as e:
            print(f"  ✗ {file_name} - 错误: {e}")
    
    # 检查targets.json内容
    print("\n正在检查targets.json内容...")
    try:
        targets_url = urljoin(base_url, "metadata/targets.json")
        response = requests.get(targets_url, timeout=10)
        if response.status_code == 200:
            targets_data = response.json()
            targets = targets_data.get('signed', {}).get('targets', {})
            if targets:
                print(f"  发现 {len(targets)} 个目标文件:")
                for target_name, target_info in targets.items():
                    print(f"    - {target_name}")
            else:
                print("  targets.json中没有目标文件")
        else:
            print(f"  无法获取targets.json: HTTP {response.status_code}")
    except Exception as e:
        print(f"  检查targets.json时出错: {e}")

if __name__ == "__main__":
    check_update_server()