from PyQt5.QtWidgets import QWidget, QToolBox, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
import os

try:
    from .ui_setting_window import Ui_Settings
except ImportError:
    from ui_setting_window import Ui_Settings

class SettingsWidget(QWidget):
    update_mode_changed = pyqtSignal(str)
    auto_check_update_changed = pyqtSignal(bool)
    heatmap_params_dict_changed = pyqtSignal(dict)
    tf_link_net_params_dict_changed = pyqtSignal(dict)
    html_theme_changed = pyqtSignal(str)
    protein_infer_method_changed = pyqtSignal(str)
    stat_mean_by_zero_dominant_changed = pyqtSignal(bool)
    metatree_dir_changed = pyqtSignal(str)

    def __init__(self, parent=None, update_branch="main", auto_check_update=True, stat_mean_by_zero_dominant=False, settings=None):
        super().__init__(parent)
        self.update_mode = update_branch
        self.auto_check_update = auto_check_update
        # store QSettings object (may be None)
        self.settings = settings
        if parent:
            self.setWindowIcon(parent.windowIcon())

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        
        self.init_ui(self.update_mode, self.auto_check_update, stat_mean_by_zero_dominant, settings)
        # resize the window, 800 as default
        self.resize(800, 400)
        
        # move to the first tab in QToolBox
        toolbox = self.findChildren(QToolBox)
        for widget in toolbox:
            widget.setCurrentIndex(0)
                    
        # signal-slot connections
        self.ui.checkBox_auto_check_update.stateChanged.connect(self.handle_checkbox_state_changed)
        self.ui.radioButton_update_stable.toggled.connect(self.handle_radio_button_toggled)
        self.ui.radioButton_update_beta.toggled.connect(self.handle_radio_button_toggled)
        
        self.ui.comboBox_heatmap_linkage_method.currentTextChanged.connect(self.handle_heatmap_params_changed)
        self.ui.comboBox_heatmap_linkage_metric.currentTextChanged.connect(self.handle_heatmap_params_changed)
        self.ui.spinBox_heatmap_x_labels_rotation.valueChanged.connect(self.handle_heatmap_params_changed)
        self.ui.spinBox_heatmap_y_labels_rotation.valueChanged.connect(self.handle_heatmap_params_changed)
        
        
        # link all signal-slot connections for TF-link network
        self.ui.comboBox_tf_link_net_taxa_sahpe.currentTextChanged.connect(self.handle_tf_link_network_changed)
        self.ui.comboBox_tf_link_net_func_shape.currentTextChanged.connect(self.handle_tf_link_network_changed)
        self.ui.lineEdit_tf_link_net_taxa_color.textChanged.connect(self.handle_tf_link_network_changed)
        self.ui.lineEdit_tf_link_net_taxa_focus_color.textChanged.connect(self.handle_tf_link_network_changed)
        self.ui.lineEdit_tf_link_net_func_color.textChanged.connect(self.handle_tf_link_network_changed)
        self.ui.lineEdit_tf_link_net_func_focus_color.textChanged.connect(self.handle_tf_link_network_changed)
        
        self.ui.doubleSpinBox_tf_link_net_line_opacity.valueChanged.connect(self.handle_tf_link_network_changed)
        self.ui.doubleSpinBox_tf_link_net_line_width.valueChanged.connect(self.handle_tf_link_network_changed)
        self.ui.doubleSpinBox_tf_link_net_line_curve.valueChanged.connect(self.handle_tf_link_network_changed)
        self.ui.lineEdit_tf_link_net_line_color.textChanged.connect(self.handle_tf_link_network_changed)
        self.ui.spinBox_tf_link_net_repulsion.valueChanged.connect(self.handle_tf_link_network_changed)
        self.ui.comboBox_tf_link_net_font_weight.currentTextChanged.connect(self.handle_tf_link_network_changed)
        self.ui.comboBox_tf_link_net_label_position.currentTextChanged.connect(self.handle_tf_link_network_changed)
        self.ui.spinBox_tf_link_net_text_width.valueChanged.connect(self.handle_tf_link_network_changed)
        self.ui.doubleSpinBox_tf_link_net_gravity.valueChanged.connect(self.handle_tf_link_network_changed)
        
        # HTML theme
        self.ui.comboBox_html_theme.currentTextChanged.connect(self.handle_html_theme_changed)
        
        # Protein inference method
        self.ui.comboBox_protein_infer_greedy_mode.currentTextChanged.connect(self.handle_protein_infer_method_changed)
        
        # stat_mean_by_zero_dominant
        self.ui.checkBox_stat_mean_by_zero_dominant.stateChanged.connect(self.handle_stat_mean_by_zero_dominant_changed)
        
        # open metatree directory path
        self.ui.pushButton_open_metatree_dir_path.clicked.connect(self.set_meta_tree_directory)
        # handle manual edits to the metatree path line edit
        try:
            self.ui.lineEdit_metatree_dir_path.textChanged.connect(self._handle_metatree_lineedit_changed)
        except Exception:
            pass
        
        
    def init_ui(self, update_mode, auto_check_update, stat_mean_by_zero_dominant, settings=None,):
        if update_mode == "main":
            self.ui.radioButton_update_stable.setChecked(True)
        elif update_mode == "dev":
            self.ui.radioButton_update_beta.setChecked(True)
        self.ui.checkBox_auto_check_update.setChecked(auto_check_update)
        
        # set the default values for stat_mean_by_zero_dominant
        self.ui.checkBox_stat_mean_by_zero_dominant.setChecked(stat_mean_by_zero_dominant)
        
        if settings:
            method = settings.value('protein_infer_greedy_mode', 'fast')
            selected_method = 'normal' if method == 'greedy' else 'fast'
            print(f"Protein inference method: {method}")
            self.ui.comboBox_protein_infer_greedy_mode.setCurrentText(selected_method)
        # set MetaTree path line edit from settings if available
        if settings and settings.contains('metatree_dir'):
            try:
                mt_path = settings.value('metatree_dir')
                if mt_path:
                    self.ui.lineEdit_metatree_dir_path.setText(mt_path)
            except Exception:
                pass
            

    def handle_checkbox_state_changed(self):
        self.auto_check_update = self.ui.checkBox_auto_check_update.isChecked()
        self.auto_check_update_changed.emit(self.auto_check_update)

    def handle_heatmap_params_changed(self):
        method = self.ui.comboBox_heatmap_linkage_method.currentText()
        metric = self.ui.comboBox_heatmap_linkage_metric.currentText()
        x_labels_rotation = self.ui.spinBox_heatmap_x_labels_rotation.value()
        y_labels_rotation = self.ui.spinBox_heatmap_y_labels_rotation.value()
        
        heatmap_params_dict = {
            "linkage_method": method,
            "distance_metric": metric,
            "x_labels_rotation": x_labels_rotation,
            "y_labels_rotation": y_labels_rotation,
        }
        
        self.heatmap_params_dict_changed.emit(heatmap_params_dict)
        
    def handle_tf_link_network_changed(self):
        network_params_dict = {
            "taxa_shape": self.ui.comboBox_tf_link_net_taxa_sahpe.currentText(),
            "func_shape": self.ui.comboBox_tf_link_net_func_shape.currentText(),
            "taxa_color": self.ui.lineEdit_tf_link_net_taxa_color.text(),
            "taxa_focus_color": self.ui.lineEdit_tf_link_net_taxa_focus_color.text(),
            "func_color": self.ui.lineEdit_tf_link_net_func_color.text(),
            "func_focus_color": self.ui.lineEdit_tf_link_net_func_focus_color.text(),
            "line_opacity": self.ui.doubleSpinBox_tf_link_net_line_opacity.value(),
            "line_width": self.ui.doubleSpinBox_tf_link_net_line_width.value(),
            "line_curve": self.ui.doubleSpinBox_tf_link_net_line_curve.value(),
            "line_color": self.ui.lineEdit_tf_link_net_line_color.text(),
            'repulsion': self.ui.spinBox_tf_link_net_repulsion.value(),
            'font_weight': self.ui.comboBox_tf_link_net_font_weight.currentText(),
            'label_position': self.ui.comboBox_tf_link_net_label_position.currentText(),
            'text_width': self.ui.spinBox_tf_link_net_text_width.value(),
            'gravity': self.ui.doubleSpinBox_tf_link_net_gravity.value(),
            
        }
        self.tf_link_net_params_dict_changed.emit(network_params_dict)
    
    def handle_radio_button_toggled(self, checked):
        sender = self.sender()
        # print(f"Toggled: {sender.objectName()}, Checked: {checked}")

        if sender == self.ui.radioButton_update_stable and checked:
            self.update_mode = "main"
            self.update_mode_changed.emit(self.update_mode)
        elif sender == self.ui.radioButton_update_beta and checked:
            self.update_mode = "dev"
            self.update_mode_changed.emit(self.update_mode)
            
    def handle_html_theme_changed(self):
        theme = self.ui.comboBox_html_theme.currentText()
        self.html_theme_changed.emit(theme)
        
    def handle_protein_infer_method_changed(self):
        protein_infer_greedy_mode = self.ui.comboBox_protein_infer_greedy_mode.currentText()
        method = {
            'normal': 'greedy',
            'fast': 'heap',
        }
        self.protein_infer_method_changed.emit(method[protein_infer_greedy_mode])
        
    def handle_stat_mean_by_zero_dominant_changed(self):
        checked = self.ui.checkBox_stat_mean_by_zero_dominant.isChecked()
        self.stat_mean_by_zero_dominant_changed.emit(checked)
    
    def set_meta_tree_directory(self):
        # open a file dialog to select a directory, check if index.html exists in the selected directory
        # shows on lineEdit_metatree_dir_path
        
        # start at current setting or user home
        start_dir = None
        if hasattr(self, 'settings') and self.settings:
            try:
                current = self.settings.value('metatree_dir')
                if current:
                    start_dir = current
            except Exception:
                start_dir = None

        if not start_dir:
            start_dir = os.path.expanduser('~')

        folder = QFileDialog.getExistingDirectory(self, 'Select MetaTree directory', start_dir)
        if not folder:
            return

        index_html = os.path.join(folder, 'index.html')
        if not os.path.exists(index_html):
            QMessageBox.warning(self, 'Warning', "Selected directory does not contain 'index.html'. Please select a valid MetaTree build directory.")
            # clear the line edit (do not show invalid folder) and remove stored setting, notify listeners
            try:
                self.ui.lineEdit_metatree_dir_path.setText('')
            except Exception:
                pass
            if hasattr(self, 'settings') and self.settings:
                try:
                    # remove the stored metatree_dir (or set to empty)
                    try:
                        self.settings.remove('metatree_dir')
                    except Exception:
                        self.settings.setValue('metatree_dir', '')
                    # notify listeners that metatree is unavailable
                    try:
                        self.metatree_dir_changed.emit('')
                    except Exception:
                        pass
                except Exception:
                    pass
            return

        # update UI
        try:
            self.ui.lineEdit_metatree_dir_path.setText(folder)
        except Exception:
            pass

        # save to QSettings if available
        if hasattr(self, 'settings') and self.settings:
            try:
                self.settings.setValue('metatree_dir', folder)
                # notify listeners that metatree_dir was changed
                try:
                    self.metatree_dir_changed.emit(folder)
                except Exception:
                    pass
            except Exception:
                pass

    def _handle_metatree_lineedit_changed(self, text: str):
        """Handle manual edits to the metatree path line edit.

        If the entered path points to a valid metatree (contains index.html) we save it;
        otherwise remove the setting and notify listeners to hide the button.
        """
        text = text.strip() if text is not None else ''
        if text == '':
            # empty path -> remove setting and notify
            if hasattr(self, 'settings') and self.settings:
                try:
                    try:
                        self.settings.remove('metatree_dir')
                    except Exception:
                        self.settings.setValue('metatree_dir', '')
                except Exception:
                    pass
            try:
                self.metatree_dir_changed.emit('')
            except Exception:
                pass
            return

        # check if index.html exists
        index_html = os.path.join(text, 'index.html')
        if os.path.exists(index_html):
            # save
            if hasattr(self, 'settings') and self.settings:
                try:
                    self.settings.setValue('metatree_dir', text)
                except Exception:
                    pass
            try:
                self.metatree_dir_changed.emit(text)
            except Exception:
                pass
        else:
            # invalid path -> remove stored setting and notify
            if hasattr(self, 'settings') and self.settings:
                try:
                    try:
                        self.settings.remove('metatree_dir')
                    except Exception:
                        self.settings.setValue('metatree_dir', '')
                except Exception:
                    pass
            try:
                self.metatree_dir_changed.emit('')
            except Exception:
                pass
         
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = SettingsWidget(parent=None, update_branch="dev", auto_check_update=False)
    widget.show()
    sys.exit(app.exec_())
