#!/usr/bin/env python3
"""
验证targets目录中的文件
"""

import os
from pathlib import Path

def verify_targets_files():
    """验证targets目录中的文件"""
    print("=== 验证targets目录中的文件 ===")
    
    # 检查targets目录
    targets_dir = Path("updates/targets")
    if not targets_dir.exists():
        print("错误: targets目录不存在")
        return False
    
    print("targets目录中的文件:")
    files_found = False
    for file in targets_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size
            print(f"  {file.name} ({size} bytes)")
            files_found = True
    
    if not files_found:
        print("  targets目录为空")
        return False
    
    # 检查是否有ZIP文件
    zip_files = list(targets_dir.glob("*.zip"))
    if zip_files:
        print("\n找到以下ZIP文件:")
        for zip_file in zip_files:
            size = zip_file.stat().st_size
            print(f"  {zip_file.name} ({size} bytes)")
        return True
    else:
        print("\n警告: targets目录中没有找到ZIP文件")
        # 检查是否有其他文件
        other_files = [f for f in targets_dir.iterdir() if f.is_file() and not f.name.endswith('.zip')]
        if other_files:
            print("找到以下非ZIP文件:")
            for other_file in other_files:
                size = other_file.stat().st_size
                print(f"  {other_file.name} ({size} bytes)")
        return False

if __name__ == "__main__":
    if verify_targets_files():
        print("\n🎉 targets目录文件验证成功!")
    else:
        print("\n❌ targets目录文件验证失败!")
        exit(1)