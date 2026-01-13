## 项目速览

本仓库实现一个基于 PyQt5 的独立“数字进制转换器”对话框，主要逻辑在 `number_conversion_dialog.py`，自定义控件在 `widgets/widgets.py`，资源路径/打包兼容工具在 `widgets/utils.py`。UI 采用信号槽、标志位避免循环更新、并提供 64 位位键盘与有符号/无符号、数据宽度选项（QWORD/DWORD/WORD/BYTE）。

## 立即可做的操作（示例命令）
- **运行（开发）**: 在仓库根目录执行 `python number_conversion_dialog.py [初始值] [HEX|DEC]`，例如 `python number_conversion_dialog.py 12345 DEC`。
- **打包（PyInstaller）**: 推荐使用仓内 spec 或命令：

  pyinstaller --onefile --windowed --icon="resources/HOWE_LOGO.ico" --add-data="resources;resources" number_conversion_dialog.py

  或直接使用 `number_conversion_dialog.spec`（已包含在仓库）以保留自定义选项。

## 关键约定与模式（对 AI 助手非常重要）
- **入口/运行模式**: `number_conversion_dialog.py` 既可作为包导入也可独立运行。文件顶部使用动态 `sys.path.insert` 与多重 import-fallback（`.`、相对 `widgets`、全路径 `number_converter_project.widgets`、最后的模块别名导入）。编辑或重构导入时保留这些备选路径以保证两种运行模式兼容。
- **资源加载**: 使用 `widgets/utils.py::resource_path()` 做资源定位，应在改动图标或添加资源时调用该函数，避免打包后路径失效。
- **自定义控件**: `widgets/widgets.py::ExpandingTextEdit` 是替代 `QLineEdit` 的可扩展文本框，提供 `.setText()` 和 `.text()` 以兼容调用者。修改文本相关逻辑应优先考虑此类方法。
- **防循环更新**: 全局字段 `self.updating` 在 `NumberConversionDialog` 中广泛使用以避免信号链触发递归更新。任何对文本域/位键盘批量更新必须在前后设置该标志。
- **位映射**: 位键盘用 `self.bits` 长度为 64，且按钮索引 i 对应位的权重为 `1 << (63 - i)`（高位在前）。有关 bit 操作、截断与范围判定，参见 `get_unsigned_value()`, `set_bit_keyboard_value()` 与 `get_bit_count()`。
- **数据宽度与有符号**: 支持 `BYTE, WORD, DWORD, QWORD`；有符号模式通过 `self.is_signed` 控制显示与补码处理，格式化函数（`format_hex/dec/bin/oct`）会基于当前宽度处理值与填充。
- **延迟初始化**: 使用 `QTimer.singleShot(100, ...)` 延迟执行初始转换，变更初始化逻辑时请保留或调整该延迟以避免 UI 未完全建立就访问控件。

## 代码片段示例（便于补全与重构）
- 防循环更新模式：

  self.updating = True
  try:
      # 批量更新文本或按钮状态
  finally:
      self.updating = False

- 位到整数及反向转换：

  # 位数组转无符号值
  value = 0
  for i, bit in enumerate(self.bits):
      if bit:
          value |= (1 << (63 - i))

  # 设置位数组并同步按钮
  for i in range(64):
      self.bits[i] = 1 if (value & (1 << (63 - i))) else 0

## 编辑/重构注意事项
- 不要移除 import-fallback 逻辑，除非你更新了 README 并确保所有使用场景（包内导入与独立运行）已统一。
- 修改 UI 控件签名时同时更新 `ExpandingTextEdit` 的兼容方法（`.setText()`/`.text()`）。
- 调整数据宽度或补码逻辑时，更新相关的 `get_bit_count()`, `get_value_range()`, 以及所有 `format_*` 函数以保持一致性。

## 调试与常见问题
- 如果运行时找不到资源（图标等），优先使用 `widgets/utils.py::resource_path()` 的返回路径进行调试打印，确认 `sys._MEIPASS`（打包）或仓库相对路径（开发）是否正确。
- 如果出现输入框循环更新或 UI 卡顿，搜索 `self.updating` 使用点来定位未正确设置/清除的地方。

## 参考文件
- 项目入口: [number_conversion_dialog.py](number_conversion_dialog.py)
- 自定义控件: [widgets/widgets.py](widgets/widgets.py)
- 资源定位: [widgets/utils.py](widgets/utils.py)
- 项目说明: [README.md](README.md)

---
如果这些点有不明确的地方，告诉我想要更详细的哪一节（例如位映射、打包流程或导入兼容），我会迭代更新。
