#!/usr/bin/env python3
"""
打包需要上传到服务器的TUF元数据和目标文件
"""

import shutil
from pathlib import Path

def package_for_server():
    """打包需要上传到服务器的文件"""
    print("=== 打包需要上传到服务器的文件 ===")
    
    # 定义路径
    updates_dir = Path("updates")
    metadata_dir = updates_dir / "metadata"
    targets_dir = updates_dir / "targets"
    package_dir = Path("server_upload_package")
    
    # 创建打包目录
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制元数据文件
    metadata_package_dir = package_dir / "metadata"
    metadata_package_dir.mkdir()
    
    print("复制元数据文件...")
    metadata_files = list(metadata_dir.glob("*.json"))
    for meta_file in metadata_files:
        shutil.copy(meta_file, metadata_package_dir)
        print(f"  ✓ {meta_file.name}")
    
    # 复制目标文件
    targets_package_dir = package_dir / "targets"
    targets_package_dir.mkdir()
    
    print("复制目标文件...")
    target_files = list(targets_dir.rglob("*"))
    for target_file in target_files:
        if target_file.is_file():
            # 保持目录结构
            relative_path = target_file.relative_to(targets_dir)
            dest_path = targets_package_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(target_file, dest_path)
            print(f"  ✓ {relative_path}")
    
    print(f"\n🎉 打包完成!")
    print(f"请将 '{package_dir}' 目录中的所有文件上传到服务器的相应目录。")
    print(f"元数据文件应上传到: /media/update/win/metadata/")
    print(f"目标文件应上传到: /media/update/win/targets/")

if __name__ == "__main__":
    package_for_server()