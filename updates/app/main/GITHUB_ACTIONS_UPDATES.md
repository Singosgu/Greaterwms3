# GitHub Actions 自动化生成 Updates 信息

## 概述

本文档说明了如何在 GitHub Actions 工作流中自动化生成 TUF 仓库所需的 updates 目录信息，确保在所有支持的平台上都能正确生成必要的元数据文件。该流程会自动覆盖现有数据，确保每次构建都使用最新的配置。

## 工作原理

在 GitHub Actions 构建过程中，我们添加了一个专门的步骤来初始化 TUF 仓库：

1. **清理现有数据** - 自动清理现有的 updates 目录以确保干净的构建环境
2. **创建目录结构** - 自动创建 updates 目录及其子目录
3. **初始化 TUF 仓库** - 生成必要的密钥对和元数据文件
4. **创建示例应用包** - 生成初始版本的目标文件
5. **发布初始版本** - 将初始版本添加到 TUF 仓库

## 实现细节

### Windows 平台

```yaml
- name: Clean and Initialize TUF Repository (Windows)
  if: runner.os == 'Windows'
  run: |
    python -c "
    import os
    import sys
    import shutil
    from pathlib import Path
    sys.path.insert(0, str(Path.cwd()))
    from main.update_config import APP_NAME, CURRENT_VERSION
    from tufup.repo import Repository
    
    # 定义仓库路径
    REPO_DIR = Path.cwd() / 'updates'
    KEYS_DIR = REPO_DIR / 'keys'
    METADATA_DIR = REPO_DIR / 'metadata'
    TARGETS_DIR = REPO_DIR / 'targets'
    
    # 清理现有的目录（如果存在）
    for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f'清理目录: {directory}')
    
    # 创建必要的目录
    for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f'创建目录: {directory}')
    
    # 创建仓库实例
    repo = Repository(
        app_name=APP_NAME,
        repo_dir=REPO_DIR,
        keys_dir=KEYS_DIR,
    )
    
    # 初始化仓库
    repo.initialize()
    print('TUF 仓库初始化成功!')
    
    # 创建一个简单的应用目录结构作为示例
    app_dir = REPO_DIR / 'app'
    app_dir.mkdir(exist_ok=True)
    
    # 创建一个简单的应用文件
    app_file = app_dir / 'app.py'
    app_file.write_text(f'# {APP_NAME} Application\\nprint(\"Hello from {APP_NAME} version {CURRENT_VERSION}\")')
    
    # 添加初始版本到仓库
    repo.add_bundle(
        new_bundle_dir=app_dir,
        new_version=CURRENT_VERSION,
        skip_patch=True  # 跳过补丁创建以简化示例
    )
    
    print('仓库初始化完成!')
    "
```

### macOS/Linux 平台

```yaml
- name: Clean and Initialize TUF Repository (macOS/Linux)
  if: runner.os != 'Windows'
  run: |
    python3 -c "
    import os
    import sys
    import shutil
    from pathlib import Path
    sys.path.insert(0, str(Path.cwd()))
    from main.update_config import APP_NAME, CURRENT_VERSION
    from tufup.repo import Repository
    
    # 定义仓库路径
    REPO_DIR = Path.cwd() / 'updates'
    KEYS_DIR = REPO_DIR / 'keys'
    METADATA_DIR = REPO_DIR / 'metadata'
    TARGETS_DIR = REPO_DIR / 'targets'
    
    # 清理现有的目录（如果存在）
    for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f'清理目录: {directory}')
    
    # 创建必要的目录
    for directory in [REPO_DIR, KEYS_DIR, METADATA_DIR, TARGETS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f'创建目录: {directory}')
    
    # 创建仓库实例
    repo = Repository(
        app_name=APP_NAME,
        repo_dir=REPO_DIR,
        keys_dir=KEYS_DIR,
    )
    
    # 初始化仓库
    repo.initialize()
    print('TUF 仓库初始化成功!')
    
    # 创建一个简单的应用目录结构作为示例
    app_dir = REPO_DIR / 'app'
    app_dir.mkdir(exist_ok=True)
    
    # 创建一个简单的应用文件
    app_file = app_dir / 'app.py'
    app_file.write_text(f'# {APP_NAME} Application\\nprint(\"Hello from {APP_NAME} version {CURRENT_VERSION}\")')
    
    # 添加初始版本到仓库
    repo.add_bundle(
        new_bundle_dir=app_dir,
        new_version=CURRENT_VERSION,
        skip_patch=True  # 跳过补丁创建以简化示例
    )
    
    print('仓库初始化完成!')
    "
```

## 生成的文件结构

成功执行后，将生成以下文件结构：

```
updates/
├── keys/
│   ├── root
│   ├── root.pub
│   ├── snapshot
│   ├── snapshot.pub
│   ├── targets
│   ├── targets.pub
│   ├── timestamp
│   └── timestamp.pub
├── metadata/
│   ├── 1.root.json
│   ├── root.json
│   ├── snapshot.json
│   ├── targets.json
│   └── timestamp.json
└── targets/
    └── Bomiot-1.1.1.tar.gz
```

## 验证机制

工作流包含验证机制，确保所有关键文件都已正确生成：

1. **元数据文件验证** - 检查 root.json, targets.json, snapshot.json, timestamp.json
2. **目标文件验证** - 检查初始版本的目标文件
3. **目录结构验证** - 验证完整的目录结构

## 自动覆盖功能

新的实现包含了自动覆盖现有数据的功能：

1. **清理机制** - 在每次构建前自动清理现有的 updates 目录
2. **重建机制** - 重新创建完整的目录结构和文件
3. **一致性保证** - 确保每次构建都使用最新的配置和数据

## 注意事项

1. **密钥管理** - 在实际生产环境中，应使用安全的密钥管理机制
2. **版本控制** - 确保 BASE_VERSION 环境变量与实际应用版本一致
3. **平台兼容性** - 不同平台使用相应的 Python 命令（python vs python3）
4. **清理机制** - 在每次构建前清理旧的 updates 目录以避免冲突

## 故障排除

如果遇到问题，请检查：

1. Python 环境是否正确设置
2. 依赖包是否已正确安装
3. 文件权限是否正确
4. 磁盘空间是否充足
5. 是否有足够的权限删除和创建目录