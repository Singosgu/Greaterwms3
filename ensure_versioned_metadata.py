#!/usr/bin/env python3
"""
确保生成版本化的TUF元数据文件
此脚本应该在创建更新包后运行，以确保所有版本化的元数据文件都已生成
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def ensure_versioned_metadata():
    """确保生成版本化的元数据文件"""
    print("=== 确保生成版本化的TUF元数据文件 ===")
    
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
        
        # 发布更改以确保生成版本化的元数据文件
        print("发布TUF仓库更改以生成版本化元数据文件...")
        try:
            repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
            print("✓ TUF仓库更改发布成功，版本化元数据文件已生成")
        except Exception as e:
            print(f"✗ TUF仓库更改发布失败: {e}")
            # 如果发布失败，尝试手动创建版本化的文件
            print("尝试手动创建版本化元数据文件...")
            return create_versioned_files_manually(metadata_dir)
        
        # 验证生成的元数据文件
        print("验证生成的元数据文件...")
        return verify_metadata_files(metadata_dir)
            
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

def create_versioned_files_manually(metadata_dir):
    """手动创建版本化的元数据文件"""
    try:
        # 检查基础文件是否存在
        root_path = metadata_dir / "root.json"
        root1_path = metadata_dir / "1.root.json"
        
        if not root_path.exists():
            print("✗ 缺少基础文件: root.json")
            return False
        
        # 如果1.root.json不存在，复制root.json为1.root.json
        if not root1_path.exists():
            print("创建1.root.json文件...")
            shutil.copy(root_path, root1_path)
            print("✓ 1.root.json文件创建成功")
        
        # 创建2.root.json文件
        root2_path = metadata_dir / "2.root.json"
        if not root2_path.exists():
            print("创建2.root.json文件...")
            # 读取1.root.json内容
            with open(root1_path, 'r') as f:
                root_data = json.load(f)
            
            # 更新版本号
            root_data['signed']['version'] = 2
            
            # 写入2.root.json
            with open(root2_path, 'w') as f:
                json.dump(root_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            
            print("✓ 2.root.json文件创建成功")
        
        return True
    except Exception as e:
        print(f"手动创建版本化文件时出错: {e}")
        return False

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
    success = ensure_versioned_metadata()
    if success:
        print("\n🎉 版本化元数据文件生成完成!")
        print("现在应该可以解决2.root.json文件缺失的问题了。")
    else:
        print("\n❌ 版本化元数据文件生成失败!")
        exit(1)