#!/usr/bin/env python3
"""
修复TUF仓库密钥问题的最终版本
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def fix_tuf_keys_final():
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
        
        # 删除现有的密钥文件以强制重新生成
        print("删除现有的密钥文件以强制重新生成...")
        for key_file in keys_dir.glob("*"):
            key_file.unlink()
            print(f"已删除: {key_file.name}")
        
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
        metadata_files = list(metadata_dir.glob("*.json"))
        if metadata_files:
            print(f"生成了 {len(metadata_files)} 个元数据文件:")
            for meta_file in metadata_files:
                print(f"  - {meta_file.name}")
        else:
            print("警告: 未生成任何元数据文件")
        
        print("TUF密钥修复完成!")
        return True
            
    except Exception as e:
        print(f"修复TUF密钥时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

if __name__ == "__main__":
    success = fix_tuf_keys_final()
    if success:
        print("\n🎉 TUF密钥修复成功!")
        print("请重新上传updates/metadata目录下的所有文件到服务器。")
    else:
        print("\n❌ TUF密钥修复失败!")
