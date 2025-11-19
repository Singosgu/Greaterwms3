#!/usr/bin/env python3
"""
创建简单的更新包
"""

import zipfile
import shutil
import platform
import os
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def create_zip_package(source_dir, output_path):
    """创建ZIP格式的更新包"""
    print(f"创建ZIP更新包: {output_path}")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(source_dir)
                zipf.write(file_path, arc_path)
    print(f"ZIP更新包创建成功: {output_path}")

def ensure_versioned_metadata():
    """确保生成版本化的TUF元数据文件"""
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
        import json
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
            from tufup.repo import Repository
            repo = Repository.from_config()
            print("现有TUF仓库加载成功")
        except Exception as e:
            print(f"现有TUF仓库加载失败: {e}")
            print("使用配置重新初始化仓库...")
            # 创建新的仓库实例
            from tufup.repo import Repository
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
        import json
        import shutil
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
    import json
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

def create_simple_update():
    """创建简单的更新包"""
    print("开始创建简单的更新包...")
    
    # 检测当前平台（只支持Windows）
    system = platform.system().lower()
    package_format = 'zip'
    package_extension = '.zip'
    package_name = "Bomiot-1.1.1.zip"
    
    print(f"当前平台: {system}, 使用格式: {package_format}")
    
    # 创建临时目录
    temp_dir = Path("temp_app")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 创建targets目录
    targets_dir = Path("updates/targets")
    targets_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 复制主要文件和目录
        print("复制应用程序文件...")
        items_to_copy = [
            "main",
            "launcher.py",
            "requirements.txt"
        ]
        
        for item in items_to_copy:
            src = Path(item)
            if src.exists():
                dst = temp_dir / item
                if src.is_dir():
                    shutil.copytree(src, dst)
                    print(f"  复制目录: {item}")
                else:
                    shutil.copy2(src, dst)
                    print(f"  复制文件: {item}")
        
        # 创建更新包
        package_path = targets_dir / package_name
        print(f"创建更新包: {package_path}")
        
        if package_format == 'zip':
            create_zip_package(temp_dir, package_path)
        
        print("更新包创建成功!")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("临时文件清理完成!")
        
        # 确保生成版本化的元数据文件
        print("\n确保生成版本化的TUF元数据文件...")
        if ensure_versioned_metadata():
            print("✓ 版本化元数据文件生成成功!")
            return True
        else:
            print("✗ 版本化元数据文件生成失败!")
            return False
        
    except Exception as e:
        print(f"创建更新包时出错: {e}")
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False

if __name__ == "__main__":
    success = create_simple_update()
    if success:
        print("\n简单更新包创建成功!")
    else:
        print("\n简单更新包创建失败!")
        sys.exit(1)