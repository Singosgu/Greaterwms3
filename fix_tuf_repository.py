#!/usr/bin/env python3
"""
修复TUF仓库签名问题
"""

import json
import shutil
from pathlib import Path
from tufup.repo import Repository

def fix_tuf_repository():
    """修复TUF仓库"""
    print("开始修复TUF仓库...")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    targets_dir = updates_dir / "targets"
    
    # 检查是否存在现有仓库
    if not updates_dir.exists():
        print("错误: updates目录不存在")
        return False
    
    if not keys_dir.exists():
        print("错误: keys目录不存在")
        return False
        
    # 检查密钥文件是否存在
    required_keys = ['root', 'snapshot', 'targets', 'timestamp']
    for key_name in required_keys:
        key_file = keys_dir / key_name
        if not key_file.exists():
            print(f"错误: 缺少密钥文件 {key_name}")
            return False
    
    # 从配置文件读取设置
    print("读取配置文件...")
    config_file = Path('.tufup-repo-config')
    if not config_file.exists():
        print("错误: .tufup-repo-config 文件不存在")
        return False
        
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("配置信息:")
    print(f"  应用名称: {config['app_name']}")
    
    # 更改当前工作目录到updates目录，以便Repository.from_config能正确找到配置文件
    import os
    original_cwd = os.getcwd()
    os.chdir(updates_dir)
    
    try:
        # 加载现有仓库配置
        print("加载现有仓库配置...")
        try:
            # 使用from_config类方法加载配置
            repo = Repository.from_config()
            print("仓库配置加载成功")
        except Exception as e:
            print(f"仓库配置加载失败: {e}")
            print("重新初始化仓库...")
            # 如果加载失败，创建新的仓库实例
            repo = Repository(
                app_name=config['app_name'],
                repo_dir=str(updates_dir.absolute()),
                keys_dir=str(keys_dir.absolute()),
                key_map=config['key_map'],
                encrypted_keys=config['encrypted_keys'],
                expiration_days=config['expiration_days'],
                thresholds=config['thresholds']
            )
            repo.initialize()
        
        # 添加目标文件
        print("添加目标文件...")
        if targets_dir.exists():
            target_files = list(targets_dir.rglob("*"))
            print(f"找到 {len(target_files)} 个目标文件")
            
            # 使用add_bundle方法而不是add_target方法
            # 我们需要将targets目录作为一个bundle添加
            if targets_dir.exists() and any(targets_dir.iterdir()):
                try:
                    # 获取版本号，这里我们假设使用当前时间作为版本号
                    import datetime
                    version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    
                    # 添加整个targets目录作为bundle
                    repo.add_bundle(new_bundle_dir=targets_dir.absolute(), new_version=version)
                    print(f"成功添加目标文件bundle，版本: {version}")
                except Exception as e:
                    print(f"添加目标文件bundle失败: {e}")
            else:
                print("targets目录为空，跳过添加")
        
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
    success = fix_tuf_repository()
    if success:
        print("\nTUF仓库修复成功!")
    else:
        print("\nTUF仓库修复失败!")