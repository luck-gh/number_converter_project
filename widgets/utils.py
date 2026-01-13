import os
import sys

# 优先使用共享实现, 回退到本地实现以保证兼容性
try:
    from common_utils.resource import resource_path
except Exception:
    def resource_path(relative_path):
        """
        获取资源的绝对路径, 兼容开发环境和PyInstaller打包环境。
        在打包环境中, 会尝试在相对路径和根路径下寻找资源。
        """
        try:
            # PyInstaller创建的临时文件夹
            base_path = sys._MEIPASS

            # 尝试完整的相对路径
            path1 = os.path.join(base_path, relative_path)
            if os.path.exists(path1):
                return path1

            # 尝试只在根目录下寻找文件名 (处理--add-data data.txt:.的情况)
            path2 = os.path.join(base_path, os.path.basename(relative_path))
            if os.path.exists(path2):
                return path2

            # 如果都找不到, 返回原始的相对路径 (可能会失败, 但作为后备)
            return path1

        except Exception:
            # 在开发环境中, 使用当前文件所在目录的父目录的父目录作为根目录
            # utils.py 在 number_converter_project/widgets/ 目录下, 所以其父目录的父目录是 number_converter_project/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)
