# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showTagsDialog.ui'
#
# Created: Wed Jan 25 00:05:15 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (QVariant, Qt, SIGNAL)
from PyQt4.QtGui import *

from mutagen import File
import re
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class showTagDialog(QDialog):
    def __init__(self, parent=None):
        super(showTagDialog, self).__init__(parent)
        self.setupUi(self)
        
    def setInfos(self,tags):
        if os.path.exists(".temp.jpg"):
            self.imagelabel.setPixmap(QPixmap(".temp.jpg").scaled(150, 150, Qt.KeepAspectRatio, transformMode=Qt.FastTransformation))
        else:
            self.imagelabel.setText("[No - artwork]")
            
        temp = "Title: {0}".format(tags['TIT2']) if tags.has_key('TIT2') else "Title: /"
        self.titlelabel.setText(temp)
        temp = "Artist: %s" %(tags['TPE1']) if tags.has_key('TPE1') else "Artist: /"
        self.artistlabel.setText(temp)
        
        temp = "Album: %s" %(tags['TALB']) if tags.has_key('TALB') else "Album: /"
        self.albumlabel.setText(temp)        
        temp = "Track Number: %s" %(tags['TRCK']) if tags.has_key('TRCK') else "Track Number: /"
        self.tracklabel.setText(temp)
        temp = "Disk Number: %s" %(tags['TPOS']) if tags.has_key('TPOS') else "Disk Number: /"
        self.label_7.setText(temp)
        temp = "Year: %s" %(tags['TRDC']) if tags.has_key('TRDC') else "Year: /"
        self.yearlabel.setText(temp)
        temp = "Comment: %s" %(tags['COMM']) if tags.has_key('COMM') else "Comment: /"
        self.commentlabel.setText(temp)
        temp = "Genre: %s" %(tags['TCON']) if tags.has_key('TCON') else "Genre: /"
        self.genrelabel.setText(temp)
        temp = "Composer: %s" %(tags['TCOM']) if tags.has_key('TCOM') else "Composer: /"
        self.composerlabel.setText(temp)
        for head in tags.keys(): # For all keys
            if re.search("USLT::",head): #if keys contain USLT
                for line in tags[head].text.split("\n"):
                    self.lyricslist.addItem(QListWidgetItem(line))           
        
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(582, 407)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.imagelabel = QtGui.QLabel(Dialog)
        self.imagelabel.setObjectName(_fromUtf8("imagelabel"))
        self.horizontalLayout_2.addWidget(self.imagelabel)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.titlelabel = QtGui.QLabel(Dialog)
        self.titlelabel.setObjectName(_fromUtf8("titlelabel"))
        self.verticalLayout_2.addWidget(self.titlelabel)
        self.artistlabel = QtGui.QLabel(Dialog)
        self.artistlabel.setObjectName(_fromUtf8("artistlabel"))
        self.verticalLayout_2.addWidget(self.artistlabel)
        self.albumlabel = QtGui.QLabel(Dialog)
        self.albumlabel.setObjectName(_fromUtf8("albumlabel"))
        self.verticalLayout_2.addWidget(self.albumlabel)
        self.yearlabel = QtGui.QLabel(Dialog)
        self.yearlabel.setObjectName(_fromUtf8("yearlabel"))
        self.verticalLayout_2.addWidget(self.yearlabel)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.tracklabel = QtGui.QLabel(Dialog)
        self.tracklabel.setObjectName(_fromUtf8("tracklabel"))
        self.verticalLayout_4.addWidget(self.tracklabel)
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_4.addWidget(self.label_7)
        self.commentlabel = QtGui.QLabel(Dialog)
        self.commentlabel.setObjectName(_fromUtf8("commentlabel"))
        self.verticalLayout_4.addWidget(self.commentlabel)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.genrelabel = QtGui.QLabel(Dialog)
        self.genrelabel.setObjectName(_fromUtf8("genrelabel"))
        self.verticalLayout_3.addWidget(self.genrelabel)
        self.composerlabel = QtGui.QLabel(Dialog)
        self.composerlabel.setObjectName(_fromUtf8("composerlabel"))
        self.verticalLayout_3.addWidget(self.composerlabel)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.lyricslist = QtGui.QListWidget(Dialog)
        self.lyricslist.setObjectName(_fromUtf8("lyricslist"))
        self.verticalLayout.addWidget(self.lyricslist)
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
        self.imagelabel.setText(QtGui.QApplication.translate("Dialog", "Image", None, QtGui.QApplication.UnicodeUTF8))
        self.titlelabel.setText(QtGui.QApplication.translate("Dialog", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.artistlabel.setText(QtGui.QApplication.translate("Dialog", "Artist", None, QtGui.QApplication.UnicodeUTF8))
        self.albumlabel.setText(QtGui.QApplication.translate("Dialog", "Album", None, QtGui.QApplication.UnicodeUTF8))
        self.yearlabel.setText(QtGui.QApplication.translate("Dialog", "Year", None, QtGui.QApplication.UnicodeUTF8))
        self.tracklabel.setText(QtGui.QApplication.translate("Dialog", "Track Number", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Disc Number", None, QtGui.QApplication.UnicodeUTF8))
        self.commentlabel.setText(QtGui.QApplication.translate("Dialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.genrelabel.setText(QtGui.QApplication.translate("Dialog", "Genre", None, QtGui.QApplication.UnicodeUTF8))
        self.composerlabel.setText(QtGui.QApplication.translate("Dialog", "Composer", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = showTagDialog()
    form.show()
    app.exec_()