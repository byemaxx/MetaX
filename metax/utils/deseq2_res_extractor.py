import sys
import os
import pandas as pd
import re
# from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                               QHBoxLayout, QPushButton, QFileDialog, QTextEdit, 
#                               QLabel, QLineEdit, QMessageBox, QSplitter, 
#                               QTableView, QTabWidget, QDialog, QScrollArea, QHeaderView, 
#                               QProgressDialog, QCheckBox)
# from PySide6.QtCore import Qt, QAbstractTableModel
# from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTextEdit, 
                             QLabel, QLineEdit, QMessageBox, QSplitter, 
                             QTableView, QTabWidget, QDialog, QScrollArea, QHeaderView, 
                             QProgressDialog, QCheckBox)
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

import numpy as np
import openpyxl

class PandasModel(QAbstractTableModel):
    """A model class for displaying Pandas DataFrame in QTableView"""
    
    def __init__(self, data):
        super().__init__()
        # Reset index, keep original index as column
        if isinstance(data, pd.DataFrame):
            # If data has index, convert it to column
            if not data.index.empty and data.index.name != 'index':
                data = data.reset_index()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                # Handle different data types, especially NaN values
                if isinstance(value, (float, np.floating)):
                    if np.isnan(value):
                        return "NaN"
                    return f"{value:.6g}"  # Format number display
                return str(value)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None


class DragDropTextEdit(QTextEdit):
    """A text edit widget supporting drag-and-drop files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable drag and drop
        self.setAcceptDrops(True)
        # Save reference to main window
        self.main_window = parent
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Called when the user drags an item onto the widget"""
        mime_data = event.mimeData()
        # Check if there are URLs (files)
        if mime_data.hasUrls():
            for url in mime_data.urls():
                # Check if it is a local file
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    # Check file extension
                    if file_path.endswith(('.tsv', '.csv', '.xlsx', '.txt')):
                        event.acceptProposedAction()
                        return
        # If not accepted, ignore the event
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Called when the user drops an item onto the widget"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            # Handle all dropped files
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.endswith(('.tsv', '.csv', '.xlsx', '.txt')):
                        # Process file and update text box content
                        # Find main window instance
                        main_window = self.findMainWindow()
                        if main_window:
                            main_window.load_gene_list_from_file(file_path)
            event.acceptProposedAction()
    
    def findMainWindow(self):
        """Find the main window instance"""
        parent = self.parent()
        # Traverse up the parent widgets until the main window type is found
        while parent:
            if isinstance(parent, GeneExtractorApp):
                return parent
            parent = parent.parent()
        return None


class MissingGenesDialog(QDialog):
    """Dialog to display a list of missing entries"""
    
    def __init__(self, missing_genes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("List of Missing Entries")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Add label to display total count
        count_label = QLabel(f"The following {len(missing_genes)} entries were not found in the dataset:")
        layout.addWidget(count_label)
        
        # Create a scrollable text area to display the list of entries
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add a label for each missing entry
        for gene in missing_genes:
            gene_label = QLabel(f"• {gene}")
            gene_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            scroll_layout.addWidget(gene_label)
        
        # Add blank space
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Add OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)


class GeneExtractorApp(QMainWindow):
    def __init__(self, deseq2_df=None, deseq2_df_name=None):
        super().__init__()
        self.setWindowTitle("DESeq2 Results Extractor v0.3")
        self.resize(1000, 800)
        
        # Store data
        self.df_res = None
        self.df_ex = None
        self.df_log2FC = None
        self.df_padj = None
        self.df_long = None
        
        # Store external deseq2 dataframe and name
        self.external_deseq2_df = deseq2_df
        self.external_deseq2_df_name = deseq2_df_name
        
        # Set up UI
        self.setup_ui()
        
        # If dataframe is passed, validate and use it directly
        if self.external_deseq2_df is not None:
            if self._validate_deseq2_dataframe(self.external_deseq2_df):
                self.df_res = self.external_deseq2_df.copy()
                if self.external_deseq2_df_name:
                    self.file_path_edit.setPlaceholderText(f"Using external DESeq2 DataFrame: {self.external_deseq2_df_name}")
                else:
                    self.file_path_edit.setPlaceholderText("Using external DESeq2 DataFrame")
            else:
                # If validation fails, reset the external dataframe
                self.external_deseq2_df = None
                self.external_deseq2_df_name = None
    
    def _validate_deseq2_dataframe(self, df):
        """
        Validate if the passed DataFrame has the correct format for DESeq2 results.
        Expected format: 3-level column index from get_stats_deseq2_against_control_with_conditon
        """
        try:
            # Check if it's a DataFrame
            if not isinstance(df, pd.DataFrame):
                QMessageBox.critical(self, "DataFrame Format Error", 
                                   "The passed object is not a pandas DataFrame.")
                return False
            
            # Check if it has MultiIndex columns
            if not isinstance(df.columns, pd.MultiIndex):
                QMessageBox.critical(self, "DataFrame Format Error", 
                                   "The DataFrame must have MultiIndex columns.\n"
                                   "Expected format: 3-level columns from get_stats_deseq2_against_control_with_conditon function.")
                return False
            
            # Check if it has 3 levels in columns
            if df.columns.nlevels != 3:
                QMessageBox.critical(self, "DataFrame Format Error", 
                                   f"The DataFrame must have exactly 3 levels in column index, but got {df.columns.nlevels} levels.\n"
                                   "Expected format: 3-level columns from get_stats_deseq2_against_control_with_conditon function.")
                return False
            
            # Check if the third level contains expected DESeq2 result columns
            third_level_cols = df.columns.get_level_values(2).unique()
            expected_cols = {'log2FoldChange', 'padj', 'pvalue'}
            
            if not expected_cols.issubset(set(third_level_cols)):
                missing_cols = expected_cols - set(third_level_cols)
                QMessageBox.critical(self, "DataFrame Format Error", 
                                   f"Missing required columns in the third level: {missing_cols}\n"
                                   f"Found columns: {list(third_level_cols)}\n"
                                   "Expected format: columns from get_stats_deseq2_against_control_with_conditon function.")
                return False
            
            # Check if DataFrame is not empty
            if df.empty:
                QMessageBox.warning(self, "DataFrame Warning", 
                                  "The passed DataFrame is empty.")
                return False
            
            print(f"Successfully validated external DESeq2 DataFrame with shape: {df.shape}")
            print(f"First level (conditions): {list(df.columns.get_level_values(0).unique())}")
            print(f"Second level (groups): {list(df.columns.get_level_values(1).unique())}")
            print(f"Third level (metrics): {list(df.columns.get_level_values(2).unique())}")
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "DataFrame Validation Error", 
                               f"Error validating DataFrame format:\n{str(e)}\n\n"
                               "Please ensure the DataFrame is generated by:\n"
                               "cross_test.get_stats_deseq2_against_control_with_conditon()")
            return False
    
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create controls for the upper part
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # File selection part
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select deseq2allinCondition(XXX).tsv file...")
        self.file_path_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_button)
        
        # Add button to extract all entries
        extract_all_button = QPushButton("Extract All Entries")
        extract_all_button.clicked.connect(self.extract_all_items)
        file_layout.addWidget(extract_all_button)
        
        # Filter entries part
        filter_layout = QHBoxLayout()
        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Enter filter conditions (use ## to separate multiple conditions)")
        filter_button = QPushButton("Filter and Add Entries")
        filter_button.clicked.connect(self.filter_and_add_items)
        self.use_regex_checkbox = QCheckBox("Use Regular Expression")
        filter_layout.addWidget(self.filter_text)
        filter_layout.addWidget(self.use_regex_checkbox)
        filter_layout.addWidget(filter_button)
        
        # Entry list input part
        genes_layout = QVBoxLayout()
        genes_label = QLabel("Enter or paste a list of entries (one per line) or drag-and-drop files (.tsv, .csv, .xlsx, .txt):")
        # Use custom text edit widget supporting drag-and-drop
        self.genes_text = DragDropTextEdit(self)
        genes_layout.addWidget(genes_label)
        genes_layout.addWidget(self.genes_text)
        
        # Add buttons to load entry list from file and clear entries
        genes_button_layout = QHBoxLayout()
        load_genes_button = QPushButton("Load Entry List from File")
        load_genes_button.clicked.connect(self.browse_gene_list_file)
        clear_genes_button = QPushButton("Clear All Entries")
        clear_genes_button.clicked.connect(self.clear_all_genes)
        genes_button_layout.addWidget(load_genes_button)
        genes_button_layout.addWidget(clear_genes_button)
        genes_layout.addLayout(genes_button_layout)
        
        # Add process button
        process_button = QPushButton("Process Data")
        process_button.clicked.connect(self.process_data)
        
        # Add controls to input layout
        input_layout.addLayout(file_layout)
        input_layout.addLayout(filter_layout)
        input_layout.addLayout(genes_layout)
        input_layout.addWidget(process_button)
        
        # Create data display area for the lower part
        self.results_tabs = QTabWidget()
        
        # Create splitter to adjust the size of upper and lower areas
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(input_widget)
        splitter.addWidget(self.results_tabs)
        splitter.setSizes([300, 500])  # Set initial sizes
        
        # Output directory selection
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Select output directory...")
        self.output_dir_edit.setReadOnly(True)
        output_browse_button = QPushButton("Browse...")
        output_browse_button.clicked.connect(self.browse_output_dir)
        save_button = QPushButton("Save Results")
        save_button.clicked.connect(self.save_results)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_browse_button)
        output_layout.addWidget(save_button)
        
        # Add to main layout
        main_layout.addWidget(splitter)
        main_layout.addLayout(output_layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select deseq2 file", "", "TSV Files (*.tsv)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            # Reset external dataframe when new file is selected
            self.external_deseq2_df = None
            self.external_deseq2_df_name = None
            self.df_res = None
    
    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def browse_gene_list_file(self):
        """Open file dialog to select a file containing the entry list"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Entry List File", "", "Supported Files (*.tsv *.csv *.xlsx *.txt)"
        )
        if file_path:
            self.load_gene_list_from_file(file_path)
    
    def load_gene_list_from_file(self, file_path):
        """Load entry list from a file and update the text box"""
        try:
            # Select appropriate reading method based on file extension
            genes = []
            if file_path.endswith('.xlsx'):
                # Read the first column of Excel file
                df = pd.read_excel(file_path)
                genes = df.iloc[:, 0].astype(str).tolist()
            elif file_path.endswith('.csv'):
                # Read the first column of CSV file
                df = pd.read_csv(file_path)
                genes = df.iloc[:, 0].astype(str).tolist()
            elif file_path.endswith('.tsv'):
                # Read the first column of TSV file
                df = pd.read_csv(file_path, sep='\t')
                genes = df.iloc[:, 0].astype(str).tolist()
            elif file_path.endswith('.txt'):
                # Read text file, one entry per line
                with open(file_path, 'r') as f:
                    genes = [line.strip() for line in f if line.strip()]
            
            # Remove duplicates from the entry list
            original_count = len(genes)
            genes = list(dict.fromkeys(genes))  # Deduplication method that preserves order
            dedup_count = len(genes)
            
            # Update text box
            if genes:
                self.genes_text.setPlainText('\n'.join(genes))
                message = f"Loaded {len(genes)} entries from file {os.path.basename(file_path)}."
                if original_count > dedup_count:
                    message += f"\nRemoved {original_count - dedup_count} duplicate entry names."
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Warning", "No entry names found in the file.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading entry list:\n{str(e)}")
    
    def extract_all_items(self):
        """Extract all entries from the TSV file"""
        # Check if we have dataframe from parameter or file
        if self.external_deseq2_df is not None:
            df = self.external_deseq2_df
        else:
            file_path = self.file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select a deseq2 file first!")
                return
            try:
                # Read data file
                df = pd.read_csv(file_path, sep="\t", header=[0, 1, 2], index_col=1)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file:\n{str(e)}")
                return

        try:
            items = df.index.tolist()
            
            if items:
                self.genes_text.setPlainText('\n'.join(items))
                QMessageBox.information(self, "Success", f"Added {len(items)} entries.")
            else:
                QMessageBox.warning(self, "Warning", "No entries found in the data.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error extracting entries:\n{str(e)}")

    def filter_and_add_items(self):
        """Extract entries based on filter conditions"""
        # Check if we have dataframe from parameter or file
        if self.external_deseq2_df is not None:
            df = self.external_deseq2_df
        else:
            file_path = self.file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select a deseq2 file first!")
                return
            try:
                # Read data file
                df = pd.read_csv(file_path, sep="\t", header=[0, 1, 2], index_col=1)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file:\n{str(e)}")
                return

        filter_text = self.filter_text.text().strip()
        if not filter_text:
            QMessageBox.warning(self, "Warning", "Please enter filter conditions!")
            return

        try:
            items = df.index.tolist()
            
            # Split filter conditions
            conditions = filter_text.split("##")
            matched_items = set()

            # Use regular expression or plain text matching
            for condition in conditions:
                condition = condition.strip()
                if condition:
                    if self.use_regex_checkbox.isChecked():
                        try:
                            pattern = re.compile(condition)
                            matched = [item for item in items if pattern.search(str(item))]
                        except re.error as e:
                            QMessageBox.critical(self, "Error", f"Regex syntax error: {str(e)}")
                            return
                    else:
                        matched = [item for item in items if condition in str(item)]
                    matched_items.update(matched)

            if matched_items:
                # Get current text box content
                current_text = self.genes_text.toPlainText().strip()
                # If there is existing content, add to the end
                if current_text:
                    new_text = current_text + '\n' + '\n'.join(sorted(matched_items))
                else:
                    new_text = '\n'.join(sorted(matched_items))
                self.genes_text.setPlainText(new_text)
                QMessageBox.information(self, "Success", f"Added {len(matched_items)} matching entries.")
            else:
                QMessageBox.warning(self, "Warning", "No matching entries found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing data:\n{str(e)}")

    def process_data(self):
        # Check if we have dataframe from parameter or file
        if self.external_deseq2_df is not None:
            # Use external dataframe
            self.df_res = self.external_deseq2_df.copy()
            # Remove the first column (index) if it exists and is not part of the data
            # For external dataframe, we don't need to remove the first column as it should be properly formatted
        else:
            # Check if file is selected
            file_path = self.file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select a deseq2 file first!")
                return
            
            try:
                # Read data file
                progress_msg = QProgressDialog("Reading data file...", None, 0, 0, self)
                progress_msg.setWindowTitle("Processing")
                progress_msg.setModal(True)
                progress_msg.setCancelButton(None)
                progress_msg.setMinimumDuration(0)
                progress_msg.show()
                QApplication.processEvents()
                
                # Optimization: Use engine='c' and low_memory=False to speed up reading large files
                self.df_res = pd.read_csv(file_path, sep="\t", header=[0, 1, 2], index_col=1, engine='c', low_memory=False)
                # Remove the first column (index)
                self.df_res = self.df_res.iloc[:, 1:]
                
                progress_msg.close()
                
            except Exception as e:
                if 'progress_msg' in locals():
                    progress_msg.close()
                QMessageBox.critical(self, "Error", f"Error reading file:\n{str(e)}")
                return
        
        # Get entry list
        genes_text = self.genes_text.toPlainText().strip()
        if not genes_text:
            QMessageBox.warning(self, "Warning", "Please enter a list of entries!")
            return
        
        # Show processing progress message
        progress_msg = QProgressDialog("Processing data, please wait...", None, 0, 0, self)
        progress_msg.setWindowTitle("Processing")
        progress_msg.setModal(True)
        progress_msg.setCancelButton(None)
        progress_msg.setMinimumDuration(0)
        progress_msg.show()
        QApplication.processEvents()  # Ensure the message box is displayed
        
        # Convert text to entry list
        ex_list_original = [gene.strip() for gene in genes_text.split('\n') if gene.strip()]
        
        # Remove duplicates from the entry list
        ex_list_original_count = len(ex_list_original)
        ex_list = list(dict.fromkeys(ex_list_original))  # Deduplication method that preserves order
        ex_list_dedup_count = len(ex_list)
        
        dedup_message = ""
        if ex_list_original_count > ex_list_dedup_count:
            dedup_message = f"Found and removed {ex_list_original_count - ex_list_dedup_count} duplicate entry names.\n"

        try:
            progress_msg.setLabelText("Checking if entries exist...")
            QApplication.processEvents()
            
            # Optimization: Convert index to set to speed up lookup
            index_set = set(self.df_res.index)
            missing_genes = [gene for gene in ex_list if gene not in index_set]
            
            progress_msg.setLabelText("Extracting data...")
            QApplication.processEvents()
            
            # Show missing entries
            if missing_genes:
                # Remove non-existent entries from the list
                ex_list = [gene for gene in ex_list if gene in index_set]
            
            # If there are no valid entries, prompt the user and abort processing
            if not ex_list:
                progress_msg.close()  # Close progress message
                QMessageBox.critical(self, "Error", "All provided entries were not found in the dataset, unable to proceed.")
                return
            
            # Extract data for selected entries
            self.df_ex = self.df_res.loc[ex_list]
            
            progress_msg.setLabelText("Extracting log2FoldChange, padj, and pvalue values...")
            QApplication.processEvents()
            
            # Optimization: Extract all required columns at once
            cols = ['log2FoldChange', 'padj', 'pvalue']
            
            # Optimization: Directly extract specific entries and columns to reduce memory usage
            self.df_ex = self.df_res.loc[ex_list, (slice(None), slice(None), cols)]
            
            # Create a dictionary of dataframes to improve efficiency
            dfs = {}
            for col in cols:
                df = self.df_ex.loc[:, (slice(None), slice(None), col)]
                df.columns = df.columns.droplevel(2)
                df.columns = ["~".join(col) for col in df.columns.values]
                dfs[col] = df
            
            self.df_log2FC = dfs['log2FoldChange']
            self.df_padj = dfs['padj']
            self.df_pvalue = dfs['pvalue']
            
            progress_msg.setLabelText("Converting data format...")
            QApplication.processEvents()
            
            # Optimization: Parallel processing for long format conversion
            long_dfs = {}
            for col_name, df in dfs.items():
                df_long = df.melt(ignore_index=False).reset_index()
                df_long.columns = ["items", "condition", col_name]
                long_dfs[col_name] = df_long
            
            # Optimization: Use reduce to merge all dataframes
            from functools import reduce
            self.df_long = reduce(
                lambda left, right: pd.merge(left, right, on=["items", "condition"]),
                long_dfs.values()
            )
            
            # Add condition columns
            self.df_long['cond1'] = self.df_long['condition'].str.split("~").str[0]
            self.df_long['cond2'] = self.df_long['condition'].str.split("~").str[1]
            
            # remove the row log2FoldChange is nan
            self.df_long = self.df_long[~self.df_long['log2FoldChange'].isna()]
            
            self.df_long.set_index('items', inplace=True)
            
            progress_msg.setLabelText("Preparing Data Display...")
            QApplication.processEvents()
            
            self.display_results()  # Display results

            progress_msg.setLabelText("Completing UI updates...")
            QApplication.processEvents()
            
            progress_msg.close()  # First close the progress dialog
            
            # Construct success message
            success_message = f"{dedup_message}Original number of input entries: {ex_list_original_count}\n"
            success_message += f"Number of deduplicated entries: {ex_list_dedup_count}\n"
            
            if missing_genes:
                success_message += f"Number of missing entries: {len(missing_genes)}\n"
                success_message += f"Number of entries processed: {len(ex_list)}\n"
            else:
                success_message += "All entries were found in the dataset\n"
                
            success_message += "\nData processing successful!"
            
            # Use a simple message box, do not use QTimer
            QMessageBox.information(self, "Processing Results", success_message)
            
            # If missing genes need to be displayed, use a separate non-modal dialog
            if missing_genes:
                dialog = MissingGenesDialog(missing_genes, self)
                dialog.show()  # Use show() instead of exec(), so it does not block the UI
            
        except Exception as e:
            progress_msg.close()
            QMessageBox.critical(self, "Error", f"Error processing data:\n{str(e)}")
    
    def display_results(self):
        # Clear existing tabs
        self.results_tabs.clear()
        
        # Number of rows per page
        rows_per_page = 100
        
        def setup_table_view(table_view, model):
            # Set table view properties
            table_view.setModel(model)
            table_view.resizeColumnsToContents()
            table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
            # Set table optimization options
            table_view.verticalHeader().setDefaultSectionSize(25)  # Set row height
            table_view.setHorizontalScrollMode(QTableView.ScrollPerPixel)
            table_view.setVerticalScrollMode(QTableView.ScrollPerPixel)
            table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            table_view.horizontalHeader().setStretchLastSection(True)
            table_view.setWordWrap(False)  # Disable word wrap
            table_view.setAlternatingRowColors(True)  # Set alternating row colors
            
            return table_view

        def create_table_tab(df, tab_name):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Create pagination controls
            page_layout = QHBoxLayout()
            page_label = QLabel("Page:")
            current_page = QLineEdit()
            current_page.setFixedWidth(50)
            total_pages = (len(df) + rows_per_page - 1) // rows_per_page
            total_label = QLabel(f"/ {total_pages}")
            prev_button = QPushButton("Previous Page")
            next_button = QPushButton("Next Page")
            
            page_layout.addWidget(page_label)
            page_layout.addWidget(current_page)
            page_layout.addWidget(total_label)
            page_layout.addWidget(prev_button)
            page_layout.addWidget(next_button)
            page_layout.addStretch()
            
            # Create table view
            table_view = QTableView()
            df.index.name = 'Item_ID'  # Set index name
            model = PandasModel(df.iloc[:rows_per_page])  # Initially display the first page
            setup_table_view(table_view, model)
            
            # Set page update logic
            current_page.setText("1")
            
            def update_table(page_num):
                start_idx = (page_num - 1) * rows_per_page
                end_idx = min(start_idx + rows_per_page, len(df))
                model = PandasModel(df.iloc[start_idx:end_idx])
                table_view.setModel(model)
                table_view.reset()
            
            def on_page_changed():
                try:
                    page = int(current_page.text())
                    if 1 <= page <= total_pages:
                        update_table(page)
                    else:
                        current_page.setText("1")
                except ValueError:
                    current_page.setText("1")
            
            def on_prev_page():
                try:
                    page = max(1, int(current_page.text()) - 1)
                    current_page.setText(str(page))
                    update_table(page)
                except ValueError:
                    current_page.setText("1")
            
            def on_next_page():
                try:
                    page = min(total_pages, int(current_page.text()) + 1)
                    current_page.setText(str(page))
                    update_table(page)
                except ValueError:
                    current_page.setText("1")
            
            current_page.returnPressed.connect(on_page_changed)
            prev_button.clicked.connect(on_prev_page)
            next_button.clicked.connect(on_next_page)
            
            layout.addLayout(page_layout)
            layout.addWidget(table_view)
            return tab

        # Create tabs for each dataframe
        if self.df_log2FC is not None:
            self.results_tabs.addTab(create_table_tab(self.df_log2FC, "log2FoldChange"), "log2FoldChange")
        
        if self.df_padj is not None:
            self.results_tabs.addTab(create_table_tab(self.df_padj, "padj"), "padj")
        
        if self.df_pvalue is not None:
            self.results_tabs.addTab(create_table_tab(self.df_pvalue, "pvalue"), "pvalue")
        
        if self.df_long is not None:
            self.results_tabs.addTab(create_table_tab(self.df_long, "Combined Long Format"), "Combined Long Format")
    
    def save_results(self):
        # Check if there is data to save
        if self.df_long is None or self.df_log2FC is None or self.df_padj is None:
            QMessageBox.warning(self, "Warning", "No data to save! Please process the data first.")
            return
        
        # Check output directory
        output_dir = self.output_dir_edit.text()
        if not output_dir:
            output_dir, _ = QFileDialog.getSaveFileName(
                self, "Save results to folder", "", "All Files (*)"
            )
            if not output_dir:
                return
            self.output_dir_edit.setText(output_dir)
        
        try:
            # Ensure the directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save dataframes
            self.df_long.to_csv(os.path.join(output_dir, "combined_long.tsv"), sep="\t", index=True)
            self.df_log2FC.to_csv(os.path.join(output_dir, "log2FC.tsv"), sep="\t", index=True)
            self.df_padj.to_csv(os.path.join(output_dir, "padj.tsv"), sep="\t", index=True)
            self.df_pvalue.to_csv(os.path.join(output_dir, "pvalue.tsv"), sep="\t", index=True)
            
            QMessageBox.information(self, "Success", f"Results saved to directory:\n{output_dir}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving data:\n{str(e)}")
    
    def clear_all_genes(self):
        """Clear all entries in the text box"""
        if self.genes_text.toPlainText().strip():
            reply = QMessageBox.question(
                self, 
                "Confirm", 
                "Are you sure you want to clear all entries?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.genes_text.clear()
                QMessageBox.information(self, "Success", "All entries cleared.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeneExtractorApp()
    window.show()
    sys.exit(app.exec())