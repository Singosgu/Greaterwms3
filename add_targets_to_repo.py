#!/usr/bin/env python3
"""
添加目标文件到TUF仓库
"""

import json
import os
from pathlib import Path
from tufup.repo import Repository

def add_targets_to_repository():
    """添加目标文件到TUF仓库"""
    print("开始添加目标文件到TUF仓库...")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    targets_dir = updates_dir / "targets"
    
    # 检查目录是否存在
    if not updates_dir.exists():
        print("错误: updates目录不存在")
        return False
    
    # 更改当前工作目录到updates目录
    original_cwd = os.getcwd()
    os.chdir(updates_dir)
    
    try:
        # 加载现有仓库配置
        print("加载现有仓库配置...")
        try:
            repo = Repository.from_config()
            print("仓库配置加载成功")
        except Exception as e:
            print(f"仓库配置加载失败: {e}")
            return False
        
        # 创建一个简单的测试文件作为目标
        test_file = targets_dir / "test.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("This is a test file for TUF updates.")
        
        # 添加目标文件
        print("添加目标文件...")
        try:
            # 添加测试文件
            repo.add_bundle(new_bundle_dir=targets_dir.absolute(), new_version="1.0.0")
            print("成功添加目标文件")
        except Exception as e:
            print(f"添加目标文件失败: {e}")
            return False
        
        # 发布更改
        print("发布更改...")
        try:
            repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
            print("TUF仓库更改发布完成!")
            return True
        except Exception as e:
            print(f"发布更改失败: {e}")
            return False
            
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

if __name__ == "__main__":
    success = add_targets_to_repository()
    if success:
        print("\n目标文件添加成功!")
    else:
        print("\n目标文件添加失败!")