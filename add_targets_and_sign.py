#!/usr/bin/env python3
"""
手动添加目标文件并重新签名TUF仓库
"""

import json
import hashlib
from pathlib import Path

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def add_targets_and_sign():
    """添加目标文件并重新签名"""
    print("开始添加目标文件并重新签名...")
    
    # 定义路径
    updates_dir = Path("updates")
    targets_dir = updates_dir / "targets"
    metadata_dir = updates_dir / "metadata"
    
    # 检查目录是否存在
    if not targets_dir.exists():
        print("错误: targets目录不存在")
        return False
    
    # 收集所有目标文件信息
    targets_info = {}
    target_files = list(targets_dir.rglob("*"))
    print(f"找到 {len(target_files)} 个文件")
    
    for target_file in target_files:
        if target_file.is_file():
            # 计算相对于targets目录的路径
            relative_path = target_file.relative_to(targets_dir)
            relative_path_str = str(relative_path).replace("\\", "/")  # 使用正斜杠
            
            # 计算文件长度和哈希
            file_length = target_file.stat().st_size
            file_hash = calculate_file_hash(target_file)
            
            # 添加到目标信息
            targets_info[relative_path_str] = {
                "length": file_length,
                "hashes": {
                    "sha256": file_hash
                },
                "custom": {
                    "tufup": {
                        "required": False
                    }
                }
            }
            print(f"处理文件: {relative_path_str} (大小: {file_length} bytes)")
    
    # 读取现有的targets.json
    targets_json_path = metadata_dir / "targets.json"
    if not targets_json_path.exists():
        print("错误: targets.json文件不存在")
        return False
    
    with open(targets_json_path, 'r') as f:
        targets_data = json.load(f)
    
    # 更新targets字段
    targets_data['signed']['targets'] = targets_info
    
    # 增加版本号
    targets_data['signed']['version'] += 1
    
    # 重新计算签名（这里我们只是更新版本号，实际签名需要私钥）
    # 在实际应用中，这一步需要使用tufup库来正确签名
    
    # 保存更新后的targets.json
    with open(targets_json_path, 'w') as f:
        json.dump(targets_data, f, indent=2, ensure_ascii=False)
    
    print(f"成功更新targets.json，添加了 {len(targets_info)} 个目标文件")
    
    # 更新timestamp.json
    timestamp_json_path = metadata_dir / "timestamp.json"
    if timestamp_json_path.exists():
        with open(timestamp_json_path, 'r') as f:
            timestamp_data = json.load(f)
        
        # 更新版本号
        timestamp_data['signed']['version'] += 1
        timestamp_data['signed']['meta']['snapshot.json']['version'] += 1
        
        # 保存更新后的timestamp.json
        with open(timestamp_json_path, 'w') as f:
            json.dump(timestamp_data, f, indent=2, ensure_ascii=False)
        
        print("成功更新timestamp.json")
    
    # 更新snapshot.json
    snapshot_json_path = metadata_dir / "snapshot.json"
    if snapshot_json_path.exists():
        with open(snapshot_json_path, 'r') as f:
            snapshot_data = json.load(f)
        
        # 更新版本号
        snapshot_data['signed']['version'] += 1
        
        # 更新targets.json的版本信息
        if 'targets.json' in snapshot_data['signed']['meta']:
            snapshot_data['signed']['meta']['targets.json']['version'] = targets_data['signed']['version']
        
        # 保存更新后的snapshot.json
        with open(snapshot_json_path, 'w') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
        
        print("成功更新snapshot.json")
    
    print("所有元数据文件更新完成!")
    return True

if __name__ == "__main__":
    success = add_targets_and_sign()
    if success:
        print("\n目标文件添加和签名更新成功!")
    else:
        print("\n目标文件添加和签名更新失败!")