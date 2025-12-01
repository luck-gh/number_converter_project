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

## 打包

```bash
pyinstaller --onefile --windowed --icon=resources/HOWE_LOGO.ico --add-data "widgets.py;." --add-data "utils.py;." number_conversion_dialog.py
```
