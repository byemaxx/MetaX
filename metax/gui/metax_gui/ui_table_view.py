from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import  Qt, QDir
from PyQt5.QtGui import QIcon
import pandas as pd

import os
import io
import csv
import sys
import subprocess


def _safe_table_filename(title):
    return str(title).translate(str.maketrans({char: '_' for char in '/\\:*?"<>|'}))


def table_widget_to_dataframe(table_widget, selected_only=False):
    if selected_only:
        indexes = table_widget.selectedIndexes()
        if not indexes:
            return None
        rows = sorted({index.row() for index in indexes})
        columns = sorted({index.column() for index in indexes})
        selected_positions = {(index.row(), index.column()) for index in indexes}
    else:
        rows = list(range(table_widget.rowCount()))
        columns = list(range(table_widget.columnCount()))
        selected_positions = {(row, column) for row in rows for column in columns}

    headers = []
    for column in columns:
        header_item = table_widget.horizontalHeaderItem(column)
        headers.append(header_item.text() if header_item is not None else str(column + 1))

    data = []
    for row in rows:
        values = []
        for column in columns:
            if (row, column) not in selected_positions:
                values.append('')
                continue
            item = table_widget.item(row, column)
            values.append(item.text() if item is not None else '')
        data.append(values)

    return pd.DataFrame(data, columns=headers)


def copy_table_widget_selection_to_clipboard(table_widget):
    df = table_widget_to_dataframe(table_widget, selected_only=True)
    if df is None:
        return False
    stream = io.StringIO()
    csv.writer(stream).writerows(df.values.tolist())
    QtWidgets.QApplication.clipboard().setText(stream.getvalue())
    return True


def export_dataframe_with_dialog(parent, df, title, last_path, save_index=False):
    filename = _safe_table_filename(title)
    default_filename = os.path.join(last_path, filename + '.tsv')
    export_path, filetype = QFileDialog.getSaveFileName(
        parent,
        'Export Table',
        default_filename,
        'Text Files (*.tsv);;CSV Files (*.csv);;Excel Files (*.xlsx)',
    )

    if export_path == '':
        return last_path, False

    if not export_dataframe_to_path(df, export_path, filetype, save_index=save_index):
        QMessageBox.critical(parent, 'Error', 'Filetype not supported.')
        return last_path, False

    new_last_path = os.path.dirname(export_path)
    reply = QMessageBox.question(
        parent,
        'Information',
        'Export successfully!\n\nDo you want to open the exported file?',
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    if reply == QMessageBox.Yes:
        if sys.platform == "win32":
            os.startfile(export_path, 'open')
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, export_path])

    return new_last_path, True


def export_dataframe_to_path(df, export_path, filetype, save_index=False):
    if filetype == 'Text Files (*.tsv)':
        df.to_csv(export_path, sep='\t', index=save_index)
    elif filetype == 'CSV Files (*.csv)':
        df.to_csv(export_path, sep=',', index=save_index)
    elif filetype == 'Excel Files (*.xlsx)':
        df.to_excel(export_path, index=save_index)
    else:
        return False
    return True


class Ui_Table_view(QtWidgets.QDialog):
    last_path_updated = QtCore.pyqtSignal(str) # signal to update last_path in main window

    def __init__(self, df=None, parent=None, title='Table View', last_path=None):
        super().__init__(parent)  
        self.df = df.copy() # prevent the original df from being modified
        self.df.reset_index(inplace=True)
        self.title = title
        self.save_index = False
        self.current_page = 0  #set the current page number to 0
        self.rows_per_page = 100  # set the number of rows per page to 100
        self.setupUi(self)
        icon_path = os.path.join(os.path.dirname(__file__), "./resources/logo.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(title)
        
        self.last_path = os.path.join(QDir.homePath(), 'Desktop') if last_path is None else last_path
        


    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1200, 600)
        Dialog.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.page_buttons_layout = QtWidgets.QHBoxLayout() 
        self.previous_page_button = QtWidgets.QPushButton("Previous Page")  
        self.next_page_button = QtWidgets.QPushButton("Next Page")  
        self.page_buttons_layout.addWidget(self.previous_page_button)
        self.page_buttons_layout.addWidget(self.next_page_button)
        self.verticalLayout_2.addLayout(self.page_buttons_layout)  

        self.pushButton_export = QtWidgets.QPushButton(Dialog)
        self.pushButton_export.setObjectName("pushButton_export")
        self.verticalLayout_2.addWidget(self.pushButton_export)

        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # set right-click menu policy
        self.tableWidget.customContextMenuRequested.connect(self.openMenu)  # set right-click menu
        self.verticalLayout_2.addWidget(self.tableWidget)
        header = self.tableWidget.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.headerMenu)

        self.previous_page_button.clicked.connect(self.previous_page)  
        self.next_page_button.clicked.connect(self.next_page)  
        self.pushButton_export.clicked.connect(self.export_tsv)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        if self.df is not None:
            self.set_pd_to_QTableWidget(self.df, self.tableWidget)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.set_pd_to_QTableWidget(self.df, self.tableWidget)

    def next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.df):
            self.current_page += 1
            self.set_pd_to_QTableWidget(self.df, self.tableWidget)

    def set_pd_to_QTableWidget(self, df, table_widget):
        # 处理多重列索引
        if isinstance(df.columns, pd.MultiIndex):
            self.save_index = True
            column_labels = [' '.join(col).strip() for col in df.columns.values]
        else:
            column_labels = df.columns

        # 处理多重行索引
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
        else:
            df = df.reset_index(drop=True)

        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, len(df))
        subset_df = df.iloc[start_row:end_row]

        # 使用subset_df来填充table_widget
        table_widget.setRowCount(subset_df.shape[0])
        table_widget.setColumnCount(subset_df.shape[1])
        table_widget.setHorizontalHeaderLabels(column_labels)

        for i in range(subset_df.shape[0]):
            for j in range(subset_df.shape[1]):
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(subset_df.iat[i, j])))

    def headerMenu(self, position):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy Column Name")
        sort_ascending_action = menu.addAction("Sort Ascending")
        sort_descending_action = menu.addAction("Sort Descending")
        copy_all_action = menu.addAction("Copy Column Data")

        action = menu.exec_(self.tableWidget.horizontalHeader().mapToGlobal(position))

        if action == copy_action:
            self.copy_column_name(position)
        elif action == sort_ascending_action:
            self.sort_by_column(self.tableWidget.horizontalHeader().logicalIndexAt(position), ascending=True)
        elif action == sort_descending_action:
            self.sort_by_column(self.tableWidget.horizontalHeader().logicalIndexAt(position), ascending=False)
        elif action == copy_all_action:
            self.copy_selection_column_to_clipboard(position)
    
    def copy_selection_column_to_clipboard(self, position):
        column = self.tableWidget.horizontalHeader().logicalIndexAt(position)
        column_name = self.tableWidget.horizontalHeader().model().headerData(column, Qt.Horizontal)
        column_data = self.df[column_name]
        column_data.to_clipboard(index=False, header=False)

    def sort_by_column(self, column, ascending=True):
        """
        Sort the table by the column.
        """
        self.df.sort_values(by=self.df.columns[column], ascending=ascending, inplace=True)
        self.current_page = 0
        self.set_pd_to_QTableWidget(self.df, self.tableWidget)

        

    def copy_column_name(self, position):
        column = self.tableWidget.horizontalHeader().logicalIndexAt(position)
        column_name = self.tableWidget.horizontalHeader().model().headerData(column, Qt.Horizontal)
        QtWidgets.QApplication.clipboard().setText(column_name)
        
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Table View"))
        self.pushButton_export.setText(_translate("Dialog", "Export Table"))


    def export_tsv(self):
        try:
            self.last_path, exported = export_dataframe_with_dialog(
                self,
                self.df,
                self.title,
                self.last_path,
                save_index=self.save_index,
            )
            if exported:
                self.last_path_updated.emit(self.last_path)  # 发射信号

        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    
    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        has_selection = bool(self.tableWidget.selectedIndexes())
        copy_action = menu.addAction("Copy Selection")
        export_selection_action = menu.addAction("Export Selected Cells")
        export_selection_action.setEnabled(has_selection)
        menu.addSeparator()
        export_page_action = menu.addAction("Export Current Page")
        export_table_action = menu.addAction("Export Full Table")
        action = menu.exec_(self.tableWidget.mapToGlobal(position))

        if action == copy_action:
            self.copy_selection_to_clipboard()
        elif action == export_selection_action:
            self.export_selection()
        elif action == export_page_action:
            self.export_current_page()
        elif action == export_table_action:
            self.export_tsv()

    def export_selection(self):
        try:
            df = table_widget_to_dataframe(self.tableWidget, selected_only=True)
            if df is None:
                QMessageBox.warning(self, 'Warning', 'No cells selected!')
                return
            self.last_path, exported = export_dataframe_with_dialog(
                self,
                df,
                f'{self.title}_selected_cells',
                self.last_path,
            )
            if exported:
                self.last_path_updated.emit(self.last_path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def export_current_page(self):
        try:
            df = table_widget_to_dataframe(self.tableWidget, selected_only=False)
            self.last_path, exported = export_dataframe_with_dialog(
                self,
                df,
                f'{self.title}_current_page',
                self.last_path,
            )
            if exported:
                self.last_path_updated.emit(self.last_path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def copy_selection_to_clipboard(self):
        if not copy_table_widget_selection_to_clipboard(self.tableWidget):
            QMessageBox.warning(self, 'Warning', 'No cells selected!')
