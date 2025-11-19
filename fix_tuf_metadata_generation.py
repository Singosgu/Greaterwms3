#!/usr/bin/env python3
"""
修复TUF元数据生成问题，确保生成版本化的元数据文件
"""

import json
import os
import shutil
from pathlib import Path
from tufup.repo import Repository

def fix_tuf_metadata_generation():
    """修复TUF元数据生成问题"""
    print("=== 修复TUF元数据生成问题 ===")
    
    # 定义路径
    updates_dir = Path("updates")
    keys_dir = updates_dir / "keys"
    metadata_dir = updates_dir / "metadata"
    targets_dir = updates_dir / "targets"
    
    # 根据TUF仓库初始化与自动化更新规则，先彻底删除现有目录内容
    print("1. 清理现有TUF仓库...")
    for directory in [keys_dir, metadata_dir, targets_dir]:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"   ✓ 删除目录: {directory}")
            except Exception as e:
                print(f"   ⚠ 删除目录失败 {directory}: {e}")
    
    # 重新创建必要的目录
    print("2. 创建TUF仓库目录结构...")
    for directory in [keys_dir, metadata_dir, targets_dir]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ 创建目录: {directory}")
        except Exception as e:
            print(f"   ✗ 创建目录失败 {directory}: {e}")
            return False
    
    # 从配置文件读取设置
    print("3. 读取TUF仓库配置...")
    config_file = Path('.tufup-repo-config')
    if not config_file.exists():
        print("   ✗ 错误: .tufup-repo-config 文件不存在")
        return False
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("   ✓ 配置文件读取成功")
    except Exception as e:
        print(f"   ✗ 配置文件读取失败: {e}")
        return False
    
    print("   配置信息:")
    print(f"     应用名称: {config['app_name']}")
    
    # 创建仓库实例
    print("4. 创建TUF仓库实例...")
    try:
        repo = Repository(
            app_name=config['app_name'],
            repo_dir=str(updates_dir.absolute()),
            keys_dir=str(keys_dir.absolute()),
            key_map=config.get('key_map'),
            encrypted_keys=config.get('encrypted_keys', []),
            expiration_days=config.get('expiration_days'),
            thresholds=config.get('thresholds')
        )
        print("   ✓ TUF仓库实例创建成功")
    except Exception as e:
        print(f"   ✗ TUF仓库实例创建失败: {e}")
        return False
    
    # 初始化仓库
    print("5. 初始化TUF仓库...")
    try:
        repo.initialize()
        print("   ✓ TUF仓库初始化成功")
    except Exception as e:
        print(f"   ✗ TUF仓库初始化失败: {e}")
        return False
    
    # 创建示例应用文件
    print("6. 创建示例应用文件...")
    app_dir = updates_dir / 'app'  # 在try-except外部定义
    current_version = '1.0.0'  # 默认版本
    try:
        app_dir.mkdir(exist_ok=True)
        
        # 从server_config.json读取版本信息
        server_config_path = Path("main/server_config.json")
        if server_config_path.exists():
            with open(server_config_path, 'r', encoding='utf-8') as f:
                server_config = json.load(f)
            current_version = server_config.get('current_version', '1.0.0')
        
        app_file = app_dir / 'app.py'
        app_file.write_text(f'# Bomiot Application\nprint("Hello from Bomiot version {current_version}")')
        print(f"   ✓ 示例应用文件创建成功 (版本: {current_version})")
    except Exception as e:
        print(f"   ⚠ 示例应用文件创建失败: {e}")
        current_version = '1.0.0'  # 使用默认版本
    
    # 添加初始版本到仓库
    print("7. 添加初始版本到TUF仓库...")
    try:
        repo.add_bundle(
            new_bundle_dir=app_dir,
            new_version=current_version,
            skip_patch=True  # 跳过补丁创建以简化示例
        )
        print("   ✓ 初始版本添加成功")
    except Exception as e:
        print(f"   ✗ 初始版本添加失败: {e}")
        return False
    
    # 发布更改以确保所有元数据都被正确签名和版本化
    print("8. 发布TUF仓库更改...")
    try:
        repo.publish_changes(private_key_dirs=[str(keys_dir.absolute())])
        print("   ✓ TUF仓库更改发布成功")
    except Exception as e:
        print(f"   ✗ TUF仓库更改发布失败: {e}")
        return False
    
    # 验证生成的元数据文件
    print("9. 验证生成的元数据文件...")
    required_files = [
        "root.json",
        "1.root.json",
        "2.root.json",  # 这是之前缺失的文件
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
            print(f"   ✗ {filename} 不存在")
            missing_files.append(filename)
    
    # 检查targets目录
    print("10. 检查目标文件...")
    target_files = list(targets_dir.glob("*"))
    if target_files:
        print(f"   ✓ 发现 {len(target_files)} 个目标文件:")
        for target_file in target_files:
            print(f"     - {target_file.name}")
    else:
        print("   ⚠ targets目录为空")
    
    if not missing_files:
        print("\n✓ TUF元数据生成修复完成!")
        print("  所有必需的元数据文件都已生成，包括版本化的文件。")
        return True
    else:
        print(f"\n⚠ TUF元数据生成修复完成，但以下文件仍缺失:")
        for missing in missing_files:
            print(f"  - {missing}")
        return False

def verify_tuf_repository():
    """验证TUF仓库状态"""
    print("\n=== 验证TUF仓库状态 ===")
    
    metadata_dir = Path("updates/metadata")
    if not metadata_dir.exists():
        print("✗ metadata目录不存在")
        return False
    
    # 列出所有元数据文件
    print("当前metadata目录中的文件:")
    for item in metadata_dir.iterdir():
        if item.is_file():
            size = item.stat().st_size
            print(f"  {item.name} ({size} bytes)")
    
    # 检查关键文件
    key_files = ["root.json", "1.root.json", "2.root.json", "snapshot.json", "targets.json", "timestamp.json"]
    all_present = True
    for key_file in key_files:
        file_path = metadata_dir / key_file
        if file_path.exists():
            print(f"✓ {key_file} 存在")
        else:
            print(f"✗ {key_file} 缺失")
            all_present = False
    
    return all_present

def main():
    """主函数"""
    print("TUF元数据生成修复工具")
    print("=" * 50)
    
    # 执行修复
    success = fix_tuf_metadata_generation()
    
    # 验证结果
    if success:
        verify_success = verify_tuf_repository()
        if verify_success:
            print("\n🎉 修复成功完成!")
            print("   TUF仓库已正确初始化，所有元数据文件均已生成。")
            print("   您可以重新启动应用程序测试更新功能。")
        else:
            print("\n⚠ 修复完成但验证失败，请检查上述错误。")
    else:
        print("\n❌ 修复失败，请检查上述错误。")

if __name__ == "__main__":
    main()