from PyQt5 import QtWidgets, QtCore, QtGui

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self.checkedItemsOrder = []  # 用于存储勾选项的顺序

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        item_text = item.text()
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            # 从列表中移除取消勾选的项
            if item_text in self.checkedItemsOrder:
                self.checkedItemsOrder.remove(item_text)
        else:
            item.setCheckState(QtCore.Qt.Checked)
            # 添加勾选的项到列表中
            if item_text not in self.checkedItemsOrder:
                self.checkedItemsOrder.append(item_text)

    def paintEvent(self, e):
        painter = QtWidgets.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))

        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        # 按照勾选顺序显示
        opt.currentText = ", ".join(self.checkedItemsOrder)

        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt)
        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

    def getCheckedItems(self):
        return self.checkedItemsOrder  # 返回勾选项的顺序列表


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
        self.checkedItemsOrder = []  # 清空当前的勾选顺序列表
        for i in range(self.count()):
            item = self.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Checked)
            # 添加每个勾选的项到勾选顺序列表中
            self.checkedItemsOrder.append(item.text())

    def unselectAll(self):
        for i in range(self.count()):
            item = self.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.checkedItemsOrder = []  # 清空勾选顺序列表
