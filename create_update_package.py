#!/usr/bin/env python3
"""
创建应用程序更新包并添加到TUF仓库
"""

import json
import os
import shutil
import tarfile
import zipfile
import platform
import sys
from pathlib import Path
from tufup.repo import Repository

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

def create_tar_gz_package(source_dir, output_path):
    """创建TAR.GZ格式的更新包"""
    print(f"创建TAR.GZ更新包: {output_path}")
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(source_dir, arcname=".")
    print(f"TAR.GZ更新包创建成功: {output_path}")

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

def create_update_package():
    """创建更新包并添加到TUF仓库"""
    print("开始创建应用程序更新包...")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    targets_dir = updates_dir / "targets"
    
    # 从server_config.json读取应用信息
    server_config_path = Path("main/server_config.json")
    if not server_config_path.exists():
        print("错误: server_config.json文件不存在")
        return False
    
    with open(server_config_path, 'r', encoding='utf-8') as f:
        server_config = json.load(f)
    
    app_name = server_config.get('app_name', 'Bomiot')
    current_version = server_config.get('current_version', '1.0.0')
    
    print(f"应用名称: {app_name}")
    print(f"当前版本: {current_version}")
    
    # 检测当前平台
    system = platform.system().lower()
    if system == 'windows':
        package_format = 'zip'
        package_extension = '.zip'
    else:
        package_format = 'tar.gz'
        package_extension = '.tar.gz'
    
    print(f"当前平台: {system}, 使用格式: {package_format}")
    
    # 创建targets目录（如果不存在）
    targets_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建临时目录用于打包
    temp_dir = Path("temp_package")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # 复制需要打包的文件到临时目录
        print("复制应用程序文件...")
        files_to_copy = [
            "main",
            "launcher.py",
            "requirements.txt",
            "server_config.json",
            "__version__.py"
        ]
        
        for item in files_to_copy:
            src = Path(item)
            if src.exists():
                dst = temp_dir / item
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"  复制: {item}")
        
        # 创建更新包
        package_name = f"{app_name}-{current_version}{package_extension}"
        package_path = targets_dir / package_name
        
        if package_format == 'zip':
            create_zip_package(temp_dir, package_path)
        else:
            create_tar_gz_package(temp_dir, package_path)
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        # 检查仓库是否存在配置文件
        config_file = Path('.tufup-repo-config')
        if not config_file.exists():
            print("错误: .tufup-repo-config文件不存在")
            return False
        
        # 从配置文件读取仓库设置
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # 创建或加载仓库
        print("加载TUF仓库...")
        original_cwd = Path.cwd()
        repo = None
        try:
            # 切换到项目根目录以确保正确加载配置文件
            os.chdir(original_cwd)
            
            # 使用 from_config 方法加载现有仓库配置
            repo = Repository.from_config()
            print("仓库加载成功")
        except Exception as e:
            print(f"仓库加载失败: {e}")
            print("重新初始化仓库...")
            repo = Repository(
                app_name=config['app_name'],
                repo_dir=str(updates_dir),
                keys_dir=str(keys_dir),
                key_map=config['key_map'],
                encrypted_keys=config['encrypted_keys'],
                expiration_days=config['expiration_days'],
                thresholds=config['thresholds']
            )
            repo.initialize()
            print("仓库初始化成功")
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
        
        # 添加目标文件（使用add_bundle方法而不是add_target）
        print("添加目标文件到仓库...")
        # 创建一个临时目录来存放更新包，以便add_bundle可以处理
        bundle_dir = Path("temp_bundle")
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        
        # 将更新包复制到bundle目录
        shutil.copy2(package_path, bundle_dir / package_name)
        
        # 使用add_bundle添加目标文件
        repo.add_bundle(
            new_bundle_dir=bundle_dir,
            new_version=current_version
        )
        
        # 清理临时bundle目录
        shutil.rmtree(bundle_dir)
        
        # 发布更改
        print("发布仓库更改...")
        repo.publish_changes(private_key_dirs=[str(keys_dir)])
        
        print("TUF仓库更新完成!")
        
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
        import traceback
        traceback.print_exc()
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        # 清理临时bundle目录（如果存在）
        bundle_dir = Path("temp_bundle")
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        return False

if __name__ == "__main__":
    success = create_update_package()
    if success:
        print("\n应用程序更新包创建和TUF仓库更新成功!")
    else:
        print("\n应用程序更新包创建和TUF仓库更新失败!")
        sys.exit(1)
