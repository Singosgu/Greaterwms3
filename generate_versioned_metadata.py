#!/usr/bin/env python3
"""
生成版本化的TUF元数据文件
"""

import json
import shutil
from pathlib import Path
from tufup.repo import Repository

def generate_versioned_metadata():
    """生成版本化的元数据文件"""
    print("开始生成版本化的TUF元数据文件...")
    
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
    
    # 创建仓库实例
    try:
        print("创建TUF仓库实例...")
        repo = Repository(
            app_name=config['app_name'],
            repo_dir=str(updates_dir.absolute()),
            keys_dir=str(keys_dir.absolute()),
            key_map=config.get('key_map'),
            encrypted_keys=config.get('encrypted_keys', []),
            expiration_days=config.get('expiration_days'),
            thresholds=config.get('thresholds')
        )
        print("TUF仓库实例创建成功")
    except Exception as e:
        print(f"TUF仓库实例创建失败: {e}")
        return False
    
    # 尝试加载现有仓库配置
    try:
        print("尝试加载现有仓库...")
        repo = Repository.from_config()
        print("现有仓库加载成功")
    except Exception as e:
        print(f"现有仓库加载失败: {e}")
        print("使用配置文件重新初始化仓库...")
        repo.initialize()
    
    # 检查是否有目标文件需要添加
    if targets_dir.exists() and any(targets_dir.iterdir()):
        print("发现目标文件，添加到仓库...")
        try:
            # 创建临时bundle目录
            bundle_dir = Path("temp_bundle")
            if bundle_dir.exists():
                shutil.rmtree(bundle_dir)
            bundle_dir.mkdir()
            
            # 复制targets目录中的文件
            for item in targets_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, bundle_dir / item.name)
            
            # 添加bundle
            import datetime
            version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            repo.add_bundle(new_bundle_dir=bundle_dir, new_version=version)
            print(f"目标文件添加成功，版本: {version}")
            
            # 清理临时目录
            shutil.rmtree(bundle_dir)
        except Exception as e:
            print(f"添加目标文件失败: {e}")
    else:
        print("未发现目标文件，跳过添加步骤")
    
    # 发布更改以生成版本化的元数据文件
    print("发布仓库更改...")
    try:
        repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
        print("仓库更改发布成功")
    except Exception as e:
        print(f"仓库更改发布失败: {e}")
        return False
    
    # 验证生成的文件
    print("验证生成的元数据文件...")
    required_files = ["root.json", "1.root.json", "2.root.json", "snapshot.json", "targets.json", "timestamp.json"]
    all_files_exist = True
    
    for filename in required_files:
        file_path = metadata_dir / filename
        if file_path.exists():
            print(f"  ✓ {filename} 存在")
        else:
            print(f"  ✗ {filename} 不存在")
            all_files_exist = False
    
    if all_files_exist:
        print("✓ 版本化元数据文件生成成功!")
        return True
    else:
        print("✗ 版本化元数据文件生成不完整!")
        return False

if __name__ == "__main__":
    success = generate_versioned_metadata()
    if success:
        print("\n🎉 元数据文件生成完成!")
    else:
        print("\n❌ 元数据文件生成失败!")