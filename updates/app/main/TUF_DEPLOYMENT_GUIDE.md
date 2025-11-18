# TUF部署指南：打包文件上传到服务器

## 概述

当您将打包后的文件上传到服务器时，**不需要**服务器重新签名，但需要理解TUF的安全机制和正确的部署流程。

## TUF签名机制详解

### 1. 签名在何处进行？

TUF的数字签名是在**生成更新包时**完成的，而不是在服务器上。具体来说：

1. **本地签名**：使用`tufup`工具在本地生成元数据时，会使用私钥对元数据进行签名
2. **私钥安全**：私钥必须安全保存，不能泄露给服务器或客户端
3. **公钥验证**：客户端使用公钥验证元数据的签名

### 2. 部署时的文件组成

部署到服务器的文件包括：

```
/media/update/
├── metadata/           # 元数据目录（已签名）
│   ├── root.json      # 根元数据（已签名）
│   ├── targets.json   # 目标元数据（已签名）
│   ├── snapshot.json  # 快照元数据（已签名）
│   └── timestamp.json # 时间戳元数据（已签名）
└── targets/           # 目标文件目录
    └── Bomiot-1.1.1.tar.gz  # 应用程序更新包
```

## 正确的部署流程

### 1. 本地生成更新包（已签名）

```python
# 本地生成新的更新版本
from tufup.repo import Repository
from pathlib import Path

# 加载现有仓库
repo = Repository(
    app_name="Bomiot",
    repo_dir=Path("updates"),
    keys_dir=Path("updates/keys")
)

# 添加新版本
repo.add_bundle(
    new_bundle_dir=Path("new_app_version"),
    new_version="1.2.0"
)

# 发布更新（使用私钥签名）
repo.publish_changes(private_key_dirs=[Path("updates/keys")])
```

### 2. 上传到服务器

将生成的文件直接上传到服务器，**不需要重新签名**：

```bash
# 上传元数据目录（已签名）
scp -r updates/metadata/ user@server:/var/www/media/update/metadata/

# 上传目标文件目录
scp -r updates/targets/ user@server:/var/www/media/update/targets/
```

## 为什么不需要服务器重新签名？

### 1. 安全性考虑

- **私钥保护**：私钥必须安全保存，不能存储在服务器上
- **防止篡改**：如果服务器被入侵，攻击者无法生成有效的签名
- **责任分离**：构建和部署职责分离，提高安全性

### 2. TUF设计原则

- **离线签名**：TUF设计为支持离线签名，签名和部署可以分离
- **完整性验证**：客户端验证元数据的完整性，确保未被篡改
- **信任链**：通过根密钥建立信任链，确保所有元数据可信

## 服务器端配置

### 1. Web服务器配置

确保Web服务器正确配置以提供文件：

```nginx
# Nginx配置示例
server {
    listen 80;
    server_name your-domain.com;
    
    location /media/update/ {
        alias /var/www/media/update/;
        autoindex on;
        
        # 确保JSON文件正确提供
        location ~* \.json$ {
            add_header Content-Type application/json;
        }
    }
}
```

### 2. 文件权限设置

```bash
# 设置正确的文件权限
chmod -R 644 /var/www/media/update/metadata/
chmod -R 644 /var/www/media/update/targets/
chown -R www-data:www-data /var/www/media/update/
```

## 跨平台部署

### 1. 目录结构

```
/media/update/
├── win/               # Windows平台
│   ├── metadata/
│   └── targets/
├── mac/               # macOS平台
│   ├── metadata/
│   └── targets/
└── linux/             # Linux平台
    ├── metadata/
    └── targets/
```

### 2. 部署脚本

```bash
# 部署Windows版本
scp -r updates_win/metadata/ user@server:/var/www/media/update/win/metadata/
scp -r updates_win/targets/ user@server:/var/www/media/update/win/targets/

# 部署macOS版本
scp -r updates_mac/metadata/ user@server:/var/www/media/update/mac/metadata/
scp -r updates_mac/targets/ user@server:/var/www/media/update/mac/targets/

# 部署Linux版本
scp -r updates_linux/metadata/ user@server:/var/www/media/update/linux/metadata/
scp -r updates_linux/targets/ user@server:/var/www/media/update/linux/targets/
```

## 安全最佳实践

### 1. 密钥管理

- **离线存储**：私钥应离线存储，使用时才加载
- **备份保护**：对私钥进行加密备份
- **定期轮换**：定期轮换密钥以提高安全性

### 2. 传输安全

- **HTTPS**：使用HTTPS提供元数据和目标文件
- **完整性校验**：在传输前后校验文件完整性
- **访问控制**：限制对元数据目录的访问

### 3. 监控和审计

- **日志记录**：记录所有部署操作
- **变更监控**：监控文件变更
- **定期检查**：定期检查签名有效性

## 常见问题解答

### Q: 如果服务器被入侵怎么办？
A: 由于私钥不在服务器上，攻击者无法生成有效签名。客户端会拒绝接受被篡改的元数据。

### Q: 如何更新根密钥？
A: 需要生成新的根元数据，并通过安全渠道分发给客户端。

### Q: 可以自动化部署流程吗？
A: 可以使用CI/CD工具自动化部署，但签名步骤必须在安全环境中进行。

## 总结

打包后的文件上传到服务器时：

1. ✅ **不需要**服务器重新签名
2. ✅ **直接上传**已签名的元数据文件
3. ✅ **确保私钥安全**，不要存储在服务器上
4. ✅ **使用HTTPS**提供文件以确保传输安全
5. ✅ **定期监控**服务器文件完整性

这种设计确保了TUF安全更新机制的有效性，同时简化了部署流程。