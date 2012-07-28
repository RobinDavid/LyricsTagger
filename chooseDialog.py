# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chooseForm.ui'
#
# Created: Sun Jan 22 23:28:34 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (QVariant, Qt, SIGNAL)
from PyQt4.QtGui import *
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class chooseDialog(QDialog):
    def __init__(self, parent=None):
        super(chooseDialog, self).__init__(parent)
        self.setupUi(self)
        for i in range(15):
            self.listWidget.addItem(QListWidgetItem(str(i)))
        self.connect(self.listWidget, SIGNAL("itemSelectionChanged()"), self.changeVal)
        
    def changeVal(self):
        cur = self.listWidget.currentItem().text()
        self.selected.setText("Selected: %s" % (cur))
    
    def setList(self, list):
        self.listWidget.clear()
        for elt in list:
            self.listWidget.addItem(QListWidgetItem(elt[0]))
    
    def setTitle(self,title, text):
        self.setWindowTitle(title)
        self.label.setText(text)
    
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        self.selected = QtGui.QLabel(Dialog)
        self.selected.setObjectName(_fromUtf8("selected"))
        self.verticalLayout.addWidget(self.selected)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.selected.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = chooseDialog()
    form.show()
    app.exec_()

