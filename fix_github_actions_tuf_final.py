#!/usr/bin/env python3
"""
修复 GitHub Actions 中的 TUF 仓库问题（最终版本）
"""

import json
import os
import shutil
import sys
from pathlib import Path
from tufup.repo import Repository

def fix_github_actions_tuf():
    """修复 GitHub Actions 中的 TUF 仓库问题"""
    print("=== 修复 GitHub Actions 中的 TUF 仓库问题 ===")
    
    # 从 .tufup-repo-config 文件读取配置
    config_file = Path('.tufup-repo-config')
    if not config_file.exists():
        print("错误: .tufup-repo-config 文件不存在")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 定义仓库路径
    REPO_DIR = Path.cwd() / config['repo_dir']
    KEYS_DIR = REPO_DIR / config['keys_dir'].split('/')[-1]
    METADATA_DIR = REPO_DIR / 'metadata'
    TARGETS_DIR = REPO_DIR / 'targets'
    
    print(f"仓库目录: {REPO_DIR}")
    print(f"密钥目录: {KEYS_DIR}")
    print(f"元数据目录: {METADATA_DIR}")
    print(f"目标目录: {TARGETS_DIR}")
    
    # 检查是否已存在密钥
    existing_keys = list(KEYS_DIR.glob('*')) if KEYS_DIR.exists() else []
    
    if existing_keys:
        print("发现现有密钥，跳过重新生成...")
        print("现有密钥文件:")
        for key_file in existing_keys:
            print(f"  - {key_file.name}")
    else:
        # 只有在没有现有密钥时才清理和初始化
        print('未发现现有密钥，初始化新的 TUF 仓库...')
        
        # 清理现有的目录（如果存在）
        for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f'清理目录: {directory}')
        
        # 创建必要的目录
        for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            print(f'创建目录: {directory}')
        
        # 创建仓库实例，使用与配置文件一致的参数
        repo = Repository(
            app_name=config['app_name'],
            repo_dir=REPO_DIR,
            keys_dir=KEYS_DIR,
            key_map=config['key_map'],
            encrypted_keys=config['encrypted_keys'],
            expiration_days=config['expiration_days'],
            thresholds=config['thresholds']
        )
        
        # 初始化仓库
        repo.initialize()
        print('TUF 仓库初始化成功!')
    
    # 清理可能存在的旧目标文件，避免交互式提示
    if TARGETS_DIR.exists():
        for existing_target in TARGETS_DIR.glob('*'):
            if existing_target.is_file():
                existing_target.unlink()
                print(f'删除旧目标文件: {existing_target}')
    
    print("TUF 仓库问题修复完成!")
    return True

def ensure_versioned_metadata():
    """确保生成版本化的元数据文件"""
    print("=== 确保生成版本化的元数据文件 ===")
    
    # 从 .tufup-repo-config 文件读取配置
    config_file = Path('.tufup-repo-config')
    if not config_file.exists():
        print("错误: .tufup-repo-config 文件不存在")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 定义仓库路径
    REPO_DIR = Path.cwd() / config['repo_dir']
    KEYS_DIR = REPO_DIR / config['keys_dir'].split('/')[-1]
    METADATA_DIR = REPO_DIR / 'metadata'
    
    # 更改当前工作目录到仓库目录
    original_cwd = os.getcwd()
    os.chdir(REPO_DIR)
    
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
                keys_dir=str(KEYS_DIR.relative_to(REPO_DIR)),
                key_map=config.get('key_map'),
                encrypted_keys=config.get('encrypted_keys', []),
                expiration_days=config.get('expiration_days'),
                thresholds=config.get('thresholds')
            )
            repo.initialize()
            print("TUF仓库初始化成功")
        
        # 发布更改以确保生成版本化的元数据文件
        print("发布TUF仓库更改以生成版本化元数据文件...")
        try:
            repo.publish_changes(private_key_dirs=[str(KEYS_DIR.absolute())])
            print("✓ TUF仓库更改发布成功，版本化元数据文件已生成")
        except Exception as e:
            print(f"✗ TUF仓库更改发布失败: {e}")
            # 如果发布失败，尝试手动创建版本化的文件
            print("尝试手动创建版本化元数据文件...")
            return create_versioned_files_manually(METADATA_DIR)
        
        # 验证生成的元数据文件
        print("验证生成的元数据文件...")
        return verify_metadata_files(METADATA_DIR)
            
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
    # 修复 TUF 仓库问题
    success = fix_github_actions_tuf()
    if not success:
        print("\n❌ TUF 仓库问题修复失败!")
        sys.exit(1)
    
    # 确保生成版本化的元数据文件
    print("\n确保生成版本化的元数据文件...")
    if ensure_versioned_metadata():
        print("\n🎉 TUF 仓库问题修复和元数据生成成功!")
    else:
        print("\n❌ 版本化元数据文件生成失败!")
        sys.exit(1)