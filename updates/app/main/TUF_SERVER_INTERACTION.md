# TUF 元数据与服务器交互机制

## 概述

本文档详细说明了 TUF (The Update Framework) 元数据的生成、部署和客户端交互机制。解答了关于客户端生成的元数据如何与服务器交互，以及服务器是否需要重新生成元数据的问题。

## TUF 工作原理

### 1. 角色分离

TUF 采用角色分离的安全模型：

1. **仓库端 (Repository)** - 负责生成和维护元数据
2. **客户端 (Client)** - 负责验证和使用元数据

### 2. 元数据类型

TUF 定义了四种核心元数据类型：

1. **root.json** - 根元数据，定义其他角色的密钥
2. **targets.json** - 目标元数据，描述可用的更新文件
3. **snapshot.json** - 快照元数据，记录其他元数据的版本信息
4. **timestamp.json** - 时间戳元数据，记录 snapshot.json 的版本信息

## 当前实现分析

### GitHub Actions 中的元数据生成

在我们的实现中，GitHub Actions 工作流会为每个平台生成 TUF 元数据：

```yaml
# 清理现有的 updates 目录并重新生成
- name: Clean and Initialize TUF Repository (Windows)
  if: runner.os == 'Windows'
  run: |
    python -c "
    # ... 代码省略 ...
    # 初始化仓库
    repo.initialize()
    # 添加初始版本到仓库
    repo.add_bundle(
        new_bundle_dir=app_dir,
        new_version=CURRENT_VERSION,
        skip_patch=True
    )
    "
```

这会生成以下文件结构：
```
updates/
├── keys/                 # 密钥文件（不应部署到服务器）
├── metadata/             # 元数据文件（需要部署到服务器）
│   ├── root.json
│   ├── targets.json
│   ├── snapshot.json
│   └── timestamp.json
└── targets/              # 目标文件（需要部署到服务器）
    └── Bomiot-1.1.1.tar.gz
```

## 服务器端部署

### 1. 部署内容

服务器端只需要部署以下内容：

1. **metadata/** 目录中的所有元数据文件
2. **targets/** 目录中的所有目标文件

**注意**：`keys/` 目录包含私钥，**绝不能**部署到服务器！

### 2. HTTP 服务器结构

服务器应提供以下 HTTP 结构：

```
http://3.135.61.8:8008/media/update/
├── metadata/
│   ├── root.json
│   ├── targets.json
│   ├── snapshot.json
│   └── timestamp.json
└── targets/
    └── Bomiot-1.1.1.tar.gz
```

### 3. 客户端访问 URL

客户端会使用以下 URL 访问服务器：

- 元数据基础 URL: `http://3.135.61.8:8008/media/update/metadata/`
- 目标文件基础 URL: `http://3.135.61.8:8008/media/update/targets/`

这在客户端初始化时配置：

```python
self.client = Client(
    app_name=self.app_name,
    app_install_dir=CURRENT_DIR,
    current_version=self.current_version,
    metadata_dir=METADATA_DIR,
    metadata_base_url=repository_url + "metadata/",
    target_dir=TARGETS_DIR,
    target_base_url=repository_url + "targets/",
    refresh_required=False,
)
```

## 新版本发布流程

### 1. 服务器端操作

当需要发布新版本时，服务器端需要：

1. **生成新版本目标文件**
   ```bash
   # 创建新版本的应用包
   tar -czf Bomiot-1.2.0.tar.gz app/
   ```

2. **更新 TUF 元数据**
   使用 TUF 工具更新元数据：
   ```python
   # 在服务器端使用 TUF 仓库工具
   repo = Repository(app_name="Bomiot", repo_dir=repo_path, keys_dir=keys_path)
   repo.add_bundle(new_bundle_dir="app/", new_version="1.2.0")
   repo.publish()  # 发布更新
   ```

3. **部署更新文件**
   将新生成的文件部署到服务器：
   - 新的元数据文件到 `metadata/` 目录
   - 新的目标文件到 `targets/` 目录

### 2. 客户端操作

客户端会自动检测和下载更新：

1. **检查更新**
   ```python
   # 客户端刷新元数据
   self.client.refresh()
   
   # 检查是否有可用更新
   if self.client.updates_available:
       # 有更新可用
   ```

2. **下载更新**
   ```python
   # 下载目标文件
   target_info = self.client.get_targetinfo("Bomiot-1.2.0.tar.gz")
   target_path = self.client.download_target(target_info)
   ```

## 关键问题解答

### 1. 客户端生成的元数据如何与服务器交互？

客户端**不生成**元数据。客户端只**消费**服务器提供的元数据：
- 客户端从服务器下载元数据文件进行验证
- 客户端根据元数据信息下载目标文件
- 客户端验证所有下载文件的完整性和签名

### 2. 服务器还需要再重新生成元数据吗？

是的，服务器需要重新生成元数据，但不是每次客户端检查更新时都生成：

1. **初始部署** - 服务器需要生成初始元数据
2. **新版本发布** - 服务器需要更新元数据以包含新版本信息
3. **日常运行** - 服务器提供现有元数据供客户端下载，无需重新生成

### 3. 为什么客户端不需要生成元数据？

因为：
- 元数据包含私钥签名信息，客户端没有私钥
- 安全模型要求只有可信的仓库端才能生成和签名元数据
- 客户端只能验证元数据的真实性，不能创建新的元数据

## 安全考虑

### 1. 密钥管理

- **私钥**必须安全存储，只能在服务器端访问
- **公钥**可以公开，用于客户端验证
- 定期轮换密钥以提高安全性

### 2. 元数据签名

所有元数据文件都必须使用相应的私钥签名：
- root.json - 使用根角色私钥签名
- targets.json - 使用目标角色私钥签名
- snapshot.json - 使用快照角色私钥签名
- timestamp.json - 使用时间戳角色私钥签名

### 3. 传输安全

建议使用 HTTPS 而不是 HTTP 来提供元数据和目标文件，以防止中间人攻击。

## 最佳实践

### 1. 自动化部署

使用 CI/CD 流程自动化新版本的发布：

1. 构建新版本应用包
2. 使用 TUF 工具更新元数据
3. 自动部署到服务器

### 2. 版本管理

- 遵循语义化版本控制 (SemVer)
- 保持元数据文件的版本历史
- 提供回滚机制

### 3. 监控和日志

- 监控元数据文件的访问情况
- 记录客户端更新请求
- 设置异常检测和告警

## 故障排除

### 1. 客户端无法连接服务器

检查：
- 服务器是否正常运行
- 网络连接是否正常
- 防火墙设置是否正确

### 2. 元数据验证失败

检查：
- 元数据文件是否完整
- 签名是否有效
- 客户端时间是否正确

### 3. 目标文件下载失败

检查：
- 目标文件是否存在
- 文件权限是否正确
- 磁盘空间是否充足