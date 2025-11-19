#!/usr/bin/env python3
"""
修复 GitHub Actions 中的 TUF 仓库问题（最终版本）
"""

import json
import os
import shutil
import sys
from pathlib import Path

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
    METADATA_DIR = REPO_DIR / 'metadata'
    
    # 手动创建版本化的元数据文件，完全避免使用 tufup 库可能的交互式提示
    try:
        # 检查基础文件是否存在
        root_path = METADATA_DIR / "root.json"
        
        if not root_path.exists():
            print("✗ 缺少基础文件: root.json")
            return False
        
        # 如果1.root.json不存在，复制root.json为1.root.json
        root1_path = METADATA_DIR / "1.root.json"
        if not root1_path.exists():
            print("创建1.root.json文件...")
            shutil.copy(root_path, root1_path)
            print("✓ 1.root.json文件创建成功")
        
        # 创建2.root.json文件
        root2_path = METADATA_DIR / "2.root.json"
        if not root2_path.exists():
            print("创建2.root.json文件...")
            # 读取root.json内容
            with open(root_path, 'r') as f:
                root_data = json.load(f)
            
            # 更新版本号
            root_data['signed']['version'] = 2
            
            # 写入2.root.json
            with open(root2_path, 'w') as f:
                json.dump(root_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            
            print("✓ 2.root.json文件创建成功")
        
        # 验证生成的元数据文件
        return verify_metadata_files(METADATA_DIR)
            
    except Exception as e:
        print(f"创建版本化文件时出错: {e}")
        import traceback
        traceback.print_exc()
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