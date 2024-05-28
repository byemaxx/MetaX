from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from .Ui_Setting import Ui_Settings

class SettingsWidget(QWidget):
    update_mode_changed = pyqtSignal(str)
    auto_check_update_changed = pyqtSignal(bool)

    def __init__(self, parent=None, update_branch="main", auto_check_update=True):
        super().__init__(parent)
        self.update_mode = update_branch
        self.auto_check_update = auto_check_update

        if parent:
            self.setWindowIcon(parent.windowIcon())

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        
        self.init_ui(self.update_mode, self.auto_check_update)
        # resize the window, 600x400 as default
        self.resize(600, 400)
        
        self.ui.checkBox_auto_check_update.stateChanged.connect(self.handle_checkbox_state_changed)
        self.ui.radioButton_update_stable.toggled.connect(self.handle_radio_button_toggled)
        self.ui.radioButton_update_beta.toggled.connect(self.handle_radio_button_toggled)

    def init_ui(self, update_mode, auto_check_update):
        if update_mode == "main":
            self.ui.radioButton_update_stable.setChecked(True)
        elif update_mode == "dev":
            self.ui.radioButton_update_beta.setChecked(True)
        self.ui.checkBox_auto_check_update.setChecked(auto_check_update)

    def handle_checkbox_state_changed(self):
        self.auto_check_update = self.ui.checkBox_auto_check_update.isChecked()
        self.auto_check_update_changed.emit(self.auto_check_update)

    # def handle_radio_button_toggled(self):
    #     if self.ui.radioButton_update_stable.isChecked():
    #         self.update_mode = "main"
    #     elif self.ui.radioButton_update_beta.isChecked():
    #         self.update_mode = "dev"
    #     self.update_mode_changed.emit(self.update_mode)
    
    
    def handle_radio_button_toggled(self, checked):
        sender = self.sender()
        # print(f"Toggled: {sender.objectName()}, Checked: {checked}")

        if sender == self.ui.radioButton_update_stable and checked:
            self.update_mode = "main"
            self.update_mode_changed.emit(self.update_mode)
        elif sender == self.ui.radioButton_update_beta and checked:
            self.update_mode = "dev"
            self.update_mode_changed.emit(self.update_mode)
            
            
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = SettingsWidget(parent=None, update_branch="dev", auto_check_update=False)
    widget.show()
    sys.exit(app.exec_())
