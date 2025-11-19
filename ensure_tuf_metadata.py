#!/usr/bin/env python3
"""
确保TUF元数据文件正确生成，包括版本化的root.json文件
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def ensure_tuf_metadata():
    """确保TUF元数据文件正确生成"""
    print("=== 确保TUF元数据文件正确生成 ===")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    
    # 检查必要的目录
    if not updates_dir.exists():
        print("错误: updates目录不存在")
        return False
    
    if not keys_dir.exists():
        print("错误: keys目录不存在")
        return False
    
    if not metadata_dir.exists():
        print("错误: metadata目录不存在")
        return False
    
    # 从配置文件读取设置
    config_file = Path('.tufup-repo-config')
    if not config_file.exists():
        print("错误: .tufup-repo-config 文件不存在")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"配置加载成功: {config['app_name']}")
    except Exception as e:
        print(f"配置加载失败: {e}")
        return False
    
    # 更改当前工作目录到updates目录
    original_cwd = os.getcwd()
    os.chdir(updates_dir)
    
    try:
        # 尝试加载现有仓库
        try:
            print("尝试加载现有TUF仓库...")
            repo = Repository.from_config()
            print("现有TUF仓库加载成功")
        except Exception as e:
            print(f"现有TUF仓库加载失败: {e}")
            print("使用配置重新初始化仓库...")
            # 创建新的仓库实例
            repo = Repository(
                app_name=config['app_name'],
                repo_dir=".",
                keys_dir=str(keys_dir.relative_to(updates_dir)),
                key_map=config.get('key_map'),
                encrypted_keys=config.get('encrypted_keys', []),
                expiration_days=config.get('expiration_days'),
                thresholds=config.get('thresholds')
            )
            repo.initialize()
            print("仓库初始化成功")
        
        # 发布更改以确保生成版本化的元数据文件
        print("发布TUF仓库更改以生成版本化元数据文件...")
        try:
            repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
            print("✓ TUF仓库更改发布成功，版本化元数据文件已生成")
        except Exception as e:
            print(f"✗ TUF仓库更改发布失败: {e}")
            return False
        
        # 验证生成的元数据文件
        print("验证生成的元数据文件...")
        return verify_metadata_files(metadata_dir)
            
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

def verify_metadata_files(metadata_dir):
    """验证元数据文件"""
    required_files = [
        "root.json",
        "1.root.json",
        "2.root.json",  # 这是我们需要确保生成的文件
        "snapshot.json",
        "targets.json",
        "timestamp.json"
    ]
    
    missing_files = []
    for filename in required_files:
        file_path = metadata_dir / filename
        if file_path.exists():
            print(f"   ✓ {filename} 存在")
        else:
            print(f"   ✗ {filename} 缺失")
            missing_files.append(filename)
    
    if not missing_files:
        print("\n🎉 所有必需的元数据文件都已生成!")
        return True
    else:
        print(f"\n⚠ 以下文件缺失: {missing_files}")
        return False

if __name__ == "__main__":
    success = ensure_tuf_metadata()
    if success:
        print("\n✅ TUF元数据文件生成成功!")
    else:
        print("\n❌ TUF元数据文件生成失败!")
        exit(1)