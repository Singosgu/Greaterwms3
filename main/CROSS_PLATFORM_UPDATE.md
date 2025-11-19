# 跨平台更新机制详解

## 1. 服务器端跨平台更新区分机制

服务器通过URL路径来区分不同平台的更新，具体实现如下：

### 1.1 URL结构设计
```
基础URL: http://3.135.61.8:8008/media/update
Windows平台: http://3.135.61.8:8008/media/update/win
```

### 1.2 服务器目录结构
```
/media/update/
└── win/
    ├── metadata/
    │   ├── root.json
    │   ├── targets.json
    │   ├── snapshot.json
    │   └── timestamp.json
    └── targets/
        └── Bomiot-1.2.0.zip
```

## 2. 客户端跨平台适配机制

### 2.1 平台检测
客户端通过Python的platform模块检测当前运行平台：
```python
import platform

system = platform.system().lower()
if system == 'windows':
    platform_name = 'windows'
else:
    platform_name = 'windows'  # 默认为Windows
```

### 2.2 平台特定URL获取
客户端根据检测到的平台从配置文件中获取对应的更新URL：
```json
{
  "app_name": "Bomiot",
  "current_version": "1.1.1",
  "update_server_url": "http://3.135.61.8:8008/media/update",
  "platform_specific_urls": {
    "windows": "http://3.135.61.8:8008/media/update/win"
  }
}
```

### 2.3 动态服务器地址切换
客户端支持动态更新服务器地址，实现服务器迁移后的无缝更新：
1. 从更新包中读取新的服务器配置
2. 将新地址保存到本地配置文件
3. 后续更新使用新地址

## 3. 更新包格式差异

不同平台使用不同的更新包格式：
- **Windows**: ZIP格式 (.zip)

## 4. 跨平台脚本生成

根据不同平台生成相应的更新脚本：

### 4.1 Windows批处理脚本 (update.bat)
```batch
@echo off
REM Bomiot Windows 更新脚本
cd /d "%APP_DIR%"
echo 正在更新应用程序...
REM 更新命令
echo 更新完成
REM 重启应用程序
"%PYTHON_EXE%" %APP_ARGS%
```

## 5. 重启机制

### 5.1 Windows
```python
subprocess.Popen([sys.executable] + sys.argv)
```

## 6. CI/CD自动化构建

GitHub Actions工作流为Windows平台生成相应的TUF元数据：
1. Windows运行器生成Windows平台元数据
2. 元数据和目标文件部署到对应的URL路径

## 7. 部署建议

### 7.1 服务器配置
1. 在Web服务器上创建对应的目录结构
2. 为Windows平台维护独立的TUF仓库
3. 确保URL路径与客户端配置一致

### 7.2 更新发布流程
1. 为Windows平台构建相应的应用程序包
2. 使用TUF工具为Windows平台生成元数据
3. 将元数据和目标文件部署到对应的平台目录
4. 客户端自动检测并下载适用于当前平台的更新

这种设计确保了Windows平台的客户端能够正确获取适用于自己平台的更新，同时保持了系统的安全性和一致性。