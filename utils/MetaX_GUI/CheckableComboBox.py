from PyQt5 import QtWidgets, QtCore, QtGui

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None, meta_df = None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self.checkedItemsOrder = []  # 用于存储勾选项的顺序
        self._popup_open = False
        self.meta_df = meta_df


    def showPopup(self):
        super(CheckableComboBox, self).showPopup()
        self._popup_open = True

    def hidePopup(self):
        if self.view().underMouse():
            # 如果鼠标在下拉列表内，保持下拉列表打开
            return
        super(CheckableComboBox, self).hidePopup()
        self._popup_open = False

    def mousePressEvent(self, event):
        if self._popup_open and not self.view().rect().contains(event.pos()):
            self.hidePopup()
        super(CheckableComboBox, self).mousePressEvent(event)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        item_text = item.text()
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            if item_text in self.checkedItemsOrder:
                self.checkedItemsOrder.remove(item_text)
        else:
            item.setCheckState(QtCore.Qt.Checked)
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


    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        
        select_all_action = QtWidgets.QAction("Select All", self)
        select_all_action.triggered.connect(self.selectAll)
        
        unselect_all_action = QtWidgets.QAction("Unselect All", self)
        unselect_all_action.triggered.connect(self.unselectAll)

        menu.addAction(select_all_action)
        menu.addAction(unselect_all_action)

        if self.meta_df is not None:
            add_samples_action = QtWidgets.QMenu("Add samples by group", self)
            for col in self.meta_df.columns[1:]:  # 从第二列开始
                group_menu = QtWidgets.QMenu(col, self)
                for group_name in self.meta_df[col].unique():
                    group_action = QtWidgets.QAction(group_name, self)
                    group_action.triggered.connect(lambda checked, col=col, group_name=group_name: self.addSamplesByGroup(col, group_name))
                    group_menu.addAction(group_action)
                add_samples_action.addMenu(group_menu)
            menu.addMenu(add_samples_action)

        menu.exec_(self.mapToGlobal(event.pos()))
        
        
    def addSamplesByGroup(self, column_name, group_name):
        if self.meta_df is not None:
            samples_to_add = self.meta_df[self.meta_df[column_name] == group_name]['Sample']
            for sample in samples_to_add:
                if sample not in self.checkedItemsOrder:
                    # self.addItem(sample)
                    self.checkedItemsOrder.append(sample)
                    index = self.findText(sample)
                    if index != -1:
                        item = self.model().item(index, 0)
                        item.setCheckState(QtCore.Qt.Checked)
                        
                        
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
    
    def select_first(self):
        item = self.model().item(0, 0)
        item.setCheckState(QtCore.Qt.Checked)
        self.checkedItemsOrder.append(item.text())