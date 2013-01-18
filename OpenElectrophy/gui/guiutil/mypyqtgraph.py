# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from .qt import *

import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from pyqtgraph.parametertree import parameterTypes as types

import numpy as np


def get_dict_from_group_param(param, cascade = False):
    assert param.type() == 'group'
    d = {}
    for p in param.children():
        if p.type() == 'group':
            if cascade:
                d[p.name()] = get_dict_from_group_param(p, cascade = True)
            continue
        else:
            d[p.name()] = p.value()
    return d
get_dict = to_dict = get_dict_from_group_param


def set_dict_to_param_group(param, d, cascade = False):
    assert param.type() == 'group'
    for k, v in d.items():
        if type(v) == dict:
            if cascade:
                set_dict_to_param_group(param.param(k), v, cascade = True)
        else:
            param[k] = v
set_dict = set_dict_to_param_group


##Range
class RangeWidget(QWidget):
    sigChanged = pyqtSignal()
    def __init__(self, parent = None, 
                        value = [-1., 1],
                        orientation  = Qt.Vertical,
                        limits = [-np.inf, np.inf],
                        ):
        QWidget.__init__(self, parent)
        self._val = None
        if orientation == Qt.Horizontal:
            mainlayout = QHBoxLayout()
        else:
            mainlayout = QVBoxLayout()
        
        self.setLayout(mainlayout)
        self.spins = [ QDoubleSpinBox(), QDoubleSpinBox()]
        for s in self.spins:
            mainlayout.addWidget(s)
            s.valueChanged.connect(self.spinChanged)
            s.setMaximum(limits[1])
            s.setMinimum(limits[0])
        self.setValue(value)
        
    def spinChanged(self, val):
        self._val = [ spin.value() for spin in self.spins[::-1] ]
        self.sigChanged.emit()
    
    def value(self):
        return self._val
        
    def setValue(self, val):
        self._val = val
        for spin, v in zip(self.spins[::-1], val):
            spin.valueChanged.disconnect(self.spinChanged)
            spin.setValue(v)
            spin.valueChanged.connect(self.spinChanged)
    
    def updateDisplayLabel(self, value=None):
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






class SpinAndSliderWidget(QWidget):
    """this combinate a spin box and a slider in log scale"""
    sigChanged = pyqtSignal()
    def __init__(self, parent = None,
                            value = 1.,
                            limits = [0.001, 1000],
                            orientation  = Qt.Horizontal,
                            ):
        QWidget.__init__(self, parent)

        self._val = None
        self.limits = limits

        if orientation == Qt.Horizontal:
            self.mainlayout = QHBoxLayout()
        else:
            self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.spinbox = QDoubleSpinBox(decimals = 4, singleStep = .1,
                                                        minimum = self.limits[0], maximum = self.limits[1])
        self.mainlayout.addWidget(self.spinbox)
        self.slider = QSlider(Qt.Horizontal, minimum =0, maximum = 100)
        self.mainlayout.addWidget(self.slider)
        self.slider.setMinimumWidth(50)
        
        self.spinbox.valueChanged.connect(self.spinbox_changed)
        self.slider.valueChanged.connect(self.slider_changed)
        self.setValue(value)
 
    def value(self):
        return self._val
    
    def setValue(self, val):
        self._val = val
        self.spinbox.valueChanged.disconnect(self.spinbox_changed)
        self.spinbox.setValue(val)
        self.spinbox.valueChanged.connect(self.spinbox_changed)
        self.slider.valueChanged.disconnect(self.slider_changed)
        self.slider.setValue(self.to_log(val))
        self.slider.valueChanged.connect(self.slider_changed)
    
    def to_log(self, val):
        min, max = self.limits
        return int( (np.log10(val)-np.log10(min))/(np.log10(max) - np.log10(min) )*100 )
    
    def from_log(self, val):
        min, max = self.limits
        return 10**((val/100.)*(np.log10(max) - np.log10(min) )+np.log10(min))
 
    def slider_changed(self, val):
        self._val = self.from_log(val)
        self.spinbox.valueChanged.disconnect(self.spinbox_changed)
        self.spinbox.setValue(self._val)
        self.spinbox.valueChanged.connect(self.spinbox_changed)
        self.sigChanged.emit()
    
    def spinbox_changed(self, val):
        self._val = val
        self.slider.valueChanged.disconnect(self.slider_changed)
        self.slider.setValue(self.to_log(self._val))
        self.slider.valueChanged.connect(self.slider_changed)
        self.sigChanged.emit()

    def updateDisplayLabel(self, value=None):
        if value is None:
            value = self.param.value()
        opts = self.param.opts
        if value is None:
            text = u''
        else:
            text = u'{}'.format(self._val)
        self.displayLabel.setText(text)


class LogFloatParameterItem(types.WidgetParameterItem):
    sigChanged = pyqtSignal
    def __init__(self, param, depth):
        types.WidgetParameterItem.__init__(self, param, depth)
    def makeWidget(self):
        w = SpinAndSliderWidget()
        return w

class LogFloatParameter(Parameter):
    itemClass = LogFloatParameterItem
    sigActivated = pyqtSignal(object)
    def activate(self):
        self.sigActivated.emit(self)
        self.emitStateChanged('activated', None)

registerParameterType('logfloat', LogFloatParameter, override=True)



