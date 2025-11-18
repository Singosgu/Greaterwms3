# Bomiot 增量自动更新系统

## 概述

本系统基于以下技术实现 Bomiot 应用的增量自动更新：

1. **tufup** - 确保更新安全性
2. **bsdiff4** - 减少更新体积
3. **watchdog** - 实现实时触发

## 系统架构

### 核心组件

1. **更新器 (updater.py)** - 主要的更新逻辑实现
2. **更新配置 (update_config.py)** - 更新相关的配置参数
3. **启动器 (launcher.py)** - 集成更新检查的主程序入口
4. **跨平台更新支持 (cross_platform_updater.py)** - 跨平台更新和重启支持

## 功能特性

### 1. 安全更新 (tufup)
- 基于 TUF (The Update Framework) 标准
- 数字签名验证确保更新包完整性
- 防止回滚攻击和中间人攻击

### 2. 增量更新 (bsdiff4)
- 仅下载变更部分，减少网络流量
- 二进制差分算法，高效压缩更新包
- 自动应用补丁生成新版本

### 3. 实时监控 (watchdog)
- 文件系统监控，自动触发更新检查
- 实时响应文件变更事件
- 无需手动检查更新

## 使用方法

### 1. 集成到项目

在 [launcher.py](file://e:\Github_desktop\Greaterwms3\launcher.py) 中已经集成了自动更新检查功能：

```python
# 在应用启动时检查更新
update_applied = check_and_apply_updates()
if update_applied:
    # 如果应用了更新，退出程序让用户重启
    print("程序已更新，请重新启动")
    splash.destroy()
    exit(0)
```

### 2. 配置更新参数

在 [update_config.py](file://e:\Github_desktop\Greaterwms3\main\update_config.py) 中配置更新参数：

```python
# 更新服务器配置
UPDATE_SERVER_URL = os.getenv("BOMIOT_UPDATE_URL", "http://localhost:8000/updates")
UPDATE_CHECK_INTERVAL = int(os.getenv("BOMIOT_UPDATE_INTERVAL", "3600"))  # 默认1小时检查一次

# 更新策略配置
ENABLE_AUTO_UPDATE = os.getenv("BOMIOT_AUTO_UPDATE", "true").lower() == "true"
ENABLE_INCREMENTAL_UPDATE = os.getenv("BOMIOT_INCREMENTAL_UPDATE", "true").lower() == "true"
ENABLE_FILE_WATCHER = os.getenv("BOMIOT_FILE_WATCHER", "false").lower() == "true"
```

## 安全机制

### 1. 完整性验证
- 使用 SHA256 哈希值验证更新包完整性
- 数字签名防止篡改

### 2. 备份与回滚
- 更新前自动备份当前版本
- 更新失败时自动回滚

### 3. 权限控制
- 限制更新包执行权限
- 防止恶意代码执行

## 增量更新流程

1. **生成补丁** - 使用 bsdiff4 生成新旧版本之间的差分补丁
2. **上传补丁** - 将补丁文件上传到更新服务器
3. **客户端检查** - 客户端定期检查是否有新版本
4. **下载补丁** - 下载差分补丁文件
5. **应用补丁** - 使用 bspatch4 应用补丁生成新版本
6. **验证更新** - 验证更新后文件的完整性
7. **重启应用** - 重启应用使用新版本

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| BOMIOT_UPDATE_URL | http://localhost:8000/updates | 更新服务器地址 |
| BOMIOT_UPDATE_INTERVAL | 3600 | 更新检查间隔（秒） |
| BOMIOT_AUTO_UPDATE | true | 是否启用自动更新 |
| BOMIOT_INCREMENTAL_UPDATE | true | 是否启用增量更新 |
| BOMIOT_FILE_WATCHER | false | 是否启用文件监视器 |

## 打包注意事项

使用 Nuitka 打包时，确保包含以下依赖：

```python
# build.py 中的配置
"--include-package=tufup",
"--include-package=securesystemslib",
"--include-package=cryptography",
"--include-package=watchdog",
"--include-package=bsdiff4",
```

## 故障排除

### 常见问题

1. **更新检查失败**
   - 检查网络连接
   - 验证更新服务器地址
   - 检查防火墙设置

2. **更新应用失败**
   - 检查磁盘空间
   - 验证文件权限
   - 查看日志文件

3. **增量更新失败**
   - 检查补丁文件完整性
   - 验证原文件未被修改

### 日志查看

更新日志保存在 `cache/update.log` 文件中。

## 最佳实践

1. **定期更新** - 建议每天检查一次更新
2. **测试环境** - 在生产环境部署前先在测试环境验证
3. **备份策略** - 定期备份重要数据
4. **监控告警** - 设置更新失败告警机制

## 扩展功能

### 1. 自定义更新策略
可以根据网络状况或用户偏好自定义更新策略。

### 2. 静默更新
支持后台静默更新，不影响用户正常使用。

### 3. 分阶段发布
支持灰度发布，逐步向用户推送更新。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个更新系统。