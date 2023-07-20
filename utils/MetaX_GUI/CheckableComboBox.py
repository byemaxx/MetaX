from PyQt5 import QtWidgets, QtCore, QtGui

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

    def paintEvent(self, e):
        painter = QtWidgets.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))

        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.currentText = ", ".join(
            [self.itemText(i) for i in range(self.count())
             if self.itemData(i, QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked])

        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt)
        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

    def getCheckedItems(self):
        return [self.itemText(i) for i in range(self.count())
                if self.itemData(i, QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked]

    # 添加右键菜单
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        select_all_action = QtWidgets.QAction("Select All", self)
        select_all_action.triggered.connect(self.selectAll)
        unselect_all_action = QtWidgets.QAction("Unselect All", self)
        unselect_all_action.triggered.connect(self.unselectAll)
        menu.addAction(select_all_action)
        menu.addAction(unselect_all_action)
        menu.exec_(self.mapToGlobal(event.pos()))

    def selectAll(self):
        for i in range(self.count()):
            item = self.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Checked)

    def unselectAll(self):
        for i in range(self.count()):
            item = self.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
