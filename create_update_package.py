#!/usr/bin/env python3
"""
创建应用程序更新包并添加到TUF仓库
"""

import json
import os
import shutil
import tarfile
from pathlib import Path
from tufup.repo import Repository

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
        
        # 创建tar.gz包
        package_name = f"{app_name}-{current_version}.tar.gz"
        package_path = targets_dir / package_name
        
        print(f"创建更新包: {package_name}")
        with tarfile.open(package_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=".")
        
        print(f"更新包创建成功: {package_path}")
        
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
        return True
        
    except Exception as e:
        print(f"创建更新包时出错: {e}")
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