#!/usr/bin/env python3
"""
修复Mac平台TUF元数据生成问题，确保生成版本化的元数据文件
"""

import json
import os
import shutil
import sys
from pathlib import Path
from tufup.repo import Repository

def fix_mac_tuf_generation():
    """修复Mac平台TUF元数据生成问题"""
    print("=== 修复Mac平台TUF元数据生成问题 ===")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    targets_dir = updates_dir / "targets"
    
    # 检查必要的文件和目录
    if not updates_dir.exists():
        print("错误: updates目录不存在")
        return False
    
    if not keys_dir.exists():
        print("错误: keys目录不存在")
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
        
        # 检查是否有目标文件需要添加
        if targets_dir.exists() and any(targets_dir.iterdir()):
            print("发现目标文件，添加到仓库...")
            try:
                # 获取targets目录中的所有文件
                target_files = list(targets_dir.rglob("*"))
                print(f"找到 {len(target_files)} 个目标文件")
                
                # 如果还没有版本，使用当前时间作为版本号
                import datetime
                version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                
                # 添加整个targets目录作为bundle
                repo.add_bundle(
                    new_bundle_dir=targets_dir.absolute(),
                    new_version=version,
                    skip_patch=True  # 跳过补丁创建
                )
                print(f"成功添加目标文件bundle，版本: {version}")
            except Exception as e:
                print(f"添加目标文件bundle失败: {e}")
        else:
            print("targets目录为空，跳过添加")
        
        # 发布更改以生成版本化的元数据文件
        print("发布TUF仓库更改以生成版本化元数据文件...")
        try:
            repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
            print("✓ TUF仓库更改发布成功，版本化元数据文件已生成")
        except Exception as e:
            print(f"✗ TUF仓库更改发布失败: {e}")
            return False
        
        # 验证生成的元数据文件
        print("验证生成的元数据文件...")
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
            # 如果2.root.json仍然缺失，手动创建它
            if "2.root.json" in missing_files:
                print("手动创建2.root.json文件...")
                root1_path = metadata_dir / "1.root.json"
                root2_path = metadata_dir / "2.root.json"
                
                if root1_path.exists():
                    # 读取1.root.json内容
                    with open(root1_path, 'r') as f:
                        root_data = json.load(f)
                    
                    # 更新版本号
                    root_data['signed']['version'] = 2
                    
                    # 写入2.root.json
                    with open(root2_path, 'w') as f:
                        json.dump(root_data, f, indent=2, sort_keys=True)
                    
                    print("✓ 2.root.json文件手动创建成功")
                    return True
                else:
                    print("✗ 无法创建2.root.json，因为1.root.json不存在")
                    return False
            return False
            
    finally:
        # 恢复原来的工作目录
        os.chdir(original_cwd)

if __name__ == "__main__":
    success = fix_mac_tuf_generation()
    if success:
        print("\n🎉 Mac平台TUF元数据生成修复完成!")
        print("现在应该可以解决2.root.json文件缺失的问题了。")
    else:
        print("\n❌ Mac平台TUF元数据生成修复失败!")
        sys.exit(1)