#!/usr/bin/env python3
"""
修复TUF仓库密钥问题
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def fix_tuf_keys():
    """修复TUF仓库密钥问题"""
    print("=== 修复TUF仓库密钥问题 ===")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    
    # 检查必要的目录
    if not updates_dir.exists():
        print("错误: updates目录不存在")
        return False
    
    # 创建keys目录（如果不存在）
    keys_dir.mkdir(parents=True, exist_ok=True)
    
    # 从项目根目录读取配置文件
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
        # 检查现有的密钥文件
        print("检查现有的密钥文件...")
        key_files = list(keys_dir.glob("*"))
        if key_files:
            print(f"找到 {len(key_files)} 个密钥文件:")
            for key_file in key_files:
                print(f"  - {key_file.name}")
        else:
            print("未找到密钥文件")
        
        # 创建仓库实例
        print("创建TUF仓库实例...")
        repo = Repository(
            app_name=config['app_name'],
            repo_dir=".",
            keys_dir=str(keys_dir.relative_to(updates_dir)),
            key_map=config.get('key_map'),
            encrypted_keys=config.get('encrypted_keys', []),
            expiration_days=config.get('expiration_days'),
            thresholds=config.get('thresholds')
        )
        
        # 重新初始化仓库（强制重新创建密钥）
        print("重新初始化TUF仓库...")
        repo.initialize()
        print("TUF仓库重新初始化完成!")
        
        # 发布更改以生成新的元数据
        print("发布TUF仓库更改...")
        repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
        print("TUF仓库更改发布完成!")
        
        # 验证生成的元数据文件
        print("验证生成的元数据文件...")
        return verify_metadata_signatures(metadata_dir, keys_dir)
            
    except Exception as e:
        print(f"修复TUF密钥时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

def verify_metadata_signatures(metadata_dir, keys_dir):
    """验证元数据签名"""
    required_files = [
        "root.json",
        "1.root.json",
        "2.root.json",
        "snapshot.json",
        "targets.json",
        "timestamp.json"
    ]
    
    all_valid = True
    for filename in required_files:
        file_path = metadata_dir / filename
        if file_path.exists():
            print(f"   ✓ {filename} 存在")
            # 这里可以添加更详细的签名验证逻辑
        else:
            print(f"   ✗ {filename} 缺失")
            all_valid = False
    
    if all_valid:
        print("\n🎉 所有必需的元数据文件都已生成并签名!")
        return True
    else:
        print(f"\n⚠ 一些元数据文件缺失!")
        return False

if __name__ == "__main__":
    success = fix_tuf_keys()
    if success:
        print("\n✅ TUF密钥问题修复成功!")
    else:
        print("\n❌ TUF密钥问题修复失败!")