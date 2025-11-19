# 平台特定更新服务器URL

## 概述

本文档说明了如何为Windows平台配置特定的更新服务器URL，以支持分平台的更新管理。

## 配置文件结构

在 `main/server_config.json` 文件中，我们添加了平台特定URL的配置：

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

## 实现细节

### 1. 平台检测

系统会自动检测当前运行平台：

- **Windows**: `windows`

### 2. URL选择优先级

URL选择遵循以下优先级：

1. **动态配置文件中的URL** - 如果存在动态配置文件且包含URL，则优先使用
2. **平台特定URL** - 根据当前平台从配置文件中选择对应URL
3. **默认URL** - 如果没有平台特定URL，则使用通用的 `update_server_url`

### 3. 配置读取

在 `main/update_config.py` 中，系统会根据当前平台读取相应的URL：

```python
# 根据平台获取特定的更新服务器URL
platform_specific_urls = server_config.get('platform_specific_urls', {})
if CURRENT_PLATFORM in platform_specific_urls:
    UPDATE_SERVER_URL = platform_specific_urls[CURRENT_PLATFORM]
else:
    # 如果没有平台特定的URL，则使用通用URL
    UPDATE_SERVER_URL = server_config.get('update_server_url', UPDATE_SERVER_URL)
```

## 跨平台支持

### CrossPlatformUpdater 类

在 `main/cross_platform_updater.py` 中，添加了 `get_platform_specific_url` 方法：

```python
def get_platform_specific_url(self, base_url: str) -> str:
    """
    获取平台特定的更新服务器URL
    """
    # 从server_config.json读取平台特定的URL
    try:
        from main.update_config import SERVER_CONFIG_FILE
        if SERVER_CONFIG_FILE.exists():
            with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                server_config = json.load(f)
                platform_specific_urls = server_config.get('platform_specific_urls', {})
                if self.platform_name in platform_specific_urls:
                    return platform_specific_urls[self.platform_name]
    except Exception as e:
        logger.error(f"读取平台特定URL时出错: {e}")
    
    # 如果没有找到平台特定的URL，则返回基础URL加上平台路径
    if not base_url.endswith('/'):
        base_url += '/'
    return f"{base_url}{self.platform_name}/"
```

### BomiotUpdater 类

在 `main/updater.py` 中，更新了 `get_dynamic_update_server_url` 方法以支持平台特定URL：

```python
def get_dynamic_update_server_url(self, default_url: str) -> str:
    """
    获取动态更新服务器地址
    """
    try:
        # 首先尝试获取平台特定的URL
        platform_specific_url = self._get_platform_specific_url(default_url)
        
        if DYNAMIC_UPDATE_CONFIG_FILE.exists():
            with open(DYNAMIC_UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                dynamic_url = config.get('update_server_url')
                if dynamic_url:
                    logger.info(f"使用动态更新服务器地址: {dynamic_url}")
                    return dynamic_url
        # 如果没有动态配置文件，使用平台特定的默认地址
        logger.info(f"使用平台特定的更新服务器地址: {platform_specific_url}")
        return platform_specific_url
    except Exception as e:
        logger.error(f"读取动态更新配置时出错: {e}")
        return default_url
```

## 测试验证

可以通过以下方式验证功能：

```bash
cd "e:\Github_desktop\Greaterwms3" && python -c "
from main.cross_platform_updater import cross_platform_updater
from main.update_config import SERVER_CONFIG_FILE
import json

print('当前平台:', cross_platform_updater.platform_name)
if SERVER_CONFIG_FILE.exists():
    with open(SERVER_CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        platform_urls = config.get('platform_specific_urls', {})
        if cross_platform_updater.platform_name in platform_urls:
            print('平台特定URL:', platform_urls[cross_platform_updater.platform_name])
"
```

## 优势

1. **分平台管理** - 可以为Windows平台维护独立的更新服务器
2. **灵活配置** - 支持动态URL覆盖和平台特定URL的组合
3. **向后兼容** - 如果没有平台特定配置，会回退到通用URL
4. **自动检测** - 系统自动检测当前平台并选择相应URL

## 使用场景

1. **不同平台不同更新策略** - 可以为Windows平台设置不同的更新频率或内容
2. **服务器负载均衡** - 可以将Windows平台的更新请求分散到不同服务器
3. **平台特定功能更新** - 可以为Windows平台提供专门的更新内容
4. **灰度发布** - 可以先在Windows平台发布更新进行测试