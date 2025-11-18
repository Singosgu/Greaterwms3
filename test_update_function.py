#!/usr/bin/env python3
"""
测试更新功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.updater import BomiotUpdater

def test_update_function():
    """测试更新功能"""
    try:
        print("创建BomiotUpdater实例...")
        # 使用较低的版本号来测试更新
        updater = BomiotUpdater('Bomiot', '1.0.0')
        print("BomiotUpdater实例创建成功")
        
        # 测试初始化客户端
        print("初始化TUF客户端...")
        # 使用本地文件URL进行测试
        repository_url = "file:///" + os.path.abspath("updates").replace("\\", "/") + "/"
        success = updater.initialize_client(repository_url)
        if success:
            print("TUF客户端初始化成功")
            print("正在检查更新...")
            # 检查更新
            update_available = updater.check_for_updates()
            if update_available:
                print("✓ 发现可用更新!")
                return True
            else:
                print("✗ 无可用更新或更新失败")
                return False
        else:
            print("TUF客户端初始化失败")
            return False
    except Exception as e:
        print(f"测试时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_update_function()
    if success:
        print("\n✓ 更新检查测试成功!")
    else:
        print("\n✗ 更新检查测试失败!")