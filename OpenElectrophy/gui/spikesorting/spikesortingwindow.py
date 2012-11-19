# -*- coding: utf-8 -*-
"""
This is the spike sorting window.
Note that spikesorting widgets can be used independently.


"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .spikesortingwidgets import spikesorting_widget_list
from .toolchain import *

import numpy as np

# TODO: save result
# TODO: dock template
# TODO: change toolchain

class SpikeSortingWindow(QMainWindow):
    def __init__(self, spikesorter = None, settings = None, parent = None ):
        super(SpikeSortingWindow, self).__init__(parent = parent)
        
        self.spikesorter = spikesorter
        sps = self.spikesorter
        self.settings = settings
        
        
        
        self.setWindowTitle('Spike sorting for RecordingChannelGroup.name={}'.format(sps.rcg.name))
        self.setAnimated(False)
        self.setDockNestingEnabled(True)
        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Menu for view template
        but =  QToolButton( popupMode = QToolButton.InstantPopup,
                                            toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/view-choose.png' ),
                                            text = u'Views template')
        self.toolbar.addWidget(but)
        self.templateNames =[ 'Nothing', 'Good ensemble', 'One cell', 
                            'Manual clustering', 'Detection', 'Before to save', 'Controls']
        self.list_actTemplate = [ ]
        for name in self.templateNames:
            act = QAction(name,but, checkable = True)
            #~ act.setCheckable(True)
            self.list_actTemplate.append(act)
            but.addAction(act)
            act.triggered.connect( self.templateChanged)


        # Menu for selecting view
        #but =  QToolButton( 	popupMode = QToolButton.InstantPopup, toolButtonStyle = Qt.ToolButtonTextBesideIcon)
        but =  QToolButton( popupMode = QToolButton.InstantPopup,
                                            toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/plot.png' ),
                                            text = u'Select displayed plots')
        self.toolbar.addWidget(but)
        
        self.list_actionView = [ ]
        self.list_widget = [ ]
        self.list_dock = [ ]
        for W in spikesorting_widget_list:
            # Menu
            act = QAction(W.name,but, checkable = True)
            self.list_actionView.append(act)
            if hasattr(W, 'icon_name'):
                act.setIcon(QIcon(':/'+W.icon_name))
            but.addAction(act)
            act.triggered.connect( self.selectPlotChanged)
            
            # Widget and dock
            w = W( spikesorter = self.spikesorter ,settings = self.settings )
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            dock = QDockWidget(W.name,self)
            dock.setObjectName(  W.name )
            dock.setWidget(w)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self.list_dock.append(dock)
            self.list_widget.append(w)
            w.spike_clusters_changed.connect(self.on_spike_clusters_changed)
            w.spike_selection_changed.connect(self.on_spike_selection_changed)
            w.spike_subset_changed.connect(self.on_spike_subset_changed)
            dock.visibilityChanged.connect(self.oneDockVisibilityChanged)
        
        self.toolchain = ToolChainWidget(spikesorter = self.spikesorter ,settings = self.settings )
        # TODO: auto guess best mode
        self.toolchain.change_toolchain(FromFullBandSignalToClustered, )
        
        self.toolchain.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        dock = QDockWidget('Tool Chain',self)
        dock.setObjectName(  'Tool chain' )
        dock.setWidget(self.toolchain)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.toolchain.need_refresh.connect(self.refresh_all)
        
        but =  QToolButton( popupMode = QToolButton.InstantPopup,
                                            toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/spikesorting-mode.png' ),
                                            text = u'')
        self.toolbar.addWidget(but)
        
        self.toolbar.addSeparator()
        
        # Random a subset
        but =  QToolButton( toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/view-refresh.png' ),
                                            text = u'Refresh all')
        self.toolbar.addWidget(but)
        but.clicked.connect(self.refresh_all)
        but =  QToolButton(toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/roll.png' ),
                                            text ='Sample subset n=')
        self.toolbar.addWidget(but)
        but.clicked.connect(self.refresh_displayed_subset)
        but.clicked.connect(self.refresh_all)
        self.spinboxSubsetLimit = QSpinBox( minimum = 0, maximum = 1e9, specialValueText = "All",
                                                                            singleStep = 500, value = 5000)
        self.toolbar.addWidget(self.spinboxSubsetLimit)
        
        self.toolbar.addSeparator()
        
        #~ but =  QToolButton(toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            #~ icon = QIcon(':/document-save.png' ),
                                            #~ text = u'Save')
        #~ but.clicked.connect(self.save)
        
        self.changeTemplate(self.templateNames[0])
        self.refresh_all( )


    def refresh_all(self, shuffle = True):
        self.spikesorter.check_display_attributes()
        #~ self.spikesorter.refresh_cluster_names()
        #~ self.spikesorter.refresh_colors()
        if shuffle:
            self.refresh_displayed_subset()
        import time
        for w,dock in zip(self.list_widget, self.list_dock):
            if dock.isVisible():
                t1 = time.time()
                w.refresh()
                t2 = time.time()
                print 'refresh ', w.name, t2-t1

    def on_spike_clusters_changed(self):
        self.spikesorter.refresh_colors()
        self.spikesorter.selected_spikes[:] = False
        self.refresh_displayed_subset()
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender(): continue
            if dock.isVisible() :#and 'spike_clusters' in w.refresh_on:
                w.refresh()

    def on_spike_subset_changed(self):
        self.refresh_all( shuffle = False)
    
    def refresh_displayed_subset(self):
        val = self.spinboxSubsetLimit.value()
        if val == 0: val = np.inf
        self.spikesorter.refresh_displayed_subset(displayed_subset_size = val)

    def on_spike_selection_changed(self):
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender():
                continue
            if dock.isVisible() and hasattr(w, 'on_spike_selection_changed'):
                w.on_spike_selection_changed()

        
    ## DOCK AND TEMPLATE
    def oneDockVisibilityChanged(self):
        dock = self.sender()
        i = self.list_dock.index(dock)
        self.list_actionView[i].setChecked(dock.isVisible())
    

    def selectPlotChanged(self):
        act = self.sender()
        i = self.list_actionView.index(act)
        if act.isChecked():
            # TODO position of dock
            self.list_dock[i].setVisible(True)
            self.list_widget[i].refresh()
        else:
            self.list_dock[i].setVisible(False)
        
        
        
        
    def templateChanged(self):
        act = self.sender()
        i = self.list_actTemplate.index(act)
        for a in self.list_actTemplate: a.setChecked(False)
        act.setChecked(True)
        self.changeTemplate(self.templateNames[i])

    def changeTemplate(self, name = None):
        
        # hide all
        for dock in self.list_dock:
            dock.setVisible(False)
        
        dWidget = dict( [ (w.name, w) for w in self.list_widget] )
        dDock = dict( [ (self.list_widget[i].name, self.list_dock[i]) for i in range(len(self.list_widget)) ]  ) 
        dAct = dict( [ (self.list_widget[i].name, self.list_actionView[i]) for i in range(len(self.list_widget)) ]  ) 
        
        if name == 'Good ensemble':
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Full band signal'] , )
            dDock['Full band signal'].setVisible(True)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Full band signal'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Cross-correlogram'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Cross-correlogram'], Qt.Horizontal)
            self.tabifyDockWidget ( dDock['Full band signal'], dDock['Filtered signal'])
            dDock['Filtered signal'].setVisible(True)

            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Features NDViewer'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Features NDViewer'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)

        elif name == 'Nothing':
            pass
        
        elif name == 'One cell':
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Full band signal'] , )
            dDock['Full band signal'].setVisible(True)
            self.splitDockWidget(dDock['Full band signal'], dDock['Filtered signal'], Qt.Vertical)
            dDock['Filtered signal'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Spike list'] , )
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Spike list'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Average waveforms'], Qt.Horizontal)
            dDock['Average waveforms'].setVisible(True)
                        
            
        elif name == 'Manual clustering':
            
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Waveforms'] , )
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Average waveforms'], Qt.Horizontal)
            dDock['Average waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Average waveforms'], dDock['Features Parallel Plot'], Qt.Horizontal)
            dDock['Features Parallel Plot'].setVisible(True)
            self.splitDockWidget(dDock['Features Parallel Plot'], dDock['Features 3D'], Qt.Horizontal)
            dDock['Features 3D'].setVisible(True)
            self.splitDockWidget(dDock['Features 3D'], dDock['Features Wilson Plot'], Qt.Horizontal)
            dDock['Features Wilson Plot'].setVisible(True)
            
            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Features NDViewer'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Features NDViewer'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)
            
        elif name == 'Detection':
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Filtered signal'] , )
            dDock['Filtered signal'].setVisible(True)
            self.splitDockWidget(dDock['Filtered signal'], dDock['Average waveforms'], Qt.Vertical)
            dDock['Average waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Average waveforms'], dDock['Waveforms'], Qt.Horizontal)
            dDock['Waveforms'].setVisible(True)
            self.tabifyDockWidget ( dDock['Filtered signal'], dDock['Full band signal'])
            dDock['Full band signal'].setVisible(True)
            self.splitDockWidget(dDock['Waveforms'], dDock['Signal statistics'], Qt.Horizontal)
            dDock['Signal statistics'].setVisible(True)


            
        elif name == 'Before to save':
            dDock['Unit list'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Unit list'] , )
            dDock['Summary'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Summary'], Qt.Horizontal)
            dDock['Spike list'].setVisible(True)
            self.splitDockWidget(dDock['Unit list'], dDock['Spike list'], Qt.Vertical)
            dDock['Waveforms'].setVisible(True)
            self.splitDockWidget(dDock['Summary'], dDock['Waveforms'], Qt.Vertical)

        elif name == 'Controls':
            self.addDockWidget(Qt.TopDockWidgetArea, dDock['Cross-correlogram'] , )
            dDock['Cross-correlogram'].setVisible(True)
            self.addDockWidget(Qt.RightDockWidgetArea, dDock['Interval Inter Spike'] , )
            dDock['Interval Inter Spike'].setVisible(True)            
        
        
        self.refresh_all()
        

        



