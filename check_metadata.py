#!/usr/bin/env python3
"""
检查TUF元数据文件是否存在
"""

import os
from pathlib import Path

def check_metadata_files():
    """检查元数据文件"""
    metadata_dir = Path("updates/metadata")
    
    # 检查必要的文件
    required_files = [
        "root.json",
        "1.root.json",
        "2.root.json",
        "snapshot.json",
        "targets.json",
        "timestamp.json"
    ]
    
    print("检查TUF元数据文件...")
    all_files_exist = True
    
    for filename in required_files:
        file_path = metadata_dir / filename
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"  ✓ {filename} 存在 ({file_size} bytes)")
        else:
            print(f"  ✗ {filename} 不存在")
            all_files_exist = False
    
    if all_files_exist:
        print("\n🎉 所有必需的TUF元数据文件都已生成!")
        return True
    else:
        print("\n❌ 缺少必要的TUF元数据文件!")
        return False

if __name__ == "__main__":
    check_metadata_files()