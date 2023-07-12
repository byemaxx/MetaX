from PyQt5.QtCore import Qt, QSortFilterProxyModel, QTimer
from PyQt5.QtWidgets import QCompleter, QComboBox

class ExtendedComboBox(QComboBox):
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
