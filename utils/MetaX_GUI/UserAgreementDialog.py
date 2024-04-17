from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QTimer

class UserAgreementDialog(QDialog):
    def __init__(self, parent=None):
        super(UserAgreementDialog, self).__init__(parent)
        self.setWindowTitle("User Agreement")
        self.resize(800, 600)
        self.setupUI()
        self.setupConnections()

    def setupUI(self):
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setHtml("""
        <html>
            <head>
                <style>
                    body { font-family: 'Arial', sans-serif; }
                    a { color: #337ab7; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h2>Welcome to MetaX!</h2>
                <p>MetaX is an open-source software developed by Northomics Lab, designed specifically for academic and research use. By downloading, installing, or using MetaX, you are agreeing to be bound by the terms of this license agreement.</p>
                
                <h3>License</h3>
                <p>MetaX grants you a revocable, non-exclusive, non-transferable, limited license to download, install, and use the software solely for academic and research purposes, strictly in accordance with the terms of this agreement.</p>
                
                <h3>Restrictions</h3>
                <p>You agree not to, and you will not permit others to:</p>
                <ul>
                    <li>Use the software for any commercial purposes.</li>
                    <li>Sell, lease, loan, or rent the software or use the software for commercial time-sharing or service bureau use.</li>
                    <li>Modify, make derivative works of, disassemble, reverse compile, or reverse engineer any part of the software, except to the extent the foregoing restrictions are expressly prohibited by applicable law.</li>
                    <li>Remove any proprietary notices or labels on the software.</li>
                </ul>
                
                <h3>Intellectual Property</h3>
                <p>The software and all copyrights, trademarks, patents, trade secrets, and other intellectual property associated with it are, and remain, the exclusive property of MetaX and its licensors, including Northomics Lab. For more information about Northomics Lab, visit <a href="https://www.northomics.ca/">Northomics Lab Website</a>.</p>
                
                <h3>Disclaimer of Warranty</h3>
                <p>MetaX is provided "as is," without warranty of any kind, express or implied. The entire risk as to the quality and performance of the software is with you.</p>
                
                <h3>Limitation of Liability</h3>
                <p>In no event will MetaX be liable for any damages, including without limitation direct or indirect, special, incidental, or consequential damages, losses or expenses arising out of or in connection with the use of MetaX, even if MetaX has been advised of the possibility of such damages.</p>
                
                <h3>Contributions</h3>
                <p>If you contribute to the MetaX project, you agree to grant a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute your contributions and such derivative works.</p>
                
                <h3>Amendments to this Agreement</h3>
                <p>MetaX reserves the right to amend this agreement at any time and without notice, and it is your responsibility to review this agreement for any changes.</p>
                
                <h3>Citation</h3>
                <p>Please cite the following paper if you use MetaX in your research:</p>
                <p><b>MetaX: A peptide centric metaproteomic data analysis platform using Operational Taxa-Functions (OTF)</b></p>
                
                <br>
                <h3>Additional Information</h3>
                <p>For more information on Terms of Use, please visit:</p>
                <p>GitHub: <a href='https://github.com/byemaxx/MetaX'>The MetaX Project</a></p>
                <p>iMeta: <a href='https://wiki.imetalab.ca/'>iMetaWiki Page</a></p>
                
                <br>
                <h3>Do you agree to the terms of the license agreement?</h3>
            </body>
        </html>
        """)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.buttonBox.button(QDialogButtonBox.Yes).setEnabled(False)  # Disable the 'Yes' button initially

        layout = QVBoxLayout(self)
        layout.addWidget(self.textBrowser)
        layout.addWidget(self.buttonBox)

    def setupConnections(self):
        self.textBrowser.verticalScrollBar().valueChanged.connect(self.checkScrollBarPosition)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def showEvent(self, event):
        super().showEvent(event)
        # Delay the scrollbar check slightly to ensure UI is fully rendered
        QTimer.singleShot(100, self.checkInitialScrollBar)  # 100 ms delay

    def checkInitialScrollBar(self):
        # Enable the 'Yes' button if no scrolling is needed
        if self.textBrowser.verticalScrollBar().maximum() == 0:
            self.buttonBox.button(QDialogButtonBox.Yes).setEnabled(True)

    def checkScrollBarPosition(self, value):
        # Enable the 'Yes' button only if the user has scrolled to the bottom
        scroll_bar = self.textBrowser.verticalScrollBar()
        if value == scroll_bar.maximum():
            self.buttonBox.button(QDialogButtonBox.Yes).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Yes).setEnabled(False)
# Example usage within a main window or other parts of a PyQt application:
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = QDialog()  # This would be your main application window
    agreement_dialog = UserAgreementDialog(main_window)
    result = agreement_dialog.exec_()  # Show the dialog and block until closed

    if result == QDialog.Accepted:
        print("User agreed.")
    else:
        print("User disagreed.")
        QMessageBox.warning(None, "Warning", "You must agree to the license agreement to use this software.")
