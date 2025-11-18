#!/usr/bin/env python3
"""
测试TUF客户端初始化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.updater import BomiotUpdater

def test_tuf_client():
    """测试TUF客户端初始化"""
    try:
        print("创建BomiotUpdater实例...")
        updater = BomiotUpdater('Bomiot', '1.1.1')
        print("BomiotUpdater实例创建成功")
        
        # 测试初始化客户端
        print("初始化TUF客户端...")
        # 使用本地文件URL进行测试
        repository_url = "file:///" + os.path.abspath("updates").replace("\\", "/")
        success = updater.initialize_client(repository_url)
        if success:
            print("TUF客户端初始化成功")
            return True
        else:
            print("TUF客户端初始化失败")
            return False
    except Exception as e:
        print(f"TUF客户端测试时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tuf_client()
    if success:
        print("\nTUF客户端测试成功!")
    else:
        print("\nTUF客户端测试失败!")