# -*- coding: utf-8 -*-
"""
Widget for managing pyqtgraph for several channel.

"""

from ..qt import *

from ..guiutil import *
import pyqtgraph as pg




class MultiChannelParam(QWidget):
    def __init__(self, parent = None, all_params= None, param_by_channel = None):
        super(MultiChannelParam, self).__init__(parent)
        
        self.all_params = all_params
        self.param_by_channel = param_by_channel
        
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)
        
        self.paramSelection = pg.parametertree.Parameter.create( name='Multiple change for selection', type='group',
                                                    children = param_by_channel, tip= u'This options apply on selection AnalogSignal on left list')
        self.tree = pg.parametertree.ParameterTree()
        self.tree.header().hide()
        self.tree.setParameters(self.paramSelection, showTop=True)
        mainlayout.addWidget(self.tree,1)
        self.paramSelection.sigTreeStateChanged.connect(self.paramChanged)
        
        
        mainlayout.addWidget(QLabel(u'Select one or several channel\nto change parameters'))
        
        names = [ p.name() for p in self.all_params ]
        self.list = QListWidget()
        mainlayout.addWidget(self.list, 2)
        self.list.addItems(names)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.itemSelectionChanged.connect(self.selectionChanged)
        
        for i in range(len(names)):
            self.list.item(i).setSelected(True)
        
    
    def paramChanged(self, param, changes):
        for p, change, data in changes:
            for row in range(self.list.count()):
                item = self.list.item(row)
                if item.isSelected():
                    self.all_params.children()[row].param(p.name()).setValue(data)
    
    def selectionChanged(self):
        indexes = self.list.selectedIndexes()
        if len(indexes)==0: return
        r = indexes[0].row()
        self.paramSelection.sigTreeStateChanged.disconnect(self.paramChanged)
        for p in self.all_params.children()[r].children():
            self.paramSelection.param(p.name()).setValue(p.value())
        self.paramSelection.sigTreeStateChanged.connect(self.paramChanged)
    
    def selectedRows(self):
        return [ ind.row() for ind in self.list.selectedIndexes()]
        
    def selected(self):
        selected =  np.zeros(len(self.all_params.children()), dtype = bool)
        selected[self.selectedRows()] = True
        return selected

