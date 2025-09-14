import sys
import os
import subprocess

def build_exe():
    # 基础参数
    cmd = [
        "python", "-m", "nuitka",
        "--standalone",  # Mode
        "--jobs=16",
        "--windows-company-name=Bomiot",  # 公司名称
        "--windows-product-name=Bomiot",  # 产品名称
        "--windows-file-version=1.0.0",  # 文件版本
        "--windows-product-version=1.0.0",  # 产品版本
        "--windows-icon-from-ico=logo.ico",  # 图标文件
        "--clean-cache=all",  # 清理临时文件
        "--assume-yes-for-downloads",  # 自动下载缺失的库
        "--remove-output",  # 移除输出目录
        "--no-pyi-file",  # 不生成.pyi文件
        "--output-dir=dist",
        "--output-filename=bomiot",  # 指定输出文件名
        "--include-data-dir=dbs=dbs",  # 包含数据库目录
        "--include-data-dir=logs=logs",  # 包含日志目录
        "--include-data-dir=main=main",  # 包含日志目录
        "--include-data-file=setup.ini=setup.ini",  # 包含setup.ini文件
        "--verbose",  # 输出详细信息
        "--lto=yes",  # 开启链接时优化
        # 因为bomiot是虚拟环境中的包，不需要--include-package参数，让Nuitka自动跟随导入
        # 包含必要的包和数据文件
        "--include-package=bomiot",
        "--include-package=django",
        "--include-package=orjson",
        "--include-package=uvicorn",
        "--include-package=pandas",
        "--include-package=openpyxl",
        "--include-package=watchdog",
        "--include-package=tomlkit",
        "--include-package=psutil",
        "--include-package=xlsxwriter",
        "--include-package=requests",
        "--include-package=httptools",
        "--include-package=aiofiles",
        "--include-package=starlette",
        #djanogo 相关
        '--module-parameter=django-settings-module=bomiot.server.server.settings',
        # 新增：包含 tufup 及其依赖（确保更新功能正常）
        "--include-package=tufup",
        "--include-package=securesystemslib",  # tufup 依赖
        "--include-package=cryptography",     # tufup 依赖
        # 启动脚本
        "launcher.py",
    ]
    
    # 确保输出目录存在
    os.makedirs("dist", exist_ok=True)
    
    print(f"执行打包命令: {' '.join(cmd)}")
    # 执行编译
    try:
        subprocess.run(cmd, check=True)
        print("打包成功! 可执行文件位于 dist/bomiot.exe")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()