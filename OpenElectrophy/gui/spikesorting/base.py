# -*- coding: utf-8 -*-
"""
This is the base for spike sorting widgets.

A SpikeSortingWidget is used:
    * in the main SpikeSortingWindow
    * individually with .show() method in interactive mode.

API for SpikeSortingWidget:
    * SpikeSorter for entry
    * a refresh method
    * a list of variable changes (state in spikesorter) that could trigger a refresh.
    * a name
    * setSelection method optional
    * 3 signals:
            1. spike_labels_changed = pyqtSignal()
            2. spike_selection_changed = pyqtSignal()
            3. spike_subset_changed = pyqtSignal()


"""


from ..qt import *

import quantities as pq
import numpy as np

import neo

from ..guiutil.myguidata import *
from ..guiutil.mymatplotlib import *


class SpikeSortingWidgetBase(QWidget):
    spike_clusters_changed = pyqtSignal()
    spike_selection_changed = pyqtSignal()
    spike_subset_changed = pyqtSignal()
    clusters_activation_changed = pyqtSignal()
    clusters_color_changed = pyqtSignal()
    
    plot_options_changed = pyqtSignal()
    
    def __init__(self, parent = None, spikesorter = None, settings = None):
        super(SpikeSortingWidgetBase, self).__init__(parent =parent)
        self.spikesorter = spikesorter
        self.settings = settings
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        if hasattr(self, 'plot_dataset'):
            h = QHBoxLayout()
            self.mainLayout.addLayout(h)
            but = QPushButton(QIcon(':/configure.png'), '', self)
            h.addWidget(but)
            but.clicked.connect(self.changePlotOptions)
            h.addStretch()
            self.plot_parameters = ParamWidget(self.plot_dataset).to_dict()
            
    def changePlotOptions(self):
        dia = ParamDialog(self.plot_dataset, settings = self.settings, settingskey = '/spike_sorting_plot/'+self.__class__.__name__)
        dia.update(self.plot_parameters)
        if dia.exec_():
            self.plot_parameters = dia.to_dict()
            self.plot_options_changed.emit()
        self.refresh()
        




class ThreadRefresh(QThread):
    def __init__(self, parent = None,widgetToRefresh = None):
        QThread.__init__(self)
        self.widgetToRefresh = widgetToRefresh
    def run(self):
        self.widgetToRefresh.refresh_background()



