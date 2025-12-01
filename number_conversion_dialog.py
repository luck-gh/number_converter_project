import sys
import os

# 确保脚本可以作为独立文件运行, 动态添加其父目录到sys.path
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLabel, QComboBox, QPushButton, QCheckBox,
                             QDialogButtonBox, QMessageBox, QFrame, QGridLayout, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from widgets.widgets import ExpandingTextEdit
from widgets.utils import resource_path

class NumberConversionDialog(QDialog):
    """数字转换对话框 - 支持实时同步更新和复制功能, 包含内置位键盘"""
    def __init__(self, selected_text="", conversion_type="HEX", parent=None):
        super().__init__(parent)
        self.selected_text = selected_text.strip() if "" != selected_text else selected_text
        self.conversion_type = conversion_type
        self.updating = False  # 防止循环更新
        self.is_signed = False  # 默认为无符号模式
        self.data_width = "DWORD"  # 默认32位

        # 位键盘相关属性
        self.bits = [0] * 64  # 64位数据, 初始全为0
        self.bit_buttons = []  # 存储所有位按钮

        # 独立运行时设置窗口标题
        if parent is None:
            self.setWindowTitle("数字进制转换计算器_GHowe")
            self.setWindowIcon(QIcon(resource_path("resources/HOWE_LOGO.ico")))
        else:
            if conversion_type == "HEX":
                self.setWindowTitle("HEX 计算_GHowe")
            else:
                self.setWindowTitle("DEC 计算_GHowe")

        # 改为非模态对话框, 允许用户同时操作其他界面
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭时自动删除

        self.resize(450, 600)  # 调整大小以容纳所有控件
        self.init_ui()

        # 延迟执行初始转换, 确保界面完全初始化
        QTimer.singleShot(100, self.perform_initial_conversion)

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 原始文本显示
        original_layout = QHBoxLayout()
        self.original_label = QLabel(self.selected_text)
        if "" == self.selected_text:
            headtext = ""
            self.selected_text = "0x0"
        else:
            headtext = "原始文本:"
        original_layout.addWidget(QLabel(headtext))
        original_layout.addWidget(self.original_label)
        original_layout.addStretch()

        # 数据宽度选择和有符号选择
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("数据宽度:"))
        self.width_combo = QComboBox()
        self.width_combo.addItems(["QWORD", "DWORD", "WORD", "BYTE"])
        self.width_combo.setCurrentText(self.data_width)
        self.width_combo.currentTextChanged.connect(self.on_width_changed)
        width_layout.addWidget(self.width_combo)
        width_layout.addStretch()

        # 添加有符号/无符号选择
        self.signed_checkbox = QCheckBox("有符号")
        self.signed_checkbox.setChecked(self.is_signed)
        self.signed_checkbox.toggled.connect(self.on_signed_toggled)
        width_layout.addWidget(self.signed_checkbox)

        layout.addLayout(original_layout)
        layout.addLayout(width_layout)

        # 转换结果
        result_group = QGroupBox("进制转换 (可编辑)")
        result_layout = QVBoxLayout(result_group)

        # 使用网格布局确保标签对齐
        grid_layout = QGridLayout()

        # 十六进制
        self.hex_edit = ExpandingTextEdit()
        self.hex_edit.textChanged.connect(lambda: self.on_hex_changed(self.hex_edit.toPlainText()))
        grid_layout.addWidget(QLabel("十六进制"), 0, 0)
        grid_layout.addWidget(QLabel("(HEX):"), 0, 1)
        grid_layout.addWidget(self.hex_edit, 0, 2)

        # 十进制
        self.dec_edit = ExpandingTextEdit()
        self.dec_edit.textChanged.connect(lambda: self.on_dec_changed(self.dec_edit.toPlainText()))
        grid_layout.addWidget(QLabel("十进制"), 1, 0)
        grid_layout.addWidget(QLabel("(DEC):"), 1, 1)
        grid_layout.addWidget(self.dec_edit, 1, 2)

        # 二进制
        self.bin_edit = ExpandingTextEdit()
        self.bin_edit.textChanged.connect(lambda: self.on_bin_changed(self.bin_edit.toPlainText()))
        grid_layout.addWidget(QLabel("二进制"), 2, 0)
        grid_layout.addWidget(QLabel("(BIN):"), 2, 1)
        grid_layout.addWidget(self.bin_edit, 2, 2)

        # 八进制
        self.oct_edit = ExpandingTextEdit()
        self.oct_edit.textChanged.connect(lambda: self.on_oct_changed(self.oct_edit.toPlainText()))
        grid_layout.addWidget(QLabel("八进制"), 3, 0)
        grid_layout.addWidget(QLabel("(OCT):"), 3, 1)
        grid_layout.addWidget(self.oct_edit, 3, 2)

        # 设置列的比例, 确保输入框可以扩展
        grid_layout.setColumnStretch(2, 1)
        result_layout.addLayout(grid_layout)
        layout.addWidget(result_group)

        # 错误信息
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        # 位键盘区域 - 改进布局, 添加固定宽度的组框架
        bit_keyboard_group = QGroupBox("位键盘")
        bit_keyboard_layout = QVBoxLayout(bit_keyboard_group)

        # 标题
        title_label = QLabel("位键盘 (点击切换 0/1)")
        title_label.setAlignment(Qt.AlignCenter)
        bit_keyboard_layout.addWidget(title_label)

        # 创建4行, 每行4组, 每组4位
        for row in range(4):  # 4行
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(1)  # 减小组间间距
            row_layout.setContentsMargins(0, 0, 0, 0)

            # 每行4组
            for group in range(4):  # 每行4组
                # 创建组框架
                group_frame = QFrame()
                group_frame.setFrameStyle(QFrame.Box)  # 添加边框
                group_frame.setLineWidth(0)
                group_frame.setFixedWidth(100)  # 固定宽度
                group_layout = QHBoxLayout(group_frame)
                group_layout.setSpacing(0)  # 减小组内间距
                group_layout.setContentsMargins(1, 1, 1, 1)

                # 在组内创建4个位按钮和标签
                for bit_in_group in range(4):
                    # 计算全局位索引
                    bit_index = row * 16 + group * 4 + bit_in_group

                    # 创建容器
                    bit_widget = QWidget()
                    bit_layout = QVBoxLayout(bit_widget)
                    bit_layout.setContentsMargins(1, 1, 1, 1)
                    bit_layout.setSpacing(1)
                    bit_layout.setAlignment(Qt.AlignCenter)

                    # 创建位按钮 (无文本)
                    bit_btn = QPushButton("")
                    bit_btn.setFixedSize(20, 20)
                    bit_btn.setCheckable(True)
                    bit_btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #ffffff;
                            border: 1px solid #000ccc;
                        }}
                        QPushButton:checked {{
                            background-color: #4CAF50;
                        }}
                        QPushButton:disabled {{
                            background-color: #e0e0e0;
                            border: 1px solid #d0d0d0;
                        }}
                    """)

                    # 创建位标签 (仅在组的开始和结束)
                    if bit_in_group == 0 or bit_in_group == 3:
                        bit_label = QLabel(f"{63 - bit_index}")
                    else:
                        bit_label = QLabel("") # 空白标签占位
                    bit_label.setAlignment(Qt.AlignCenter)
                    bit_label.setFont(QFont("Arial", 7))

                    # 连接点击事件
                    bit_btn.clicked.connect(lambda checked, idx=bit_index: self.on_bit_clicked(idx))

                    # 添加到布局
                    bit_layout.addWidget(bit_btn)
                    bit_layout.addWidget(bit_label)

                    group_layout.addWidget(bit_widget)
                    self.bit_buttons.append(bit_btn)

                # 将组框架添加到行布局
                row_layout.addWidget(group_frame)

            # 将行添加到主布局
            bit_keyboard_layout.addWidget(row_widget)

        # 添加控制按钮
        control_layout = QHBoxLayout()

        clear_btn = QPushButton("全清0")
        clear_btn.clicked.connect(self.clear_all_bits)
        control_layout.addWidget(clear_btn)

        set_btn = QPushButton("全置1")
        set_btn.clicked.connect(self.set_all_bits)
        control_layout.addWidget(set_btn)

        invert_btn = QPushButton("取反")
        invert_btn.clicked.connect(self.invert_all_bits)
        control_layout.addWidget(invert_btn)

        bit_keyboard_layout.addLayout(control_layout)
        layout.addWidget(bit_keyboard_group)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 添加复制按钮 - 使用网格布局以节省空间
        copy_buttons_layout = QGridLayout()

        copy_hex_btn = QPushButton("复制 HEX")
        copy_hex_btn.clicked.connect(lambda: self.copy_to_clipboard(self.hex_edit.text()))
        copy_buttons_layout.addWidget(copy_hex_btn, 0, 0)

        copy_dec_btn = QPushButton("复制 DEC")
        copy_dec_btn.clicked.connect(lambda: self.copy_to_clipboard(self.dec_edit.text()))
        copy_buttons_layout.addWidget(copy_dec_btn, 0, 1)

        copy_bin_btn = QPushButton("复制 BIN")
        copy_bin_btn.clicked.connect(lambda: self.copy_to_clipboard(self.bin_edit.text()))
        copy_buttons_layout.addWidget(copy_bin_btn, 1, 0)

        copy_oct_btn = QPushButton("复制 OCT")
        copy_oct_btn.clicked.connect(lambda: self.copy_to_clipboard(self.oct_edit.text()))
        copy_buttons_layout.addWidget(copy_oct_btn, 1, 1)

        layout.addLayout(copy_buttons_layout)
        layout.addWidget(button_box)

    # 位键盘相关方法
    def on_width_changed(self, width_text):
        """数据宽度改变事件"""
        # 提取宽度类型
        self.data_width = width_text

        # 更新位键盘显示
        self.update_bit_keyboard_state()

        # 检查当前值是否超出范围
        self.check_value_range()

        # 更新所有显示的格式
        self.update_all_displays()

    def update_bit_keyboard_state(self):
        """更新位键盘状态 - 根据数据宽度禁用高位位"""
        # 确定要禁用的位范围
        disabled_end_map = {
            "BYTE": 56,   # 禁用 0-55 位 (高56位)
            "WORD": 48,   # 禁用 0-47 位 (高48位)
            "DWORD": 32,  # 禁用 0-31 位 (高32位)
            "QWORD": 0    # 不禁用任何位
        }
        disabled_end = disabled_end_map.get(self.data_width, 32)

        # 更新位按钮状态
        for i, btn in enumerate(self.bit_buttons):
            if i >= disabled_end:  # 低位位启用
                btn.setEnabled(True)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #000ccc;
                        font-weight: bold;
                        font-size: 10px;
                    }}
                    QPushButton:checked {{
                        background-color: #4CAF50;
                        color: white;
                    }}
                    QPushButton:disabled {{
                        background-color: #e0e0e0;
                        color: #a0a0a0;
                        border: 1px solid #d0d0d0;
                    }}
                """)
            else:  # 高位位禁用
                btn.setEnabled(False)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e0e0e0;
                        color: #a0a0a0;
                        border: 1px solid #d0d0d0;
                        font-weight: bold;
                        font-size: 10px;
                    }}
                    QPushButton:checked {{
                        background-color: #c0c0c0;
                        color: #808080;
                    }}
                """)
                # 确保禁用位显示为0
                self.bits[i] = 0
                btn.setChecked(False)

    def check_value_range(self):
        """检查当前值是否超出数据宽度范围"""
        try:
            current_value = self.get_current_value()
            max_value, min_value = self.get_value_range()

            if current_value > max_value or current_value < min_value:
                # 值超出范围, 显示警告
                self.error_label.setText(f"警告: 当前值超出{self.data_width}范围")
                # 自动截断值
                truncated_value = current_value & ((1 << self.get_bit_count()) - 1)
                if self.is_signed and truncated_value & (1 << (self.get_bit_count() - 1)):
                    # 如果是有符号且最高位为1, 转换为负数
                    truncated_value = truncated_value - (1 << self.get_bit_count())

                self.update_all_fields_with_value(truncated_value)
            else:
                self.error_label.setText("")

        except Exception as e:
            self.error_label.setText(f"范围检查错误: {str(e)}")

    def get_bit_count(self):
        """获取当前数据宽度的位数"""
        if self.data_width == "BYTE":
            return 8
        elif self.data_width == "WORD":
            return 16
        elif self.data_width == "DWORD":
            return 32
        else:  # QWORD
            return 64

    def get_value_range(self):
        """获取当前数据宽度下的值范围"""
        bit_count = self.get_bit_count()
        if self.is_signed:
            max_value = (1 << (bit_count - 1)) - 1
            min_value = -(1 << (bit_count - 1))
        else:
            max_value = (1 << bit_count) - 1
            min_value = 0
        return max_value, min_value

    def get_current_value(self):
        """获取当前显示的数值"""
        try:
            if self.conversion_type == "HEX":
                hex_text = self.hex_edit.text().replace("0x", "")
                hex_text = "".join(hex_text.split())
                return int(hex_text, 16)
            else:
                text = "".join(self.dec_edit.text().split())
                return int(text)
        except:
            return 0

    def update_all_fields_with_value(self, value):
        """使用指定值更新所有字段"""
        self.updating = True
        try:
            self.hex_edit.setText(self.format_hex(value))
            self.dec_edit.setText(self.format_dec(value))
            self.bin_edit.setText(self.format_bin(value))
            self.oct_edit.setText(self.format_oct(value))
            self.set_bit_keyboard_value(value)
        finally:
            self.updating = False

    def on_bit_clicked(self, bit_index):
        """位按钮点击事件 - 考虑数据宽度"""
        # 检查位是否启用
        if not self.bit_buttons[bit_index].isEnabled():
            return

        # 切换位的值 (0->1, 1->0)
        self.bits[bit_index] = 1 - self.bits[bit_index]

        # 更新按钮显示
        self.bit_buttons[bit_index].setChecked(self.bits[bit_index] == 1)

        # 获取当前值并检查范围
        new_value = self.get_unsigned_value()

        # 检查是否超出当前数据宽度范围
        bit_count = self.get_bit_count()
        max_unsigned = (1 << bit_count) - 1
        if new_value > max_unsigned:
            # 值超出范围, 显示警告
            self.error_label.setText(f"警告: 当前值超出{self.data_width}范围")
            # 截断值
            new_value = new_value & max_unsigned
            # 更新位键盘显示截断后的值
            self.set_bit_keyboard_value(new_value)
        else:
            self.error_label.setText("")

        # 直接调用位键盘值改变处理
        self.on_bit_keyboard_changed(new_value)

    def get_unsigned_value(self):
        """获取当前64位无符号数值"""
        value = 0
        for i, bit in enumerate(self.bits):
            if bit == 1:
                value |= (1 << (63 - i))  # 高位在前
        return value

    def set_bit_keyboard_value(self, value):
        """设置位键盘数值 (始终处理为无符号) """
        # 确保是无符号值
        value_unsigned = value & 0xFFFFFFFFFFFFFFFF

        # 更新位数组
        for i in range(64):
            self.bits[i] = 1 if (value_unsigned & (1 << (63 - i))) else 0

        # 更新按钮显示
        for i, btn in enumerate(self.bit_buttons):
            btn.setChecked(self.bits[i] == 1)

    def clear_all_bits(self):
        """将所有位清0"""
        for i in range(64):
            self.bits[i] = 0
            self.bit_buttons[i].setChecked(False)

        self.on_bit_keyboard_changed(0)

    def set_all_bits(self):
        """将所有位置1 - 考虑数据宽度限制"""
        bit_count = self.get_bit_count()
        # 只将有效位置1, 高位保持0
        for i in range(64):
            if i >= 64 - bit_count:  # 只设置有效低位
                self.bits[i] = 1
                self.bit_buttons[i].setChecked(True)
            else:  # 高位保持0
                self.bits[i] = 0
                self.bit_buttons[i].setChecked(False)

        new_value = self.get_unsigned_value()
        self.on_bit_keyboard_changed(new_value)

    def invert_all_bits(self):
        """将所有位取反 - 考虑数据宽度限制"""
        bit_count = self.get_bit_count()
        # 只取反有效位, 高位保持0
        for i in range(64):
            if i >= 64 - bit_count:  # 只取反有效低位
                self.bits[i] = 1 - self.bits[i]
                self.bit_buttons[i].setChecked(self.bits[i] == 1)
            else:  # 高位保持0
                self.bits[i] = 0
                self.bit_buttons[i].setChecked(False)

        new_value = self.get_unsigned_value()
        self.on_bit_keyboard_changed(new_value)

    def on_bit_keyboard_changed(self, value):
        """位键盘值改变 - 直接处理, 无需信号"""
        if self.updating:
            return

        self.updating = True
        try:
            # 处理有符号显示
            display_value = value
            if self.is_signed:
                # 如果最高位为1, 转换为有符号数
                if value & (1 << 63):
                    display_value = value - (1 << 64)

            # 更新所有进制字段
            self.hex_edit.setText(self.format_hex(display_value))
            self.dec_edit.setText(self.format_dec(display_value))
            self.bin_edit.setText(self.format_bin(display_value))
            self.oct_edit.setText(self.format_oct(display_value))

            self.error_label.setText("")
        except Exception as e:
            self.error_label.setText(f"位键盘更新错误: {str(e)}")
        finally:
            self.updating = False

    def on_signed_toggled(self, checked):
        """有符号/无符号切换"""
        self.is_signed = checked

        # 获取当前显示的值
        try:
            if self.conversion_type == "HEX":
                hex_text = self.hex_edit.text().replace("0x", "")
                hex_text = "".join(hex_text.split())
                if hex_text:
                    value = int(hex_text, 16)
                else:
                    value = 0
            else:
                dec_text = self.dec_edit.text()
                dec_text = "".join(dec_text.split())
                if dec_text:
                    value = int(dec_text)
                else:
                    value = 0
        except:
            value = 0

        # 重新计算当前值的显示
        self.update_all_fields_with_value(value)

    def update_all_displays(self):
        """根据当前有符号设置更新所有显示"""
        try:
            # 获取当前值
            if self.conversion_type == "HEX":
                hex_text = self.hex_edit.text().replace("0x", "")
                hex_text = "".join(hex_text.split())
                if not hex_text:
                    return
                value = int(hex_text, 16)
            else:
                dec_text = self.dec_edit.text()
                dec_text = "".join(dec_text.split())
                if not dec_text:
                    return
                value = int(dec_text)

            # 根据有符号设置重新格式化显示
            self.hex_edit.setText(self.format_hex(value))
            self.dec_edit.setText(self.format_dec(value))
            self.bin_edit.setText(self.format_bin(value))
            self.oct_edit.setText(self.format_oct(value))

        except Exception as e:
            print(f"更新显示错误: {str(e)}")

    def str_Alignment_for_len(self, str_value:str, alignment_length:int, align_from_end:bool=True, str_Alignment:int=0):
        """
        按照指定的对齐方式格式化字符串, 将其分割为多个段落的字符串。

        参数:
            str_value (str): 需要格式化的输入字符串
            alignment_length (int): 初始部分之后的对齐段落的长度
            align_from_end (bool, 可选): 如果为True, 根据字符串长度计算初始对齐长度；
                                        否则使用提供的initial_alignment值。默认为True
            initial_alignment (int, 可选): 当align_from_end为False时使用的初始对齐长度。默认为0

        返回:
            str: 格式化后的字符串, 各段落之间用空格分隔
        """
        # 根据对齐方式计算初始对齐长度
        if align_from_end:
            initial_alignment = len(str_value) % alignment_length
        # 如果align_from_end为False, 直接使用传入的initial_alignment值

        # 将字符串分割为多个段落
        # 第一部分：从开始到初始对齐长度
        # 后续部分：按照对齐长度进行分割
        formatted_segments = [str_value[:initial_alignment]] + [str_value[i:i + alignment_length] for i in range(initial_alignment, len(str_value), alignment_length)]

        # 将各段落用空格连接并去除首尾空格
        return ' '.join(formatted_segments).strip()

    # 修改格式化函数以考虑数据宽度
    def format_hex(self, value):
        """格式化十六进制显示, 考虑数据宽度"""
        # 处理有符号值
        if self.is_signed and value < 0:
            # 将负数转换为补码形式
            bit_count = self.get_bit_count()
            value_unsigned = (1 << bit_count) + value
        else:
            value_unsigned = value & ((1 << self.get_bit_count()) - 1)

        # 根据数据宽度确定十六进制位数
        if self.data_width == "BYTE":  # 8位
            hex_str = f"{value_unsigned:02X}"
        elif self.data_width == "WORD":  # 16位
            hex_str = f"{value_unsigned:04X}"
        elif self.data_width == "DWORD":  # 32位
            hex_str = f"{value_unsigned:08X}"
        else:  # QWORD 64位
            hex_str = f"{value_unsigned:016X}"

        return f"0x{hex_str}"

    def format_dec(self, value):
        """格式化十进制显示, 处理有符号值"""
        if self.is_signed:
            # 如果是有符号模式, 确保值在数据宽度有符号范围内
            bit_count = self.get_bit_count()
            max_val = (1 << (bit_count - 1)) - 1
            min_val = -(1 << (bit_count - 1))
            if value > max_val:
                value = value - (1 << bit_count)
            elif value < min_val:
                value = value + (1 << bit_count)
        return str(value)

    def format_bin(self, value):
        """格式化二进制显示, 考虑数据宽度"""
        # 处理有符号值
        if self.is_signed and value < 0:
            # 将负数转换为补码形式
            bit_count = self.get_bit_count()
            value_unsigned = (1 << bit_count) + value
        else:
            value_unsigned = value & ((1 << self.get_bit_count()) - 1)

        # 根据数据宽度确定二进制位数
        if self.data_width == "BYTE":  # 8位
            bin_str = f"{value_unsigned:08b}"
        elif self.data_width == "WORD":  # 16位
            bin_str = f"{value_unsigned:016b}"
        elif self.data_width == "DWORD":  # 32位
            bin_str = f"{value_unsigned:032b}"
        else:  # QWORD 64位
            bin_str = f"{value_unsigned:064b}"

        # formatted_bin = ' '.join([bin_str[i:i+4] for i in range(0, len(bin_str), 4)])
        formatted_bin = self.str_Alignment_for_len(bin_str, 4)

        return formatted_bin

    def format_oct(self, value):
        """格式化八进制显示, 处理有符号值"""
        # 处理有符号值
        if self.is_signed and value < 0:
            # 将负数转换为补码形式
            value_64 = (1 << 64) + value
        else:
            value_64 = value & 0xFFFFFFFFFFFFFFFF

        # 转换为八进制字符串, 去掉前缀
        oct_str = oct(value_64)[2:]

        # 根据数据宽度确定八进制位数
        if self.data_width == "BYTE":  # 8位
            oct_str = oct_str.zfill(3)  # 8位最大八进制是377
        elif self.data_width == "WORD":  # 16位
            oct_str = oct_str.zfill(6)  # 16位最大八进制是177777
        elif self.data_width == "DWORD":  # 32位
            oct_str = oct_str.zfill(11)  # 32位最大八进制是37777777777
        else:  # QWORD 64位
            oct_str = oct_str.zfill(22)  # 64位最大八进制是1777777777777777777777

        # 每3位添加一个空格（八进制的标准分组方式）
        # formatted_oct = ' '.join([oct_str[i:i+3] for i in range(0, len(oct_str), 3)])
        formatted_oct = self.str_Alignment_for_len(oct_str, 3)
        return formatted_oct

    def perform_initial_conversion(self):
        """执行初始数字转换"""
        try:
            if self.conversion_type == "HEX":
                # HEX 转其他进制
                hex_text = self.selected_text.replace("0x", "")
                hex_text = "".join(hex_text.split())
                if not hex_text:  # 添加空值检查
                    self.error_label.setText("错误: 请输入有效的十六进制数字")
                    return

                value = int(hex_text, 16)

                # 检查是否超出数据宽度范围
                max_value = (1 << self.get_bit_count()) - 1
                if value > max_value:
                    self.error_label.setText(f"警告: 初始值超出{self.data_width}范围")
                    value = value & max_value

            else:  # DEC 转换
                # DEC 转其他进制
                if not self.selected_text:  # 添加空值检查
                    self.error_label.setText("错误: 请输入有效的十进制数字")
                    return

                value = int("".join(self.selected_text.split()))

                # 检查是否超出数据宽度范围
                max_value, min_value = self.get_value_range()
                if value > max_value or value < min_value:
                    self.error_label.setText(f"警告: 初始值超出{self.data_width}范围")
                    # 截断值
                    if self.is_signed:
                        if value > max_value:
                            value = max_value
                        elif value < min_value:
                            value = min_value
                    else:
                        value = value & ((1 << self.get_bit_count()) - 1)

            self.hex_edit.setText(self.format_hex(value))
            self.dec_edit.setText(self.format_dec(value))
            self.bin_edit.setText(self.format_bin(value))
            self.oct_edit.setText(self.format_oct(value))

            # 更新位键盘
            self.set_bit_keyboard_value(value)

            # 更新位键盘状态（禁用高位）
            self.update_bit_keyboard_state()

            # 如果之前有警告, 保持警告显示, 否则清空
            if not self.error_label.text().startswith("警告"):
                self.error_label.setText("")

        except ValueError as e:
            self.error_label.setText(f"错误: 无法解析 '{self.selected_text}' 为{self.conversion_type}数字")
        except Exception as e:
            self.error_label.setText(f"错误: {str(e)}")
            # 添加详细错误信息
            import traceback
            print(f"进制转换错误: {traceback.format_exc()}")

    def on_hex_changed(self, text:str):
        """十六进制输入改变"""
        if self.updating:
            return

        try:
            # 去除可能的0x前缀和空格
            hex_text = "".join(text.split())
            hex_text = hex_text.replace("0x", "")
            if not hex_text:
                return

            value = int(hex_text, 16)

            # 检查是否超出数据宽度范围
            max_value = (1 << self.get_bit_count()) - 1
            if value > max_value:
                self.error_label.setText(f"警告: 十六进制值超出{self.data_width}范围")
                value = value & max_value
                # 重新设置截断后的值
                self.updating = True
                self.hex_edit.setText(self.format_hex(value))
                self.updating = False
            else:
                self.error_label.setText("")

            self.update_other_fields("HEX", value)

        except ValueError:
            self.error_label.setText(f"错误: 无效的十六进制数字 '{text}'")
        except Exception as e:
            self.error_label.setText(f"错误: {str(e)}")

    def on_dec_changed(self, text:str):
        """十进制输入改变"""
        if self.updating:
            return

        try:
            if not text:
                return

            dec_text = "".join(text.split())
            value = int(dec_text)

            # 检查是否超出数据宽度范围
            max_value, min_value = self.get_value_range()
            if value > max_value or value < min_value:
                self.error_label.setText(f"警告: 十进制值超出{self.data_width}范围")
                # 截断值
                if self.is_signed:
                    bit_count = self.get_bit_count()
                    if value > max_value:
                        value = max_value
                    elif value < min_value:
                        value = min_value
                else:
                    value = value & ((1 << self.get_bit_count()) - 1)
                # 重新设置截断后的值
                self.updating = True
                self.dec_edit.setText(self.format_dec(value))
                self.updating = False
            else:
                self.error_label.setText("")

            self.update_other_fields("DEC", value)

        except ValueError:
            self.error_label.setText(f"错误: 无效的十进制数字 '{text}'")
        except Exception as e:
            self.error_label.setText(f"错误: {str(e)}")

    def on_bin_changed(self, text:str):
        """二进制输入改变"""
        if self.updating:
            return

        try:
            if not text:
                return

            # 去除空格后转换为整数
            bin_text = "".join(text.split())
            value = int(bin_text, 2)

            # 检查是否超出数据宽度范围
            max_value = (1 << self.get_bit_count()) - 1
            if value > max_value:
                self.error_label.setText(f"警告: 二进制值超出{self.data_width}范围")
                value = value & max_value
                # 重新设置截断后的值
                self.updating = True
                self.bin_edit.setText(self.format_bin(value))
                self.updating = False
            else:
                self.error_label.setText("")

            self.update_other_fields("BIN", value)

        except ValueError:
            self.error_label.setText(f"错误: 无效的二进制数字 '{text}'")
        except Exception as e:
            self.error_label.setText(f"错误: {str(e)}")

    def on_oct_changed(self, text:str):
        """八进制输入改变"""
        if self.updating:
            return

        try:
            if not text:
                return
            oct_text = "".join(text.split())
            value = int(oct_text, 8)

            # 检查是否超出数据宽度范围
            max_value = (1 << self.get_bit_count()) - 1
            if value > max_value:
                self.error_label.setText(f"警告: 八进制值超出{self.data_width}范围")
                value = value & max_value
                # 重新设置截断后的值
                self.updating = True
                self.oct_edit.setText(self.format_oct(value))
                self.updating = False
            else:
                self.error_label.setText("")

            self.update_other_fields("OCT", value)

        except ValueError:
            self.error_label.setText(f"错误: 无效的八进制数字 '{text}'")
        except Exception as e:
            self.error_label.setText(f"错误: {str(e)}")

    def update_other_fields(self, source, value):
        """更新其他进制字段"""
        self.updating = True

        try:
            # 处理有符号显示
            display_value = value
            if self.is_signed and value > (1 << 63) - 1:
                # 如果值超过有符号正数范围, 转换为负数
                display_value = value - (1 << 64)

            if source != "HEX":
                self.hex_edit.setText(self.format_hex(display_value))

            if source != "DEC":
                self.dec_edit.setText(self.format_dec(display_value))

            if source != "BIN":
                self.bin_edit.setText(self.format_bin(display_value))

            if source != "OCT":
                self.oct_edit.setText(self.format_oct(display_value))

            # 更新位键盘 - 使用原始值
            self.set_bit_keyboard_value(value)

            self.error_label.setText("")

        except Exception as e:
            self.error_label.setText(f"更新错误: {str(e)}")
        finally:
            self.updating = False

    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "复制成功", f"已复制到剪贴板: {text}")
        except Exception as e:
            QMessageBox.critical(self, "复制失败", f"复制时发生错误: {str(e)}")

if __name__ == '__main__':
    import argparse

    # --- 参数解析 ---
    # 创建一个 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="一个独立的数字进制转换工具。")

    # 添加命令行参数
    # 第一个参数: selected_text, 是可选的位置参数
    parser.add_argument('selected_text', type=str, nargs='?', default="0x0",
                        help="要转换的初始数字文本 (例如, '123' 或 '0x7B')。")

    # 第二个参数: conversion_type, 也是可选的位置参数
    parser.add_argument('conversion_type', type=str, nargs='?', default="HEX",
                        help="初始转换类型 ('HEX' 或 'DEC')。")

    # 解析命令行传入的参数
    args = parser.parse_args()

    # --- 启动应用 ---
    # 使对话框可以独立运行
    app = QApplication(sys.argv)

    # 使用从命令行解析的参数创建对话框实例
    dialog = NumberConversionDialog(selected_text=args.selected_text, conversion_type=args.conversion_type)
    dialog.show()

    sys.exit(app.exec_())
