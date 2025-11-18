#!/usr/bin/env python3
"""
创建简单的更新包
"""

import tarfile
import shutil
from pathlib import Path

def create_simple_update():
    """创建简单的更新包"""
    print("开始创建简单的更新包...")
    
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
        
        # 创建tar.gz包
        package_path = targets_dir / "Bomiot-1.1.1.tar.gz"
        print(f"创建更新包: {package_path}")
        
        with tarfile.open(package_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=".")
        
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