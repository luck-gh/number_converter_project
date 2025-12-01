from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class ExpandingTextEdit(QTextEdit):
    """一个可以根据内容自动扩展高度的文本编辑框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QTextEdit.NoWrap)  # 初始不换行
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭垂直滚动条
        self.textChanged.connect(self._on_text_changed)
        self._update_height()

    def _on_text_changed(self):
        """文本改变时触发, 检查是否需要换行"""
        text = self.toPlainText()
        font_metrics = self.fontMetrics()
        text_width = font_metrics.width(text)

        # 减去一个小的边距以获得更准确的宽度
        widget_width = self.width() - 10

        # 如果文本宽度大于控件宽度, 则启用自动换行
        if text_width > widget_width:
            if self.lineWrapMode() == QTextEdit.NoWrap:
                self.setLineWrapMode(QTextEdit.WidgetWidth)
                self._update_height()
        # 如果文本宽度小于控件宽度, 则恢复不换行
        else:
            if self.lineWrapMode() == QTextEdit.WidgetWidth:
                self.setLineWrapMode(QTextEdit.NoWrap)
                self._update_height()

    def _update_height(self):
        """根据内容更新控件的高度"""
        # 计算文档所需的总高度
        doc_height = self.document().size().height()
        # 获取单行文本的高度
        single_line_height = self.fontMetrics().height()

        # 添加边距
        margins = self.contentsMargins()
        new_height = doc_height + margins.top() + margins.bottom()

        # 确保最小高度至少为一行
        min_height = single_line_height + margins.top() + margins.bottom() + 5

        if new_height < min_height:
            new_height = min_height

        # 设置一个合理的最大高度（例如, 4行的高度）
        max_height = (single_line_height * 4) + margins.top() + margins.bottom() + 5
        if new_height > max_height:
            new_height = max_height

        # 仅在高度有显著变化时才设置, 以防止无限循环
        if abs(self.height() - int(new_height)) > 2:
            self.setFixedHeight(int(new_height))

    def resizeEvent(self, event):
        """当控件大小调整时, 重新检查换行设置"""
        super().resizeEvent(event)
        self._on_text_changed()

    # --- 提供与 QLineEdit 兼容的方法, 方便替换 ---
    def setText(self, text):
        """设置文本, 兼容 QLineEdit 的方法"""
        self.setPlainText(text)

    def text(self):
        """获取文本, 兼容 QLineEdit 的方法"""
        return self.toPlainText()
