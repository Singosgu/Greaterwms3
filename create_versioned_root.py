#!/usr/bin/env python3
"""
手动创建版本化的root.json文件
"""

import json
import shutil
from pathlib import Path

def create_versioned_root():
    """创建版本化的root.json文件"""
    print("创建版本化的root.json文件...")
    
    # 定义路径
    metadata_dir = Path("updates/metadata")
    
    # 检查1.root.json是否存在
    root1_path = metadata_dir / "1.root.json"
    root_path = metadata_dir / "root.json"
    
    if root1_path.exists() and root_path.exists():
        # 复制1.root.json为2.root.json
        root2_path = metadata_dir / "2.root.json"
        
        # 读取1.root.json内容
        with open(root1_path, 'r') as f:
            root_data = json.load(f)
        
        # 保存为2.root.json
        with open(root2_path, 'w') as f:
            json.dump(root_data, f, indent=2)
        
        print(f"✓ 成功创建: {root2_path}")
        
        # 验证所有文件
        required_files = ["root.json", "1.root.json", "2.root.json", "snapshot.json", "targets.json", "timestamp.json"]
        print("\n验证文件:")
        for filename in required_files:
            file_path = metadata_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✓ {filename} ({size} bytes)")
            else:
                print(f"  ✗ {filename} (缺失)")
        
        return True
    else:
        print("✗ 缺少必要的文件: 1.root.json 或 root.json")
        return False

if __name__ == "__main__":
    success = create_versioned_root()
    if success:
        print("\n🎉 版本化元数据文件创建完成!")
        print("现在应该可以解决502 Bad Gateway错误了。")
    else:
        print("\n❌ 版本化元数据文件创建失败!")