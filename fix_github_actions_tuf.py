#!/usr/bin/env python3
"""
修复 GitHub Actions 中的 TUF 密钥问题
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def fix_github_actions_tuf():
    """修复 GitHub Actions 中的 TUF 密钥问题"""
    print("=== 修复 GitHub Actions 中的 TUF 密钥问题 ===")
    
    # 从 .tufup-repo-config 文件读取配置
    with open('.tufup-repo-config', 'r') as f:
        config = json.load(f)
    
    # 定义仓库路径
    REPO_DIR = Path.cwd() / config['repo_dir']
    KEYS_DIR = REPO_DIR / config['keys_dir'].split('/')[-1]
    METADATA_DIR = REPO_DIR / 'metadata'
    TARGETS_DIR = REPO_DIR / 'targets'
    
    # 检查是否已存在密钥
    existing_keys = list(KEYS_DIR.glob("*")) if KEYS_DIR.exists() else []
    
    if existing_keys:
        print("发现现有密钥，跳过重新生成...")
        print("现有密钥文件:")
        for key_file in existing_keys:
            print(f"  - {key_file.name}")
        
        # 检查是否已存在元数据
        existing_metadata = list(METADATA_DIR.glob("*.json")) if METADATA_DIR.exists() else []
        if existing_metadata:
            print("发现现有元数据，跳过重新生成...")
            print("现有元数据文件:")
            for meta_file in existing_metadata:
                print(f"  - {meta_file.name}")
            return True
    
    # 如果没有现有密钥或元数据，则初始化仓库
    print("未发现现有密钥或元数据，初始化新的 TUF 仓库...")
    
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
    
    print("TUF 密钥问题修复完成!")
    return True

if __name__ == "__main__":
    success = fix_github_actions_tuf()
    if success:
        print("\n🎉 GitHub Actions TUF 密钥问题修复成功!")
    else:
        print("\n❌ GitHub Actions TUF 密钥问题修复失败!")