from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import  Qt, QDir
import os


class Ui_Table_view(QtWidgets.QDialog):

    def __init__(self, df=None):
        super().__init__()
        self.df = df.copy() # prevent the original df from being modified
        self.df.reset_index(inplace=True) 
        self.current_page = 0  #set the current page number to 0
        self.rows_per_page = 100  # set the number of rows per page to 100
        self.setupUi(self)
        self.desk_path = os.path.join(QDir.homePath(), 'Desktop')

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
        start_row = self.current_page * self.rows_per_page
        end_row = start_row + self.rows_per_page
        subset_df = df.iloc[start_row:end_row]

        # 使用subset_df来填充table_widget
        table_widget.setRowCount(subset_df.shape[0])
        table_widget.setColumnCount(subset_df.shape[1])
        table_widget.setHorizontalHeaderLabels(subset_df.columns)

        for i in range(subset_df.shape[0]):
            for j in range(subset_df.shape[1]):
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(subset_df.iat[i, j])))

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Table View"))
        self.pushButton_export.setText(_translate("Dialog", "Export Table"))


    def export_tsv(self):
        try:
            export_path, filetype = QFileDialog.getSaveFileName(self, 'Export Table', self.desk_path, 
                                                                'Text Files (*.tsv);;CSV Files (*.csv)')
            if export_path == '':
                return
            if filetype == 'Text Files (*.tsv)':
                self.df.to_csv(export_path, sep='\t', index=False)
            elif filetype == 'CSV Files (*.csv)':
                self.df.to_csv(export_path, sep=',', index=False)
            else:
                QMessageBox.critical(self, 'Error', 'Filetype not supported.')
                return

            QMessageBox.information(self, 'Information', 'Export successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

