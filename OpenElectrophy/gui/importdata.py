# -*- coding: utf-8 -*-
"""
widget for importing data into a db
    
"""


from .qt import *

import distutils.version

from .guiutil.icons import icons
from .guiutil.myguidata import *

import os


from collections import OrderedDict

import datetime

import time


from ..core.base import OEBase

from ..io import iolist

import neo
from neo.io.tools import populate_RecordingChannel




import sqlalchemy


# constructing possibles input and output
read_io_list = OrderedDict()
for io in iolist:
    if io.name is not None:
        read_io_list[io.name] = io
    else:
        read_io_list[io.__name__] = io


class ImportData(QDialog) :
    """
    """
    def __init__(self  , parent = None ,
                            dbinfo = None,
                            settings = None,
                            use_thread = True,
                            read_io_list = read_io_list):
        super(ImportData, self).__init__(parent)
        self.settings = settings
        self.dbinfo = dbinfo
        self.use_thread = use_thread
        self.read_io_list = read_io_list
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        
        self.comboNeoIO = QComboBox()
        self.comboNeoIO.addItems(self.read_io_list.keys())
        self.mainLayout.addWidget(self.comboNeoIO)
        self.comboNeoIO.currentIndexChanged .connect(self.changeIO)

        
        self.tab = QTabWidget()
        self.mainLayout.addWidget( self.tab )
        
        
        # Files tab
        w =  QWidget()
        v = QVBoxLayout()
        w.setLayout(v)
        self.tab.addTab(w, 'Files')
        self.butAdd = QPushButton(QIcon(':/list-add.png') , 'Add files')
        v.addWidget(self.butAdd)
        self.connect(self.butAdd , SIGNAL('clicked()') , self.addFiles)
        self.listFiles = QListWidget()
        v.addWidget(self.listFiles)
        
        # Options input tab
        self.widgetInput =  QWidget()
        v = QVBoxLayout()
        self.widgetInput.setLayout(v)
        self.tab.addTab(self.widgetInput, 'IO specifics params')
        
        # General options
        class Parameters(DataSet):
            #~ parentnum = ChoiceItem('Wich parent to change', ['1','2','3'])
            #~ anint = IntItem('an integer', 5)
            #~ name = StringItem('the name', default = 'sam')
            #~ description = TextItem('description', default ='multiline')
            populate_recordingchannel =BoolItem('If neo.io reader do not support RecordingChannel do create them', default = True)
            
        self.generalOptions = ParamWidget(Parameters, title = None)
        self.tab.addTab(self.generalOptions, 'General options')
        
        
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Open| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.startImporting)
        buttonBox.rejected.connect(self.reject)
        
        # initiate options tab
        self.inputOptions = None
        self.changeIO( 0 )
        
        self.threadimport = None

    
    def changeIO(self, num):
        self.name = self.read_io_list.keys()[num]
        self.ioclass = self.read_io_list[self.name]
        
        if self.inputOptions is not None :
            self.inputOptions.hide()
            self.widgetInput.layout().removeWidget( self.inputOptions )
        self.inputOptions = None
        
        main_object = self.ioclass.readable_objects[0]
        if main_object in self.ioclass.read_params:
            oldparams = self.ioclass.read_params[main_object]
            if oldparams is not None and oldparams!= [ ]:
                Parameters = old_params_to_guidata(oldparams)
                self.inputOptions = ParamWidget( Parameters )
                self.widgetInput.layout().addWidget( self.inputOptions )
        
        if self.ioclass.mode =='file':
            self.butAdd.setEnabled(True)
            self.butAdd.setText('Add files')
        elif self.ioclass.mode =='dir':
            self.butAdd.setEnabled(True)
            self.butAdd.setText('Add dir')
        elif self.ioclass.mode =='database':
            self.butAdd.setEnabled(False)
        elif self.ioclass.mode =='fake':
            self.butAdd.setEnabled(False)
        else:
            self.butAdd.setEnabled(False)
            
        self.listFiles.clear()

    def addFiles(self):        
        fd = QFileDialog(acceptMode = QFileDialog.AcceptOpen)
        if self.ioclass.extensions is not None and len(self.ioclass.extensions)>0:
            filter = '{} files ({})'.format(self.name, ', '.join('*.{}'.format(ext) for ext in self.ioclass.extensions))
            #~ filter = '{} files ('.format(self.name)
            #~ for ext in self.ioclass.extensions:
                #~ filter += '*.{}'.format(ext)
            #~ filter += ');;'
            fd.setFilter(filter)
        
        if self.ioclass.mode =='file':
            fd.setFileMode(QFileDialog.ExistingFiles)
        elif self.ioclass.mode =='dir':
            fd.setFileMode(QFileDialog.Directory)
        
        if (fd.exec_()) :
            names = fd.selectedFiles()
            self.listFiles.addItems(names)

    def startImporting(self):
        if self.threadimport is not None:
            return
        
        #~ if self.generalOptions['group_segment'] and :
            #~ bl = Block()
            #~ self.session.add(bl)
            #~ self.session.commit()

        #~ fileType = self.paramTypes['import_type']
        #~ cl = dict_format[fileType]['class']
            
        bl = None
        error_list= [ ]
        
        if self.ioclass.mode =='file' or self.ioclass.mode =='dir':
            names = [ ]
            for i in range(self.listFiles.count()):
                names.append( unicode(self.listFiles.item(i).text()) )
        elif self.ioclass.mode =='database' or self.ioclass.mode =='fake':
            names = [ 'fake' ]
        
        # for outside
        self.names = names
        
        io_kargs = { }
        if self.inputOptions is not None:
            io_kargs = self.inputOptions.to_dict()
        
        options = self.generalOptions.to_dict()
        
        if self.use_thread:
            self.threadimport = QImportThread(self, names, self.ioclass, io_kargs, self.dbinfo, options)
            self.threadimport.finished.connect(self.importFinished)
            self.threadimport.one_file_done.connect(self.promptOneFileDone)
            self.setEnabled(False)
            self.threadimport.start()
        else:
            for name in names:
                read_and_import(name, self.ioclass,io_kargs, self.dbinfo, options)
            self.accept()
    
    
    def promptOneFileDone(self, name):
        print 'OneFileDone', name
    
    def importFinished(self):
        
        if len(self.threadimport.error_list) >0:
            text = "Fail to import :"
            for f in self.threadimport.error_list:
                if f is not None:
                    text+= '    '+f
                else:
                    text = 'nofile'
            QMessageBox.warning(self,u'Fail',text,
                    QMessageBox.Ok , QMessageBox.NoButton)
        self.threadimport = None
        self.setEnabled(True)
        self.listFiles.clear()
        self.accept()
    
    
    

        
class QImportThread(QThread):
    one_file_done = pyqtSignal(unicode)
    
    def __init__(self, parent, names, ioclass, io_kargs, dbinfo, options):
        super(QImportThread, self).__init__(parent)
        self.names = names
        self.ioclass = ioclass
        self.error_list = [ ]
        self.io_kargs = io_kargs
        self.dbinfo = dbinfo
        self.options = options
        
        
    def run(self):
        for i, name in enumerate(self.names):
            print 'runnning', name
            #try :
            if 1:
                read_and_import(name, self.ioclass,self.io_kargs, self.dbinfo, self.options)
            #except:
             #       self.error_list.append(name)
            self.one_file_done.emit('{}'.format(name))




def read_and_import(name, ioclass,io_kargs, dbinfo, options):
    #~ print 'read_and_import', name
    
    if ioclass.mode =='file':
        reader = ioclass(filename = name  )
    elif ioclass.mode =='dir':
        reader = ioclass(dirname = name  )
    elif ioclass.mode =='database':
        reader = ioclass(url = name  )
    elif ioclass.mode =='fake':
        reader = ioclass()
    
    
    if distutils.version.LooseVersion(neo.__version__) < '0.3':
        neo_blocks = [ reader.read(** io_kargs) ]
    else:
        neo_blocks = reader.read(** io_kargs)
        
    for neo_block in neo_blocks:
        if options['populate_recordingchannel'] and neo.RecordingChannelGroup not in reader.supported_objects:
            #~ print 'populate_RecordingChannel'
            populate_RecordingChannel(neo_block, remove_from_annotation = False)
        
        oe_block = OEBase.from_neo(neo_block, dbinfo.mapped_classes, cascade = True)
        oe_block.file_origin = os.path.basename(name)
    
    session = dbinfo.Session()
    dbinfo.Session.add(oe_block)
    session.commit()
