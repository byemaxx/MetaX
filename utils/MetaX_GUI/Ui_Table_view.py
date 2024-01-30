from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import  Qt, QDir
from PyQt5.QtGui import QIcon
import pandas as pd

import os
import io
import csv
import sys

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
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # set right-click menu policy
        self.tableWidget.customContextMenuRequested.connect(self.openMenu)  # set right-click menu
        self.verticalLayout_2.addWidget(self.tableWidget)

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


        header = table_widget.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.headerMenu)
        
        

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
            # make sure the file name is valid
            filename = self.title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            default_filename = os.path.join(self.last_path, filename + '.tsv')
            export_path, filetype = QFileDialog.getSaveFileName(self, 'Export Table', default_filename, 
                                                            'Text Files (*.tsv);;CSV Files (*.csv);;Excel Files (*.xlsx)')

            if export_path == '':
                return
            if filetype == 'Text Files (*.tsv)':
                self.df.to_csv(export_path, sep='\t', index=self.save_index)
            elif filetype == 'CSV Files (*.csv)':
                self.df.to_csv(export_path, sep=',', index=self.save_index)
            elif filetype == 'Excel Files (*.xlsx)':
                self.df.to_excel(export_path, index=self.save_index)
            else:
                QMessageBox.critical(self, 'Error', 'Filetype not supported.')
                return

            # update last_path
            self.last_path = os.path.dirname(export_path)
            self.last_path_updated.emit(self.last_path)  # 发射信号

            reply = QMessageBox.question(self, 'Information', 'Export successfully!\n\nDo you want to open the exported file?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if sys.platform == "win32":
                    os.startfile(export_path, 'open') # open the file with default application
                else:
                    # use default application to open the file
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, export_path])
                    

        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    
    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        copy_action = menu.addAction("Copy")
        action = menu.exec_(self.tableWidget.mapToGlobal(position))

        if action == copy_action:
            self.copy_selection_to_clipboard()

    def copy_selection_to_clipboard(self):
        selection = self.tableWidget.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            QtWidgets.QApplication.clipboard().setText(stream.getvalue())

