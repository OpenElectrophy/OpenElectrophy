# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from guidata.dataset.datatypes import DataSet 
from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox, DataSetEditLayout
from guidata.dataset.dataitems import (FloatItem, IntItem, BoolItem, ChoiceItem,
                             MultipleChoiceItem, ImageChoiceItem, FilesOpenItem,
                             StringItem, TextItem, ColorItem, FileSaveItem,
                             DateTimeItem,
                             FileOpenItem, DirectoryItem, FloatArrayItem)
from guidata.dataset.qtitemwidgets import DataSetWidget

from collections import OrderedDict



from guidata.dataset.qtitemwidgets import LineEditWidget


class PasswordItem(StringItem):
    pass

class PasswordLineEditWidget(LineEditWidget):
    def __init__(self, *args, **kargs):
        super(PasswordLineEditWidget, self).__init__(*args, **kargs)
        self.edit.setEchoMode(QLineEdit.Password)
DataSetEditLayout.register(PasswordItem, PasswordLineEditWidget)    



class ParamWidget(QWidget):
    def __init__(self, dataset, title = '', settings = None, settingskey = None, parent = None):
        super(ParamWidget, self).__init__(parent = parent)
        
        self.settings = settings
        self.settingskey = settingskey
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        
        if self.settings is not None and self.settingskey is not None:
            stored_list = self.settings.getValueOrDefault('storedParameters/'+self.settingskey, [ ])

            h = QHBoxLayout()
            self.mainLayout.addLayout(h)
            h.addStretch(0)
            self.comboParam = QComboBox()
            h.addWidget(self.comboParam)
            
            self.refreshCombo()
            self.comboParam.currentIndexChanged.connect(self.comboParamChanged)

            buttonSave = QPushButton(QIcon(':/list-add.png') ,'')
            buttonSave.setMaximumSize(25,25)
            h.addWidget(buttonSave)
            buttonSave.clicked.connect(self.saveNewParam)
            buttonDel = QPushButton(QIcon(':/list-remove.png') ,'')
            buttonDel.setMaximumSize(25,25)
            h.addWidget(buttonDel)
            buttonDel.clicked.connect(self.delSavedParam)
        
        self.params = DataSetEditGroupBox(title,dataset, show_button = False)
        self.mainLayout.addWidget( self.params )
        
        self.default_dict = self.to_dict()
        

    def to_dict(self):
        self.params.set()
        ds = self.params.dataset
        d = OrderedDict()
        for item in ds._items:
            if type(item) is ChoiceItem:
                val = None
                ind = getattr(ds,  item._name)
                choices = item.get_prop_value("data", item, "choices")
                for choice in choices:
                    if choice[0] == ind:
                        val = choice[1]
            else:
                val = getattr(ds,  item._name)
            d[item._name] = val
        return d
        
    def update(self, d):
        ds = self.params.dataset
        for item in ds._items:
            if item._name in d:
                if type(item) is ChoiceItem:
                    choices = item.get_prop_value("data", item, "choices")
                    choices = [ c[1] for c in choices ]
                    ind = choices.index(d[item._name])
                    setattr(ds,  item._name, ind)
                else:
                    setattr(ds,  item._name, d[item._name])
        self.params.get()
    
    def reset(self):
        self.update(self.default_dict)
    
    def refreshCombo(self):
        stored_list = self.settings['storedParameters/'+self.settingskey]
        self.comboParam.clear()
        list_name = [ l[0] for l in stored_list ]
        self.comboParam.addItems(['Default' , ]+list_name  )
        
    
    def comboParamChanged(self, pos) :
        if pos <= 0 :
            self.reset()
        else :
            stored_list = self.settings['storedParameters/'+self.settingskey]
            self.update(stored_list[pos-1][1])
    
    def saveNewParam( self ) :
        class Parameters(DataSet):
            name = StringItem('name', default = '')
        dia = ParamDialog(Parameters, title = 'key')
        ok = dia.exec_()
        if  ok !=  QDialog.Accepted: return
        
        name = dia.to_dict()['name']
        stored_list = self.settings['storedParameters/'+self.settingskey]
        stored_list += [ [ name , self.to_dict() ] ]
        self.settings['storedParameters/'+self.settingskey] = stored_list

        self.refreshCombo()
        self.comboParam.setCurrentIndex(len(stored_list))

    def delSavedParam( self) :
        pos = self.comboParam.currentIndex()
        if pos == 0: return

        stored_list = self.settings['storedParameters/'+self.settingskey]
        del stored_list[pos-1]
        self.settings['storedParameters/'+self.settingskey] = stored_list
            
        self.refreshCombo()
        self.comboParam.setCurrentIndex(0)



class ParamDialog(QDialog):
    def __init__(self,   dataset, title = '', settings = None, settingskey = None, parent = None):
        super(ParamDialog, self).__init__(parent = parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        self.param_widget = ParamWidget( dataset, title = '', settings = None, settingskey = None,)
        mainLayout.addWidget(self.param_widget)
        h = QHBoxLayout()
        self.buttonOK = QPushButton(QIcon(':/dialog-ok-apply.png') ,'OK')
        h.addWidget(self.buttonOK)
        self.buttonOK.clicked.connect(self.accept)
        mainLayout.addLayout(h)

    def update(self, d):
        self.param_widget.update(d)

    def to_dict(self):
        return self.param_widget.to_dict()


