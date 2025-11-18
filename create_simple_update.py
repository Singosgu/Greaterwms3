#!/usr/bin/env python3
"""
创建简单的更新包
"""

import tarfile
import zipfile
import shutil
import platform
import os
from pathlib import Path

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

def create_simple_update():
    """创建简单的更新包"""
    print("开始创建简单的更新包...")
    
    # 检测当前平台
    system = platform.system().lower()
    if system == 'windows':
        package_format = 'zip'
        package_extension = '.zip'
        package_name = "Bomiot-1.1.1.zip"
    else:
        package_format = 'tar.gz'
        package_extension = '.tar.gz'
        package_name = "Bomiot-1.1.1.tar.gz"
    
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
        else:
            create_tar_gz_package(temp_dir, package_path)
        
        print("更新包创建成功!")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("临时文件清理完成!")
        
        return True
        
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