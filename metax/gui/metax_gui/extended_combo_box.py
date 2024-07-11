from PyQt5.QtCore import Qt, QSortFilterProxyModel, QTimer, pyqtSignal
from PyQt5.QtWidgets import QCompleter, QComboBox, QMenu, QAction

class ExtendedComboBox(QComboBox):
    # Define a custom signal for returning all searched items
    add_all_searched = pyqtSignal(list)

    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

        # connect signals
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.updateFilter)
        self.lineEdit().textEdited.connect(self.startTimer)

        self.completer.activated.connect(self.on_completer_activated)
        self.textToSearch = ""

        # Add right-click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    # start timer when text edited
    def startTimer(self, text):
        self.textToSearch = text
        self.timer.start(300)

    # update filter after 300ms and with at least 3 characters
    def updateFilter(self):
        if len(self.textToSearch) >= 2:
            self.pFilterModel.setFilterFixedString(self.textToSearch)
            self.setCompleter(self.completer)
        else:
            self.setCompleter(None)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)

    # Show context menu
    def showContextMenu(self, position):
        contextMenu = QMenu(self)
        addAllAction = QAction("Add all matched items", self)
        contextMenu.addAction(addAllAction)

        addAllAction.triggered.connect(self.addAllSearched)
        
        contextMenu.exec_(self.mapToGlobal(position))

    # Triggered when 'add all searched' is clicked
    def addAllSearched(self):
        # Apply the current filter based on the text in the input field
        self.textToSearch = self.currentText().strip()
        self.updateFilter()

        current_text = self.currentText().strip()
        if not current_text or current_text in ["All Taxa", "All Functions", "All Taxa-Functions", "All Peptides, All Proteins, All Items"]:
            print(f'ComboBox has special value "{current_text}". No items to search.')
            return

        all_items = []
        for i in range(self.pFilterModel.rowCount()):
            index = self.pFilterModel.index(i, 0)
            item_text = self.pFilterModel.data(index, Qt.DisplayRole)
            if item_text not in ["All Taxa", "All Functions", "All Taxa-Functions", "All Peptides", "All Proteins", "All Items"]:
                all_items.append(item_text)
        self.add_all_searched.emit(all_items)