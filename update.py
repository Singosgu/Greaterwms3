import os
import sys
from tufup.client import Client

def run_update():
    """
    检查并执行应用程序的自动更新。
    """
    try:
        # Nuitka 打包后，tufup 插件会将服务器 URL 嵌入到可执行文件中。
        # 这里你可以直接实例化 Client，它会自动获取该 URL。
        # 如果你没有在 Nuitka 参数中指定 auto-update-url-spec，
        # 你需要在这里提供硬编码的 URL，例如：Client("https://your.update.server")
        client = Client('http://3.135.61.8:8008/media/update')

        # 检查并下载更新
        print("正在检查更新...")
        result = client.update()
        
        if result:
            new_version = result.get('new_version')
            print(f"更新成功！已更新到版本：{new_version}")
            print("请重新启动应用程序以应用更新。")
            
            # 返回 True，告诉主应用需要重启
            return True
        else:
            print("没有可用的新版本。")
            return False

    except Exception as e:
        print(f"自动更新失败：{e}")
        return False

if __name__ == "__main__":
    # 如果单独运行这个文件，它将执行更新并退出
    run_update()