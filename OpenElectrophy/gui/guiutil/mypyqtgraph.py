# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from .qt import *

import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from pyqtgraph.parametertree import parameterTypes as types

import numpy as np


class RangeWidget(QWidget):
    sigChanged = pyqtSignal()
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self._val = None
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)
        self.spins = [ QDoubleSpinBox(), QDoubleSpinBox()]
        for s in self.spins:
            mainlayout.addWidget(s)
            s.valueChanged.connect(self.spinChanged)
            s.setMaximum(np.inf)
            s.setMinimum(-np.inf)
        
    def spinChanged(self, val):
        self._val = [ spin.value() for spin in self.spins[::-1] ]
        self.sigChanged.emit()
    
    def value(self):
        return self._val
        
    def setValue(self, val):
        self._val = val
        for spin, v in zip(self.spins[::-1], val):
            spin.setValue(v)
        
    
    def updateDisplayLabel(self, value=None):
        print 'ici', value, self._val, self.param.value()
        if value is None:
            value = self.param.value()
        opts = self.param.opts
        if value is None:
            text = u''
        else:
            text = u'{} - {}'.format(*self._val)
        self.displayLabel.setText(text)


class RangeParameterItem(types.WidgetParameterItem):
    sigChanged = pyqtSignal
    def __init__(self, param, depth):
        types.WidgetParameterItem.__init__(self, param, depth)
    def makeWidget(self):
        w = RangeWidget()
        return w

class RangeParameter(Parameter):
    itemClass = RangeParameterItem
    sigActivated = pyqtSignal(object)
    
    def activate(self):
        self.sigActivated.emit(self)
        self.emitStateChanged('activated', None)



registerParameterType('range', RangeParameter, override=True)



