#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import (Qt, SIGNAL, SLOT, PYQT_VERSION_STR, QT_VERSION_STR)
from PyQt4.QtGui import * #QApplication, QMainWindow
import ui_taggergui
import qrc_resources
import platform
import os
from chooseDialog import chooseDialog

from ParolesManiaGrabber import ParolesManiaGrabber
import time
import re
# Mutagen packages
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, USLT
from mutagen import File
from compatid3 import CompatID3
from showtagDialog import showTagDialog
#--------------

__version__ = "1.1"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class MainWindow(QMainWindow, ui_taggergui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.setupUi()
        self.setupUi(self)
        
        #--- variables ---
        self.filename = None
        self.log_file = None
        self.PM = ParolesManiaGrabber()
        self.RECURSIVE = None
        self.OVERRIDE_EXISTING_LYRICS = None
        self.COMPATIBILITY_WMP = None
        self.VERBOSE = None
        self.artist = ""
        self.title = ""
        self.artist_skipped = False
        self.currentItem = 0
        self.totalcount = 0
        self.stopped = False
        self.paused = False
        self.pause_clicked = False
        self.backItem = 0
        #-----------------
        
        self.showTag.setVisible(False)
        self.labelprogressBar.setVisible(False)
        self.progressBar.setVisible(False)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.checkVerbose.setChecked(True)
        self.checkOverride.setChecked(True)
        self.checkID3.setChecked(True)
        self.checkRecursive.setChecked(True)
        
        self.artistfield.setFocus()
        
        self.connect(self.search, SIGNAL("clicked()"), self.searchClicked)
        self.connect(self.chooseFile, SIGNAL("clicked()"), self.openFile)
        self.connect(self.toolButton, SIGNAL("clicked()"), self.openDir)
        self.connect(self.showTag, SIGNAL("clicked()"), self.showTags)
        self.connect(self.pauseButton, SIGNAL("clicked()"), self.pauseProcessing)
        self.connect(self.goButton, SIGNAL("clicked()"), self.run)
        self.connect(self.stopButton, SIGNAL("clicked()"), self.stopProcessing)
        
        self.connect(self.actionOpen_Directory, SIGNAL("triggered()"), self.openDir)
        self.connect(self.actionOpen_File, SIGNAL("triggered()"), self.openFile)
        self.connect(self.actionExit, SIGNAL("triggered()"), qApp, SLOT("quit()"))
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.about)

    def processFile(self, filename):
        
        self.log(filename)
        name = os.path.split(filename)[1]
        # create ID3 tag if not exists
        try: 
            tags = ID3(filename)
            newtags = MP3(filename)
        except ID3NoHeaderError:
            self.log("Adding ID3 header",1)
            tags = ID3()
        
        ly_exist = False
        ly_header = ""
        
        #Lookup in mp3 tags if it contains lyrics
        for head in tags.keys(): # For all keys
            if re.search("USLT::",head): #if keys contain USLT
                if len(tags.getall(head)) != 0: #    
                    ly_exist = True
                    ly_header = head   
        
        if ly_exist and not self.OVERRIDE_EXISTING_LYRICS:
            self.log("Lyrics already exist skip",1)
            return True
        
        #global artist #Write it because it's forbidden in python to assign a variable without having declared it before in a block
        #global artist_skipped
        # Change artist only if the new read one is different to avoid useless artist_link requests
        if tags.get("TPE1") is not None:
            newartist = tags.get("TPE1")[0]
            if newartist != self.artist: #set new artist only if he is new
                self.artist = newartist
                if self.PM.setArtist(newartist) is None:#Update only when artist change
                     
                    #------------------------------------------
                    mylist = self.PM.getAvailableArtists()
                    if mylist==[]:
                        self.log("Artist skipped (not found )!",1)
                        self.artist_skipped=True
                        return False
                    mylist.sort()
                    dial = chooseDialog()
                    dial.setTitle("Artist choice","Choose Artist for %s" % (filename))
                    dial.setList(mylist)
                    if dial.exec_():
                        self.PM.resumeSetArtist(dial.listWidget.currentRow())
                        artist_ok = True
                        self.artist_skipped=False
                        self.log("Artist New: "+self.artist,1)
                    else:
                        self.log("Artist skipped (choosed by user)!",1)
                        self.artist_skipped=True
                        return False   
                        
                else:
                    self.artist_skipped=False
                    #self.artist = newartist
                    self.log("Artist New: "+self.artist,1)
    
            else:
                self.log("Artist Same: "+self.artist,1)
                if self.artist_skipped:
                    return False
        else:
            self.log("Artist name not found in ID3 Tags (TPE1)",1)
            self.log(name+" skipped",1)
            return False
        
        
            
        if tags.get("TIT2")[0] != self.title: #Will probably get into each processFile call    
            self.title = tags.get("TIT2")[0]
            if self.title is not None:
                res = self.PM.setTitle(self.title)
                if res is None:

                    #------------------------------------------
                    mylist = self.PM.getAvailableTitles()
                    if mylist == []:
                        self.log("No lyrics found for this title !",1)
                        return False
                    mylist.sort()
                    dial = chooseDialog()
                    dial.setTitle("Title choice","Choose Title for %s" % (filename))
                    dial.setList(mylist)
                    if dial.exec_():
                        self.PM.resumeSetTitle(dial.listWidget.currentRow())
                        if self.PM.lyricsFound():
                            self.log("Lyrics found !",1)
                        else:
                            self.log("No lyrics for this song !",1)
                    else:
                        self.log ("Song skipped (choosed by user)!",1)
                        return False
    
                elif not res:
                    self.log("Artist not set",1)
                    return False
                else:
                    if self.PM.lyricsFound():
                        self.log("Lyrics found !",1)
                    else:
                        self.log("No lyrics for this song !",1)
            else:
                self.log("Title field not found in ID3 Tags (TIT2)",1)
                self.log(name+" skipped",1)
                return False
        
        #-----------------------------------------------------
                
        #!! At this point artist and title are correctly set !    
        '''
        ly_exist = False
        ly_header = ""
        
        #Lookup in mp3 tags if it contains lyrics
        for head in tags.keys(): # For all keys
            if re.search("USLT::",head): #if keys contain USLT
                if len(tags.getall(head)) != 0: #    
                    ly_exist = True
                    ly_header = head   
        '''
        
        if not self.PM.lyricsFound(): #Lyrics are NOT found
            if ly_exist:
                self.log("Lyrics already tagged and not found on ParoleMania (skipped)",1)
                return True #We keep existing lyrics
            else:
                self.log("Lyrics not found in tags and not found on ParolesMania",1)
                return False #No existing lyrics and not found on website
        else: #Lyrics are found on parolesmania
            if ly_exist:
                if self.OVERRIDE_EXISTING_LYRICS: #If lyrics already exist and override true we should  delete them before
                    # remove old unsychronized lyrics
                    self.log("Remove old Lyrics in tags",1)
                    if not self.COMPATIBILITY_WMP: #because if enable useless to remove USLT
                        tags.delall(ly_header)
                        tags.save(filename)
                else: #Lyrics already exist and we should not override them so just exit true
                    self.log("Lyrics already exist skip",1)
                    return True
    
            #From here lyrics will be written in the file anyway    
            lyrics = self.PM.getLyrics()
                
            # USLT frames are present
            if not self.COMPATIBILITY_WMP:
                tags[u"USLT::'eng'"] = (USLT(encoding=1, lang=u'fre', desc=u'', text=lyrics))
                tags.save(filename)    
            else:#Alternative for windows because not compatible with 2.4
                newtags.delete()
                #newtags.save(filename)
                newtags = MP3(filename)
                try:
                    newtags.add_tags(ID3=CompatID3)
                except:
                    print("Into mutagen error !")
                    newtags.delete()
                    newtags = MP3(filename)
                    try:
                        newtags.add_tags(ID3=CompatID3)
                    except:
                        pass
                
                for e in tags.keys(): #Recopy old frames but not old lyrics!
                    if not (ly_exist and e == ly_header):
                        newtags[e] = tags.get(e)
                    else:
                        pass
                        #print e, " Skipped old lyrics!"
                
                #Itunes seems to like encoding=1 'eng' and
                #WIndows Media Player prefer 'fre'         
                newtags[u"USLT::'eng'"] = (USLT(encoding=1, lang=u'fre', desc=u'', text=lyrics))
                    
                newtags.tags.update_to_v23()
            
                #Finally save tags to the file
                newtags.tags.save(filename,v2=3)
            self.log('Lyrics Added to '+name,1)    
            return True
    
    def log(self, mess, nb_tab=0):
        if type(mess) is unicode:
            for enc in ('utf8','iso-8859-1','latin1'):
                try:
                    mess = mess.encode(enc)
                    self.log_file.write("\t"*nb_tab+mess+"\n")
                    self.listContent.addItem(QListWidgetItem("\t"*nb_tab+mess))
                    break
                except:
                    pass
        else:
            self.log_file.write("\t"*nb_tab+mess+"\n")
            self.listContent.addItem(QListWidgetItem("\t"*nb_tab+mess))
    
    def dirLookup(self, dir_path):
        if os.path.isfile(dir_path):#TODO: Add print everywhere for backtrack !
            if self.processFile(dir_path): #log if returned value is false etc..
                self.log("OK\n")
            else:
                self.log("Failed\n")
            self.progressBar.setValue(self.progressBar.value()+1)
            self.listContent.scrollToBottom()
                
        elif os.path.isdir(dir_path):        
            for fn in os.listdir(dir_path):
                if not self.stopped:
                    currentfile = os.path.join(dir_path, fn)
                    if self.RECURSIVE and os.path.isdir(currentfile):
                        self.dirLookup(currentfile) #Make a recursive call if is a directory
                    elif currentfile.lower().endswith('.mp3'):
                        QApplication.processEvents()
                        if self.pause_clicked:
                            print "into pause clicked !"
                            #self.pause_clicked = False
                            return
                        if self.paused:
                            print self.backItem
                            self.backItem = self.backItem -1
                            if self.backItem == 0:
                                self.paused = False
                        else:
                            self.currentItem = self.currentItem + 1
                            self.labelprogressBar.setText("Progression %s/%s" %(self.currentItem,self.totalcount))
                            self.dirLookup(currentfile) # Make also a recursive call 
    
    def run(self):
        if not self.paused:
            self.setupRun()
            self.log_file = open("report.txt","w")
            self.PM.setProxy(str(self.proxyEdit.text()))
            
            self.VERBOSE = True if self.checkVerbose.isChecked() else False
            self.RECURSIVE = True if self.checkRecursive.isChecked() else False
            self.OVERRIDE_EXISTING_LYRICS= True if self.checkOverride.isChecked() else False
            self.COMPATIBILITY_WMP = True if self.checkID3.isChecked() else False
            
            self.listContent.clear()
            if os.path.isfile(self.filename):
                self.progressBar.setMaximum(1)
            else:
                self.totalcount = self.countNbFiles(self.filename)
                self.progressBar.setMaximum(self.totalcount)
        self.labelprogressBar.setText("Progression %s/%s" %(self.currentItem,self.totalcount))
        self.dirLookup(self.filename)
        self.pause_clicked = False
        if not self.paused:
            self.log_file.close()
            self.putback()
        
    def countNbFiles(self, path):
        if os.path.isdir(path):
            count =0
            for f in os.listdir(path):
                currentfile = os.path.join(path,f)
                if self.RECURSIVE and os.path.isdir(currentfile):
                    count += self.countNbFiles(currentfile)
                elif currentfile.lower().endswith('.mp3'):
                    count = count + 1
            return count
    
    def setupRun(self):
        self.searchBox.setEnabled(False)
        self.pathBox.setEnabled(False)
        self.optionBox.setEnabled(False)
        self.actionOpen_File.setEnabled(False)
        self.actionOpen_Directory.setEnabled(False)
        self.goButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.progressBar.setValue(0)
        self.labelprogressBar.setVisible(True)
        self.progressBar.setVisible(True)
        
    
    def putback(self):
        self.artist = ""
        self.title = ""
        self.currentItem = 0
        self.totalcount = 0
        self.stopped = False
        self.artist_skipped = False
        self.searchBox.setEnabled(True)
        self.pathBox.setEnabled(True)
        self.optionBox.setEnabled(True)
        self.actionOpen_File.setEnabled(True)
        self.actionOpen_Directory.setEnabled(True)
        self.goButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.labelprogressBar.setVisible(False)
        self.progressBar.setVisible(False)
    
    def openDir(self):
        dir = "."
        if self.filename is not None:
            dir = os.path.dirname(self.filename)
        fname = unicode(QFileDialog.getExistingDirectory(self, "LyricsTagger - Choose a Directory",dir))
        if not fname == "":
            self.filename = fname
            self.fileSelectEdit.clear()
            self.fileSelectEdit.setEnabled(False)
            self.lineEdit.setText(fname)
            self.lineEdit.setEnabled(True)
            self.lineEdit.setReadOnly(True)
    
    def openFile(self):
        dir = "."
        if self.filename is not None:
            dir = os.path.dirname(self.filename)
        formats = "*.mp3 *.flac"
        fname = unicode(QFileDialog.getOpenFileName(self, "LyricsTagger - Choose a File",dir,formats))
        if not fname == "":
            self.filename = fname
            self.fileSelectEdit.setEnabled(True)
            self.lineEdit.clear()
            self.fileSelectEdit.setText(fname)
            self.showTag.setVisible(True)
            self.lineEdit.setEnabled(False)
            self.fileSelectEdit.setReadOnly(True)
        
    def searchClicked(self):
        self.PM.setProxy(str(self.proxyEdit.text()))
        artist_ok = False
        if self.artistfield.text() == "" or self.titlefield.text() == "":
            QMessageBox.warning(self, "Cannot search", "Artist and Title should be filled", QMessageBox.Ok)
        else:
            dial = chooseDialog()
            if self.PM.setArtist(str(self.artistfield.text())) is None:
                list = self.PM.getAvailableArtists()
                if list == []:
                    QMessageBox.warning(self, "Warning", "Artist not found",QMessageBox.Ok)
                else:
                    dial.setTitle("Artist choice","Choose Artist")
                    dial.setList(list)
                    if dial.exec_():
                        self.PM.resumeSetArtist(dial.listWidget.currentRow())
                        artist_ok = True
            else:
                artist_ok = True
            
            if artist_ok:
                    res = self.PM.setTitle(str(self.titlefield.text()))
                    if res == False:
                        QMessageBox.warning(self, "Warning", "Artist not set !",QMessageBox.Ok)
                    if res is None:
                        list = self.PM.getAvailableTitles()
                        if list == []:
                             QMessageBox.warning(self, "Warning", "Title not found", QMessageBox.Ok)
                        else:
                            dial.setTitle("Title choice","Choose right Title")
                            dial.setList(list)
                            if dial.exec_():
                                self.PM.resumeSetTitle(dial.listWidget.currentRow())
                    if self.PM.lyricsFound():
                        self.listContent.clear()
                        for line in self.PM.getLyrics().split("\n"):
                            self.listContent.addItem(QListWidgetItem(line))
        
    def stopProcessing(self):
        self.stopped = True
    
    def pauseProcessing(self):
        if self.paused:
            self.pauseButton.setText("Pause")
            self.run()
        else:
            self.paused = True
            self.pause_clicked = True
            self.pauseButton.setText("Continue")
            self.backItem = self.currentItem
    
    def showTags(self):
        dial = showTagDialog()
        file = File(self.filename)
        tags = file.tags
        try:
            os.remove(".temp.jpg")
        except:
            pass
        if tags.has_key("APIC:"):
            with open('.temp.jpg', 'wb') as img:
                img.write(tags['APIC:'].data)
        dial.setInfos(tags)
        dial.exec_()
        try:
            os.remove(".temp.jpg")
        except:
            pass
    
    def about(self):
        QMessageBox.about(self,"About LyricsTagger",
                """<b>LyricsTagger</b> v {0}
                <p>Copyright &copy; 2008 Qtrac Ltd. 
                All rights reserved.
                <p>This application can be used to tag
                lyrics for multiples mp3 files.
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR,
                platform.system()))
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(561, 557)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.searchBox = QtGui.QGroupBox(self.centralwidget)
        self.searchBox.setObjectName(_fromUtf8("searchBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.searchBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.searchBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        self.artistfield = QtGui.QLineEdit(self.searchBox)
        self.artistfield.setObjectName(_fromUtf8("artist"))
        self.horizontalLayout_3.addWidget(self.artistfield)
        self.label_3 = QtGui.QLabel(self.searchBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.titlefield = QtGui.QLineEdit(self.searchBox)
        self.titlefield.setObjectName(_fromUtf8("title"))
        self.horizontalLayout_3.addWidget(self.titlefield)
        self.search = QtGui.QPushButton(self.searchBox)
        self.search.setObjectName(_fromUtf8("search"))
        self.horizontalLayout_3.addWidget(self.search)
        self.verticalLayout_2.addWidget(self.searchBox)
        self.pathBox = QtGui.QGroupBox(self.centralwidget)
        self.pathBox.setObjectName(_fromUtf8("pathBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.pathBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_5 = QtGui.QLabel(self.pathBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_5.addWidget(self.label_5)
        self.lineEdit = QtGui.QLineEdit(self.pathBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout_5.addWidget(self.lineEdit)
        self.toolButton = QtGui.QToolButton(self.pathBox)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout_5.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(self.pathBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.fileSelectEdit = QtGui.QLineEdit(self.pathBox)
        self.fileSelectEdit.setObjectName(_fromUtf8("fileSelectEdit"))
        self.horizontalLayout_4.addWidget(self.fileSelectEdit)
        self.chooseFile = QtGui.QToolButton(self.pathBox)
        self.chooseFile.setObjectName(_fromUtf8("chooseFile"))
        self.horizontalLayout_4.addWidget(self.chooseFile)
        self.showTag = QtGui.QPushButton(self.pathBox)
        self.showTag.setObjectName(_fromUtf8("showTag"))
        self.horizontalLayout_4.addWidget(self.showTag)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addWidget(self.pathBox)
        
        self.optionBox = QtGui.QGroupBox(self.centralwidget)
        self.optionBox.setObjectName(_fromUtf8("optionBox"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.optionBox)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.checkVerbose = QtGui.QCheckBox(self.optionBox)
        self.checkVerbose.setObjectName(_fromUtf8("checkVerbose"))
        self.verticalLayout_5.addWidget(self.checkVerbose)
        self.checkRecursive = QtGui.QCheckBox(self.optionBox)
        self.checkRecursive.setObjectName(_fromUtf8("checkRecursive"))
        self.verticalLayout_5.addWidget(self.checkRecursive)
        self.checkOverride = QtGui.QCheckBox(self.optionBox)
        self.checkOverride.setObjectName(_fromUtf8("checkOverride"))
        self.verticalLayout_5.addWidget(self.checkOverride)
        self.checkID3 = QtGui.QCheckBox(self.optionBox)
        self.checkID3.setObjectName(_fromUtf8("checkID3"))
        self.verticalLayout_5.addWidget(self.checkID3)
        
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.horlayprox = QtGui.QHBoxLayout(self.optionBox)
        self.horlayprox.setObjectName(_fromUtf8("horlayprox"))
        self.label_prox = QtGui.QLabel(self.optionBox)
        self.label_prox.setObjectName(_fromUtf8("label_prox"))
        self.label_prox.setText("Proxy: ")
        self.horlayprox.addWidget(self.label_prox)
        self.proxyEdit = QtGui.QLineEdit(self.optionBox)
        self.proxyEdit.setObjectName(_fromUtf8("proxyEdit"))
        self.horlayprox.addWidget(self.proxyEdit)
        self.label_prox_ex = QtGui.QLabel(self.optionBox)
        self.label_prox_ex.setObjectName(_fromUtf8("label_prox_ex"))
        self.label_prox_ex.setText("(ex: http://127.0.0.1:8118)")
        self.label_prox_ex.setEnabled(False)
        self.horlayprox.addWidget(self.label_prox_ex)
        self.verticalLayout_5.addLayout(self.horlayprox)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.verticalLayout_2.addWidget(self.optionBox)
        
        self.buttonsBox = QtGui.QVBoxLayout()
        self.buttonsBox.setObjectName(_fromUtf8("buttonsBox"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pauseButton = QtGui.QPushButton(self.centralwidget)
        self.pauseButton.setObjectName(_fromUtf8("pauseButton"))
        self.horizontalLayout.addWidget(self.pauseButton)
        self.goButton = QtGui.QPushButton(self.centralwidget)
        self.goButton.setObjectName(_fromUtf8("goButton"))
        self.horizontalLayout.addWidget(self.goButton)
        self.stopButton = QtGui.QPushButton(self.centralwidget)
        self.stopButton.setObjectName(_fromUtf8("stopButton"))
        self.horizontalLayout.addWidget(self.stopButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonsBox.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.buttonsBox)
        self.progressBox = QtGui.QHBoxLayout()
        self.progressBox.setObjectName(_fromUtf8("progressBox"))
        self.labelprogressBar = QtGui.QLabel(self.centralwidget)
        self.labelprogressBar.setObjectName(_fromUtf8("labelprogressBar"))
        self.progressBox.addWidget(self.labelprogressBar)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.progressBox.addWidget(self.progressBar)
        self.verticalLayout_2.addLayout(self.progressBox)
        self.listContent = QtGui.QListWidget(self.centralwidget)
        self.listContent.setObjectName(_fromUtf8("listContent"))
        self.verticalLayout_2.addWidget(self.listContent)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 561, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_File = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/newf.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpen_File.setIcon(icon1)
        self.actionOpen_File.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.actionOpen_File.setObjectName(_fromUtf8("actionOpen_File"))
        self.actionOpen_Directory = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/newd.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpen_Directory.setIcon(icon2)
        self.actionOpen_Directory.setObjectName(_fromUtf8("actionOpen_Directory"))
        self.actionExit = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionExit.setIcon(icon3)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/help.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setIcon(icon4)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.actionOpen_Directory)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.label_2.setBuddy(self.artistfield)
        self.label_3.setBuddy(self.titlefield)
        self.label_4.setBuddy(self.fileSelectEdit)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.artistfield, self.titlefield)
        MainWindow.setTabOrder(self.titlefield, self.search)
        MainWindow.setTabOrder(self.search, self.checkVerbose)
        MainWindow.setTabOrder(self.checkVerbose, self.checkRecursive)
        MainWindow.setTabOrder(self.checkRecursive, self.checkOverride)
        MainWindow.setTabOrder(self.checkOverride, self.checkID3)
        MainWindow.setTabOrder(self.checkID3, self.pauseButton)
        MainWindow.setTabOrder(self.pauseButton, self.goButton)
        MainWindow.setTabOrder(self.goButton, self.stopButton)
        MainWindow.setTabOrder(self.stopButton, self.listContent)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.searchBox.setTitle(QtGui.QApplication.translate("MainWindow", "Simple Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Artist:", None, QtGui.QApplication.UnicodeUTF8))
        self.artistfield.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Enter artist name</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.artistfield.setStatusTip(QtGui.QApplication.translate("MainWindow", "Enter artist name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.titlefield.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Enter song title</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.titlefield.setStatusTip(QtGui.QApplication.translate("MainWindow", "Enter song title", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setToolTip(QtGui.QApplication.translate("MainWindow", "Launch research", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setStatusTip(QtGui.QApplication.translate("MainWindow", "Launch research on ParolesMania", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setWhatsThis(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Launch search</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.pathBox.setTitle(QtGui.QApplication.translate("MainWindow", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Select a directory:", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a directory to lookup", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setStatusTip(QtGui.QApplication.translate("MainWindow", "Select a directory to lookup", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "Select a file:", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSelectEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>MP3 files to Tag</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSelectEdit.setStatusTip(QtGui.QApplication.translate("MainWindow", "MP3 files to Tag", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseFile.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.showTag.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Show current tags</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.showTag.setStatusTip(QtGui.QApplication.translate("MainWindow", "Show current tags", None, QtGui.QApplication.UnicodeUTF8))
        self.showTag.setText(QtGui.QApplication.translate("MainWindow", "Show Tag", None, QtGui.QApplication.UnicodeUTF8))
        self.optionBox.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.checkVerbose.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Verbose output</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkVerbose.setText(QtGui.QApplication.translate("MainWindow", "Verbose", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRecursive.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Search MP3 files in subdirectories</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRecursive.setText(QtGui.QApplication.translate("MainWindow", "Recursive directory search", None, QtGui.QApplication.UnicodeUTF8))
        self.checkOverride.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Replace existing lyrics if they are found on internet</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkOverride.setText(QtGui.QApplication.translate("MainWindow", "Override existing lyrics", None, QtGui.QApplication.UnicodeUTF8))
        self.checkID3.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Save tags in IDv3.2.4 (Windows Media Player does not support this version yet)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkID3.setText(QtGui.QApplication.translate("MainWindow", "Save in IDv3.2.3 instead of 3.2.4 (incompatible with Windows Media Player)", None, QtGui.QApplication.UnicodeUTF8))
        self.pauseButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Pause the tagging</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pauseButton.setText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.goButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Start Lyrics search and tag</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.goButton.setText(QtGui.QApplication.translate("MainWindow", "Go !", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head/><body><p>Stop tagging</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("MainWindow", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.labelprogressBar.setText(QtGui.QApplication.translate("MainWindow", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_File.setText(QtGui.QApplication.translate("MainWindow", "Open File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_File.setStatusTip(QtGui.QApplication.translate("MainWindow", "Open File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_File.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_Directory.setText(QtGui.QApplication.translate("MainWindow", "Open Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_Directory.setStatusTip(QtGui.QApplication.translate("MainWindow", "Open Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_Directory.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+D", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setStatusTip(QtGui.QApplication.translate("MainWindow", "Exit LyricsTagger", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setStatusTip(QtGui.QApplication.translate("MainWindow", "About LyricsTagger", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+H", None, QtGui.QApplication.UnicodeUTF8))

    
    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setApplicationName("LyricsTagger")
    win = MainWindow()
    win.show()
    app.exec_()