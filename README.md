# 数字进制转换器 (Number Converter)

这是一个独立的、基于 PyQt5 的数字进制转换工具, 提供了一个图形化界面, 用于在不同的数字基数（十六进制、十进制、二进制、八进制）之间进行实时转换。

## 主要功能

- **多进制实时转换**: 在十六进制 (HEX)、十进制 (DEC)、二进制 (BIN) 和八进制 (OCT) 之间进行同步转换。在一个输入框中修改数值, 其他所有输入框会立即更新。
- **可配置数据宽度**: 支持多种数据宽度 (QWORD/64位, DWORD/32位, WORD/16位, BYTE/8位), 并会根据所选宽度对输入值进行范围检查和截断。
- **有符号/无符号计算**: 支持在有符号和无符号模式之间切换, 并正确处理负数的补码表示。
- **交互式位键盘**: 提供一个64位的图形化位键盘, 用户可以直接点击切换任意位的值 (0/1), 并实时看到所有进制的变化。
- **命令行启动**: 支持通过命令行参数启动, 可以预设初始值和转换类型。
- **独立运行**: 该工具可以作为完全独立的应用程序运行, 无需依赖主串口工具。

## 如何运行

可以直接通过 Python 解释器运行 `number_conversion_dialog.py` 文件:

```bash
python number_conversion_dialog.py [初始值] [类型]
```

**参数说明:**

- `[初始值]` (可选): 要转换的初始数字, 例如 `12345` 或 `0x3039`。默认为 `0x0`。
- `[类型]` (可选): 初始值的类型, `HEX` 或 `DEC`。默认为 `HEX`。

**示例:**

```bash
# 启动并计算十进制数 12345
python number_conversion_dialog.py 12345 DEC

# 启动并计算十六进制数 0x1A2B
python number_conversion_dialog.py 0x1A2B HEX
```

## 文件结构

- `number_conversion_dialog.py`: 主对话框和应用入口, 包含所有UI和核心逻辑。
- `widgets.py`: 包含自定义的UI控件, 例如可自动扩展高度的文本框。
- `utils.py`: 提供辅助函数, 例如用于在打包后定位资源的 `resource_path`。
- `HOWE_LOGO.ico`: 应用程序的图标。

## 使用的模块

### 核心依赖

- **PyQt5**: 主要的 GUI 框架
  - `PyQt5.QtWidgets`: 提供所有基础控件 (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QFrame, QGridLayout, QWidget, QTextEdit)
  - `PyQt5.QtCore`: 核心功能 (Qt, QTimer)
  - `PyQt5.QtGui`: 图形界面 (QFont, QIcon)

### 自定义模块

#### widgets/widgets.py
- **ExpandingTextEdit**: 自定义文本编辑框
  - 自动根据内容调整高度
  - 支持自动换行控制
  - 无滚动条设计，适合紧凑布局

#### widgets/utils.py
- **resource_path()**: 资源路径处理函数
  - 兼容开发环境和 PyInstaller 打包环境
  - 自动定位资源文件路径

### 标准库依赖
- `sys`: 系统相关功能
- `os`: 文件系统操作

## UI 风格规范

### 窗口设置
- **窗口标题**: 使用描述性标题，如 "数字进制转换计算器_GHowe"
- **窗口图标**: 使用 ICO 格式图标，通过 resource_path 加载
- **窗口大小**: 默认 450x600 像素
- **模态设置**: 非模态对话框 (`setModal(False)`)
- **关闭行为**: 自动删除 (`setAttribute(Qt.WA_DeleteOnClose)`)

### 布局设计
- **主布局**: QVBoxLayout 垂直布局
- **分组**: 使用 QGroupBox 组织相关控件
- **网格布局**: QGridLayout 用于位键盘等规则排列
- **水平布局**: QHBoxLayout 用于标签和控件对齐
- **弹性空间**: 使用 `addStretch()` 实现控件左对齐

### 控件样式
- **字体**: 默认系统字体，可根据需要调整大小
- **颜色**: 使用系统默认颜色主题
- **间距**: 合理使用布局边距和控件间距
- **对齐**: 左对齐为主，必要时居中

### 自定义控件特性
- **ExpandingTextEdit**:
  - 初始不换行
  - 关闭滚动条
  - 动态高度调整
  - 最小高度为一行的 1.2 倍

### 事件处理
- **信号连接**: 使用 Qt 的信号槽机制
- **防循环更新**: 使用标志位防止递归更新
- **延迟执行**: 使用 QTimer.singleShot 延迟初始化操作

## 代码结构建议

### 文件组织
```
project/
├── main.py              # 应用入口
├── dialogs/             # 对话框模块
├── widgets/             # 自定义控件
│   ├── __init__.py
│   ├── widgets.py       # 自定义控件类
│   └── utils.py         # 工具函数
├── resources/           # 资源文件
└── utils.py             # 通用工具
```

### 导入策略
- 支持包内导入和独立运行
- 使用 try-except 处理不同导入场景
- 动态路径添加确保模块可访问

### 打包配置
- 使用 PyInstaller 打包
- `--onefile` 选项创建单文件应用
- `--windowed` 隐藏控制台
- `--icon` 设置应用图标
- `--add-data` 添加资源文件

## 最佳实践

1. **模块化**: 将 UI 控件和逻辑分离，便于复用
2. **资源管理**: 使用 resource_path 函数统一处理资源路径
3. **错误处理**: 在导入和资源加载时提供多重后备方案
4. **兼容性**: 确保代码可在不同环境下运行（开发/打包）
5. **用户体验**: 非模态对话框，允许同时操作多个界面

## 依赖安装

```bash
pip install PyQt5
pip install pyinstaller  # 用于打包
```

## 使用示例

在新的项目中，可以按以下方式复用这些模块：

```python
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout
from widgets.widgets import ExpandingTextEdit
from widgets.utils import resource_path

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        layout = QVBoxLayout(self)
        text_edit = ExpandingTextEdit()
        layout.addWidget(text_edit)
```

## 打包

```bash
pyinstaller --onefile --windowed --icon="resources/HOWE_LOGO.ico" --add-data="resources;resources" number_conversion_dialog.py
```
