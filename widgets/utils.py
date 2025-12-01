import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径, 兼容开发环境和PyInstaller打包环境"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 在开发环境中, __file__ 指向 utils.py
        # 我们需要向上两级找到工作区根目录
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)
