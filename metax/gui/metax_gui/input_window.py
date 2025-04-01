from PySide6.QtWidgets import (QSizePolicy, QGridLayout, QRadioButton, QButtonGroup, 
                               QTextEdit, QPushButton, QDialog)
from PySide6.QtGui import QGuiApplication
class InputWindow(QDialog):
    """
    A dialog window for inputting text.

    Args:
        `parent (QWidget)`: The parent widget of the dialog.
        `input_mode (bool)`: Flag indicating whether to show the match mode radio buttons.
        - `True`: Show the radio buttons for selecting the match mode.
        - `False`: Only show the text editor and the OK/Cancel buttons.

    Attributes:
        text_edit (QTextEdit): The text editor widget.
        exact_match_radio (QRadioButton): The radio button for exact match mode.
        search_match_radio (QRadioButton): The radio button for search match mode.
        match_mode_group (QButtonGroup): The button group for the match mode radio buttons.
        ok_button (QPushButton): The OK button.
        cancel_button (QPushButton): The Cancel button.
    """

    def __init__(self, parent=None, input_mode=False):
        super(InputWindow, self).__init__(parent)
        self.text_edit = QTextEdit(self)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.exact_match_radio = QRadioButton("Exact Match", self)
        self.search_match_radio = QRadioButton("Search Match", self)
        self.exact_match_radio.setChecked(True) 

        # 使用QButtonGroup来确保互斥
        self.match_mode_group = QButtonGroup(self)
        self.match_mode_group.addButton(self.exact_match_radio)
        self.match_mode_group.addButton(self.search_match_radio)

        self.ok_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(self.text_edit, 0, 0, 1, 2)  # 文本编辑器占据第0行，跨越0和1列
        if input_mode:  # 当input_mode为True时，添加单选按钮
            layout.addWidget(self.exact_match_radio, 1, 0)  # "精准匹配"单选按钮
            layout.addWidget(self.search_match_radio, 1, 1)  # "搜索匹配"单选按钮
            button_row = 2  # 按钮行下移
        else:
            button_row = 1
            # hide the radio buttons
            self.exact_match_radio.hide()
            self.search_match_radio.hide()
        layout.addWidget(self.ok_button, button_row, 0)  # 'OK'按钮
        layout.addWidget(self.cancel_button, button_row, 1)  # 'Cancel'按钮

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setWindowTitle('Input List')
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.resize(int(screen_geometry.width() / 1.8), int(screen_geometry.height() / 1.8))
        
        
    def get_selected_mode(self):
        """
        Get the selected match mode.

        Returns:
            str: The selected match mode. Possible values are "exact", "search", or None.
        """
        if self.exact_match_radio.isChecked():
            return "exact"
        elif self.search_match_radio.isChecked():
            return "search"
        else:
            return None

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    input_window = InputWindow(input_mode=True)  # 设置input_mode=True以显示单选按钮
    input_window.show()
    sys.exit(app.exec_())
