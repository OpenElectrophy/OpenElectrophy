# -*- coding: utf-8 -*-
"""
This is the spike sorting window.
Note that spikesorting widgets can be used independently.


"""

from ..qt import *

from .spikesortingwidgets import spikesorting_widget_list
from .toolchain import all_toolchain, ToolChainWidget

from pyqtgraph.dockarea import DockArea, Dock

from collections import OrderedDict

import numpy as np
import time


vt = view_templates = OrderedDict()
vt['Good ensemble'] =  ['UnitList', 'SpikeList', 'FilteredBandSignal', 'FeaturesNDViewer', 'AverageWaveforms', ]
vt['Nothing'] = [ ]
vt['One cell detection'] = [ 'UnitList', 'SpikeList', 'FullBandSignal', 'FilteredBandSignal', 'AllWaveforms', 'AverageWaveforms', ]



class SpikeSortingWindow(QMainWindow):
    db_changed = pyqtSignal()
    def __init__(self, spikesorter = None, settings = None, 
                        session = None, dbinfo = None, parent = None ):
                        
        super(SpikeSortingWindow, self).__init__(parent = parent)
        
        self.spikesorter = spikesorter
        sps = self.spikesorter
        self.session = session
        self.dbinfo = dbinfo
        self.settings = settings
        
        sps.check_display_attributes()
        
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
        
        self.list_actTemplate = [ ]
        for name in view_templates.keys():
            act = QAction(name,but, checkable = True)
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
        
        
        ## Tool chain
        self.toolchain = ToolChainWidget(spikesorter = self.spikesorter ,settings = self.settings )
        
        
        self.toolchain.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.dockToolChain = dock = QDockWidget('Tool Chain',self)
        dock.setObjectName(  'Tool chain' )
        dock.setWidget(self.toolchain)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.toolchain.need_refresh.connect(self.refresh_all)
        #~ self.toolchain.resize(200,200)
        #~ self.toolchain.setFixedWidth(200)
        #~ self.toolchain.setMaximumWidth(300)
        
        ##
        

        
        self.list_actionView = [ ]
        self.list_widget = [ ]
        self.list_dock = [ ]
        for i, W in enumerate(spikesorting_widget_list):
            #~ print i, W
            # Menu
            #~ act = QAction(W.name,but, checkable = True)
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
            
            
            friend = None
            for j in range(i):
                if spikesorting_widget_list[j] in W.tabified_with:
                    friend = self.list_dock[j]
                    break
            if friend is not None:
                self.tabifyDockWidget ( friend, dock)
            else:
                if ' of ' in W.prefered_position:
                    relative_pos = W.prefered_position.split(' ')[0]
                    relative_to = W.prefered_position.split(' ')[2]
                    direction = Qt.Horizontal if relative_pos in ['left', 'right'] else Qt.Vertical
                    if relative_pos == 'above' and relative_to == 'ToolChain':
                        self.splitDockWidget(self.dockToolChain, dock, Qt.Vertical)
                    else:
                        for relative_to_dock in self.list_dock:
                            if relative_to_dock.widget().__class__.__name__ == relative_to:
                                break
                        self.splitDockWidget(relative_to_dock, dock, direction)
                elif W.prefered_position == 'UpperRight':
                    self.addDockWidget(Qt.RightDockWidgetArea, dock)
            
            dock.setVisible(False)
            self.list_dock.append(dock)
            self.list_widget.append(w)
        
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
        but =  QToolButton(toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/color-picker.png' ),
                                            text = u'Clear selection')
        but.clicked.connect(self.clear_selection)
        self.toolbar.addWidget(but)
        
        self.toolbar.addSeparator()
        but =  QToolButton(toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/document-save.png' ),
                                            text = u'Save')
        but.clicked.connect(self.save_to_database)
        self.toolbar.addWidget(but)
        
        
        for dock in self.list_dock:
            dock.visibilityChanged.connect(self.oneDockVisibilityChanged)
        for w in self.list_widget:
            w.spike_clusters_changed.connect(self.on_spike_clusters_changed)
            w.spike_selection_changed.connect(self.on_spike_selection_changed)
            w.spike_subset_changed.connect(self.on_spike_subset_changed)
            w.clusters_activation_changed.connect(self.on_clusters_activation_changed)
            w.clusters_color_changed.connect(self.on_clusters_color_changed)            
        self.changeTemplate(view_templates.keys()[0])
    
    ## Event and refresh
    def refresh_all(self, shuffle = True):
        self.spikesorter.check_display_attributes()
        if shuffle:
            self.refresh_displayed_subset()
        
        for w,dock in zip(self.list_widget, self.list_dock):
            if dock.isVisible():
                t1 = time.time()
                w.refresh()
                t2 = time.time()
                print 'refresh ', w.name, t2-t1

    def on_spike_clusters_changed(self):
        self.spikesorter.refresh_colors(reset = False)
        self.spikesorter.recompute_cluster_center()
        self.spikesorter.selected_spikes[:] = False
        self.refresh_displayed_subset()
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender(): continue
            if dock.isVisible() :#and 'spike_clusters' in w.refresh_on:
                t1 = time.time()
                w.refresh()
                t2 = time.time()
                print 'refresh ', w.name, t2-t1
                
                #~ w.refresh()

    def on_spike_subset_changed(self):
        self.refresh_all( shuffle = False)
    
    def on_clusters_activation_changed(self):
        self.spikesorter.on_clusters_activation_changed()
        #~ self.refresh_all( shuffle = False)
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender():
                continue
            if not dock.isVisible(): continue
            if hasattr(w, 'on_clusters_activation_changed'):
                w.on_clusters_activation_changed()
            else:
                w.refresh()
    
    def on_clusters_color_changed(self):
        self.refresh_all( shuffle = False)
    
    
    def on_spike_selection_changed(self):
        for dock, w in zip(self.list_dock,self.list_widget):
            if w == self.sender():
                continue
            if dock.isVisible() and hasattr(w, 'on_spike_selection_changed'):
                w.on_spike_selection_changed()


    def refresh_displayed_subset(self):
        val = self.spinboxSubsetLimit.value()
        if val == 0: val = np.inf
        self.spikesorter.refresh_displayed_subset(displayed_subset_size = val)
    
    
    def clear_selection(self):
        self.spikesorter.selected_spikes[:] = False
        self.on_spike_selection_changed()
    
    
    ## DOCK AND TEMPLATE
    def oneDockChangeToVisible(self, i):
        # is tabified ??
        dock = self.list_dock[i]
        dock.visibilityChanged.disconnect(self.oneDockVisibilityChanged)
        dock.setVisible(True)
        for j, w2 in enumerate(self.list_widget):
            if self.list_dock[j].isVisible() and self.list_widget[j].__class__ in self.list_widget[i].tabified_with:
                self.tabifyDockWidget( self.list_dock[j], self.list_dock[i])

        t1 = time.time()
        self.list_widget[i].refresh()
        t2 = time.time()
        print'refresh oneDockChangeToVisible',  self.list_dock[i].widget().name, t2-t1
        
        dock.visibilityChanged.connect(self.oneDockVisibilityChanged)

    
    def oneDockVisibilityChanged(self):
        dock = self.sender()
        i = self.list_dock.index(dock)
        act = self.list_actionView[i]
        w = self.list_widget[i]
        
        if act.isChecked() and dock.isVisible():
            pass # alredy visible before that call
        elif act.isChecked() and not dock.isVisible():
            act.setChecked(False)
        elif not act.isChecked() and not dock.isVisible():
            pass # should not be possible
        elif not act.isChecked() and  dock.isVisible():
            # become visible
            act.setChecked(True)
            self.oneDockChangeToVisible(i)
            
    def selectPlotChanged(self):
        act = self.sender()
        i = self.list_actionView.index(act)
        if act.isChecked():
            self.oneDockChangeToVisible(i)
        else:
            self.list_dock[i].setVisible(False)
        #~ self.list_dock[i].setVisible(act.isChecked())
        
    def templateChanged(self):
        act = self.sender()
        i = self.list_actTemplate.index(act)
        for a in self.list_actTemplate: a.setChecked(False)
        act.setChecked(True)
        self.changeTemplate(view_templates.keys()[i])

    def changeTemplate(self, name = None):
        for i, w in enumerate(self.list_widget):
            dock = self.list_dock[i]
            if w.__class__.__name__ in view_templates[name]:
                dock.setVisible(True)
            else:
                dock.setVisible(False)

    ## Save 
    def save_to_database(self):
        if self.session is None:
            return
        msg = u'Units and SPikeTrain will saved directly in opened database.\n'
        msg += 'Note that old Units and SpikeTrain related to this RecodingChannelGourp will be removed for ever'
        mb = QMessageBox.warning(self,u'Save to database',msg, 
                QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                QMessageBox.NoButton)
        if mb == QMessageBox.Cancel : return
        if self.dbinfo.url =='sqlite://':
            msg = u'You are working in read only neo file. (memory sqlite database).\n'
            msg += u'Export this result to a file before closing OpenElectrophy \n'
            mb = QMessageBox.warning(self,u'Save to database',msg, 
                    QMessageBox.Ok ,QMessageBox.NoButton,
                    QMessageBox.NoButton)
        self.spikesorter.save_in_database(self.session, self.dbinfo)
        self.db_changed.emit()

    def save_to_hdf5(self):
        pass



