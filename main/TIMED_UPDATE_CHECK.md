# 定时更新检查配置说明

## 概述
本系统支持定时更新检查功能，可以配置更新检查的时间间隔，而不是实时监控文件系统变化。

## 配置方式

### 1. 通过 server_config.json 配置文件
在 `server_config.json` 文件中添加 `update_check_interval` 字段：

```json
{
  "app_name": "Bomiot",
  "current_version": "1.1.1",
  "update_server_url": "http://3.135.61.8:8008/media/update",
  "platform_specific_urls": {
    "windows": "http://3.135.61.8:8008/media/update/win",
    "mac": "http://3.135.61.8:8008/media/update/mac",
    "linux": "http://3.135.61.8:8008/media/update/linux"
  },
  "update_check_interval": 3600
}
```

### 2. 通过环境变量
可以使用 `BOMIOT_UPDATE_INTERVAL` 环境变量覆盖配置文件中的设置：

```bash
export BOMIOT_UPDATE_INTERVAL=3600
```

## 时间间隔说明
- 时间间隔单位为秒
- 默认值为3600秒（1小时）
- 最小建议值为60秒（1分钟）
- 最大值无限制，但建议不要超过86400秒（24小时）

## 启用定时更新检查
要启用定时更新检查功能，需要在 `server_config.json` 中设置：

```json
{
  "enable_file_watcher": true
}
```

或者通过环境变量：

```bash
export BOMIOT_FILE_WATCHER=true
```

## 注意事项
1. 定时更新检查会在单独的线程中运行，不会阻塞主程序
2. 如果更新检查过程中出现错误，系统会等待1分钟后重试
3. 定时更新检查的优先级低于手动触发的更新检查
4. 定时更新检查仅在程序启动后开始运行