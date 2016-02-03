# -*- coding: utf-8 -*-
"""

"""


# TODO integrate quantities in pyqtgraph and deal directly with units


from ..qt import *

import numpy as np
import quantities as pq

import pyqtgraph as pg

from ..guiutil import *

from ...timefrequency import LineDetector, PlotLineDetector



#~ from sqlalchemy import and_, or_



class OscillationDetection(QWidget) :
    db_changed = pyqtSignal()
    def __init__(self  , parent = None ,
                            analogsignal =None,
                            settings = None,
                            session = None,
                            mapped_classes = None,
                            ):
        QWidget.__init__(self, parent)
        
        self.ana = self.analogsignal = analogsignal
        self.neoana = self.ana.to_neo(cascade = False)
        self.settings = settings
        self.session = session
        self.mapped_classes = mapped_classes
        
        self.setWindowTitle(u'OpenElectrophy Edit oscillation for {}'.format(self.ana.id) )
        self.setWindowIcon(QIcon(':/oscillation.png'))
        
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        h = QHBoxLayout()
        self.mainLayout.addLayout(h)
        
        self.tfr_params = Parameter.create(name='Scalogram', type='group',
                    children = [
                                        {'name': 'f_start', 'type': 'float', 'value': 5.},
                                        {'name': 'f_stop', 'type': 'float', 'value': 90.},
                                        {'name': 'deltafreq', 'type': 'float', 'value': 1.},
                                        {'name': 't_start', 'type': 'float', 'value': -np.inf},
                                        {'name': 't_stop', 'type': 'float', 'value': np.inf},
                                        {'name': 'sampling_rate', 'type': 'float', 'value': None},
                                        {'name': 'f0', 'type': 'float', 'value': 2.5},
                                        {'name': 'normalisation', 'type': 'float', 'value': 0.},
                                        {'name': 'optimize_fft', 'type': 'bool', 'value': False},
                                        {'name': 'Compute scalogram', 'type': 'action'},
                                        
                                        ]
                    )
        self.tfr_params.param('Compute scalogram').sigActivated.connect(self.computeScalogram)
        
        self.detection_zone_params = Parameter.create(name='Detection zone', type='group',
                    children = [ {'name': 'time_limits', 'type': 'range', 'value': [0.,np.inf]},
                                            {'name': 'freq_limits', 'type': 'range', 'value': [5.,90.]},
                                            {'name': 'Redraw filtered signal', 'type': 'action'},
                                        ]
                                        )
        self.detection_zone_params.param('Redraw filtered signal').sigActivated.connect(self.redrawSignal)
        
        self.threshold_params = Parameter.create(name='Threshold', type='group',
                    children = [{'name': 'manual_threshold', 'type': 'bool', 'value':True},
                                        {'name': 'abs_threshold', 'type': 'float', 'value':1., 'step' : .1},
                                        {'name': 'std_relative_threshold', 'type': 'float', 'value':6.},
                                        {'name': 'time_limits', 'type': 'range', 'value': [-np.inf, 0.]},
                                        {'name': 'freq_limits', 'type': 'range', 'value': [5.,90.]},
                                        {'name': 'Detect maximas', 'type': 'action'},
                                        {'name': 'Compute lines', 'type': 'action'},
                                        ])
        self.threshold_params.param('Detect maximas').sigActivated.connect(self.detectMaximas)
        self.threshold_params.param('Compute lines').sigActivated.connect(self.computeLines)
        
        self.clean_params = Parameter.create(name='Clean', type='group',
                    children = [{'name': 'minimum_cycle_number', 'type': 'float', 'value':2.},
                                        {'name': 'eliminate_simultaneous', 'type': 'bool', 'value':True},
                                        {'name': 'regroup_full_overlap', 'type': 'bool', 'value':True},
                                        {'name': 'eliminate_partial_overlap', 'type': 'bool', 'value':True},
                                        {'name': 'Clean list', 'type': 'action'},
                                        ])
        self.clean_params.param('Clean list').sigActivated.connect(self.cleanList)
        
        self.params = Parameter.create( name='Parameters', type='group',
                                                    children = [ {'name': 'Compute all', 'type': 'action'},
                                                                        self.tfr_params,
                                                                        self.detection_zone_params,
                                                                        self.threshold_params,
                                                                        self.clean_params ,
                                                                        ])
        self.params.param('Compute all').sigActivated.connect(self.computeAll)
                                                                    

        self.tree_param = ParameterTree()
        self.tree_param.header().hide()
        h.addWidget(self.tree_param, 2)
        self.tree_param.setParameters(self.params, showTop=True)
        
        # center
        spv = QSplitter(Qt.Vertical)
        h.addWidget(spv, 4)
        
        tree = self.treeviewOscillations = QTreeWidget(contextMenuPolicy = Qt.CustomContextMenu,
                                                                        selectionMode = QAbstractItemView.ExtendedSelection)
        tree.setColumnCount(3)
        tree.setHeaderLabels(['oscillation' , 'time_max', 'freq_max','amplitude_max' ])
        spv.addWidget(tree)
        tree.customContextMenuRequested.connect(self.contextMenuTreeviewOscillation)
        tree.itemDoubleClicked.connect(self.zoomOscillationOnDoubleClick)
        tree.itemSelectionChanged.connect(self.selectionOscillationChanged)

        
        # right side
        self.canvas = SimpleCanvasAndTool( )
        self.fig = self.canvas.fig
        spv.addWidget(self.canvas)
        
        # button
        buttonBox = QDialogButtonBox()
        
        but = QPushButton(QIcon(':/document-save.png'),'Save to DB (no delete)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        but.clicked.connect(self.save_to_db_no_delete)
        
        but = QPushButton(QIcon(':/document-save.png'),'Save to DB (delete old in interest zone)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        but.clicked.connect(self.save_to_db_and_delete)
        
        but = QPushButton(QIcon(':/reload.png'),'Reload from DB')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        but.clicked.connect(self.reload_from_db_all)
        
        but = QPushButton(QIcon(':/reload.png'),'Reload from DB (only interest zone)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        but.clicked.connect(self.reload_from_db_only_zone)

        but = QPushButton(QIcon(':/window-close.png') , 'Quit')
        buttonBox.addButton(but , QDialogButtonBox.RejectRole)
        but.clicked.connect(self.close)
        
        self.mainLayout.addWidget(buttonBox)
        
        
        #context menu
        self.menu = QMenu()
        act = self.menu.addAction(u'Delete')
        act.triggered.connect(self.deleteSelection)
        act = self.menu.addAction(u'Recompute')
        act.triggered.connect(self.recomputeSelection)
        act = self.menu.addAction(self.tr('Clean'))
        act.triggered.connect(self.cleanSelection)
        
        
        # 
        self.lineDetector = LineDetector(self.neoana)
        self.plotLineDetector = PlotLineDetector(figure = self.fig , 
                                                                lineDetector = self.lineDetector,)
                                                                
        self.checkParam()

    def save_to_db(self, delete_old = False ) :
        
        t1,t2,f1,f2 = [f.magnitude for f in self.lineDetector.detection_zone]
        
        # This is mapped Oscillation mapped class
        Oscillation = dict( [ (c.__name__, c) for c in self.mapped_classes])['Oscillation']
        
        if delete_old :
            query = self.session.query(Oscillation)
            query = query.filter(Oscillation.analogsignal_id==self.ana.id)
            query = query.filter( Oscillation.freq_max>= f1 ).filter( Oscillation.freq_max<= f2 )
            query = query.filter( Oscillation.time_max>= t1 ).filter( Oscillation.time_max<= t2 )
            for osci in query.all():
                self.session.delete(osci)
            self.session.commit()
            
        #create new ones
        for o,osci in enumerate(self.lineDetector.list_oscillation) :
            # oscillation in that list is not from mapped classes so copy and save to db
            osci2 = Oscillation()
            for k in Oscillation.usable_attributes:
                setattr(osci2, k, getattr(osci, k))
            self.ana.oscillations.append(osci2)
        self.session.commit()
        self.db_changed.emit()
        
    def save_to_db_no_delete(self) :
        self.save_to_db( delete_old = False)

    def save_to_db_and_delete(self):
        self.save_to_db( delete_old = True)



    def reload_from_db(self , only_by_zone = True):
        # This is mapped Oscillation mapped class
        Oscillation = dict( [ (c.__name__, c) for c in self.mapped_classes])['Oscillation']
        
        t1,t2,f1,f2 = [f.magnitude for f in self.lineDetector.detection_zone]
        
        self.lineDetector.list_oscillation = [ ]
        query = self.session.query(Oscillation)
        query = query.filter(Oscillation.analogsignal_id==self.ana.id)
        if only_by_zone :
            query = query.filter( Oscillation.freq_max>= f1 ).filter( Oscillation.freq_max<= f2 )
            query = query.filter( Oscillation.time_max>= t1 ).filter( Oscillation.time_max<= t2 )
        self.lineDetector.list_oscillation = [osci for osci in query.all() ]
            
        self.refreshTreeview()
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        


    def reload_from_db_all(self) :
        self.reload_from_db( only_by_zone = False)
        
        
    def reload_from_db_only_zone(self):
        self.reload_from_db( only_by_zone = True)
    
    def checkParam(self):
        # get from UI
        self.lineDetector.update( ** to_dict(self.tfr_params))
        
        d = to_dict(self.detection_zone_params)
        self.lineDetector.detection_zone = d['time_limits']+d['freq_limits']

        d = to_dict(self.threshold_params)
        for k in  ['manual_threshold', 'abs_threshold', 'std_relative_threshold']:
            setattr(self.lineDetector , k, d[k])
        self.lineDetector.reference_zone = d['time_limits']+d['freq_limits']
            
        self.lineDetector.update( **to_dict(self.clean_params))
        
        #check
        self.lineDetector.checkParam()
        
        # refresh UI
        for k in  to_dict(self.tfr_params):
            v = getattr(self.lineDetector, k)
            if isinstance(v, pq.Quantity):
                self.tfr_params[k] = v.magnitude
            else:
                self.tfr_params[k] = v
        
        self.detection_zone_params['time_limits'] = [ self.lineDetector.detection_zone[0].magnitude, self.lineDetector.detection_zone[1].magnitude]
        self.detection_zone_params['freq_limits'] = [ self.lineDetector.detection_zone[2].magnitude, self.lineDetector.detection_zone[3].magnitude]
        
        self.threshold_params['time_limits'] = [ self.lineDetector.reference_zone[0].magnitude, self.lineDetector.reference_zone[1].magnitude]
        self.threshold_params['freq_limits'] = [ self.lineDetector.reference_zone[2].magnitude, self.lineDetector.reference_zone[3].magnitude]
        
        # TODO enable or disabled
        #~ enabled = not(self.paramThreshold['manual_threshold'])
        #~ for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            #~ self.paramThreshold.params[k]['widget'].setEnabled( enabled )
        #~ self.paramThreshold.params['abs_threshold']['widget'].setEnabled( not(enabled) )
        #~ self.paramThreshold.params['std_relative_threshold']['widget'].setEnabled( enabled )

    def computeScalogram(self):
        self.checkParam()
        self.lineDetector.computeTimeFreq()
        self.plotLineDetector.plotMap()
        self.canvas.draw()

    def plotDetectionZone(self, *name):
        self.checkParam()
        self.plotLineDetector.plotFilteredSig()
        self.plotLineDetector.plotDetectionZone()
        self.canvas.draw()
        
    def redrawSignal(self):
        self.checkParam()
        self.plotLineDetector.plotFilteredSig()
        self.plotLineDetector.plotDetectionZone()
        self.canvas.draw()
    
    def refreshThreshold(self, *name):
        self.checkParam()
        self.threshold_params['abs_threshold'] = self.lineDetector.computeThreshold()
        self.plotLineDetector.plotReferenceZone()
        self.plotLineDetector.plotThreshold()
        self.canvas.draw()
        
    def detectMaximas(self):
        self.refreshThreshold()
        self.lineDetector.computeThreshold()
        self.lineDetector.detectMax()
        self.plotLineDetector.plotMax()
        self.canvas.draw()
        
    def computeLines(self):
        self.lineDetector.computeThreshold()
        self.lineDetector.detectLine()
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        
        self.refreshTreeview()
        
    def cleanList(self):
        self.lineDetector.update( **to_dict(self.clean_params) )
        self.lineDetector.cleanLine()
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()
        self.refreshTreeview()
        
    def computeAll(self):
        self.computeScalogram()
        self.plotDetectionZone()
        self.redrawSignal()
        self.detectMaximas()
        self.computeLines()
        self.cleanList()
        self.refreshTreeview()

    def refreshTreeview(self):
        self.treeviewOscillations.clear()
        for o,osci in enumerate(self.lineDetector.list_oscillation) :
            item = QTreeWidgetItem(["oscillation %s" % o  ,str(osci.time_max) , str(osci.freq_max) , str(osci.amplitude_max) ] )
            self.treeviewOscillations.addTopLevelItem(item)

    
    def contextMenuTreeviewOscillation(self , point) :
        self.menu.exec_(self.cursor().pos())
    
    def zoomOscillationOnDoubleClick(self, item):
         # push the current view to define home if stack is empty
        if self.canvas.toolbar._views.empty(): self.canvas.toolbar.push_current()
        
        pos = self.treeviewOscillations.indexFromItem(item).row()
        osc= self.lineDetector.list_oscillation[pos]
        fmin=osc.freq_line.min()
        fmax=osc.freq_line.max()
        delta_f=max(10.,(fmax-fmin)/3.)
        delta_t=(osc.time_stop-osc.time_start)/2.
        self.plotLineDetector.axMap.set_ylim(max(0.,fmin-delta_f),fmax+delta_f)
        self.plotLineDetector.axMap.set_xlim(osc.time_start-delta_t,osc.time_stop+delta_t,emit=True)
        self.canvas.draw()
        
        # push the current view to add new view in the toolbar history
        self.canvas.toolbar.push_current()
        
    def selectionOscillationChanged(self):
        for l in self.plotLineDetector.lineOscillations1:
            l.set_linewidth(3)
            l.set_color('m')
        for l in self.plotLineDetector.lineOscillations2:
            l.set_linewidth(1)
            l.set_color('m')
        for item in  self.treeviewOscillations.selectedItems() :
            pos = self.treeviewOscillations.indexFromItem(item).row()
            self.plotLineDetector.lineOscillations1[pos].set_linewidth(4)
            self.plotLineDetector.lineOscillations1[pos].set_color('c')
            self.plotLineDetector.lineOscillations2[pos].set_linewidth(5)
            self.plotLineDetector.lineOscillations2[pos].set_color('c')
        self.canvas.draw()
        
        
    def deleteSelection(self):
        toremove = [ ]
        for index in  self.treeviewOscillations.selectedIndexes() :
            if index.column()==0:
                toremove.append(self.lineDetector.list_oscillation[ index.row() ])
        for r in toremove :
            self.lineDetector.list_oscillation.remove(r)
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        
        self.refreshTreeview()


    def recomputeSelection(self):
        l = [ ]
        for index in  self.treeviewOscillations.selectedIndexes() :
            l.append( index.row() )
        
        self.lineDetector.recomputeSelection( l )
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        
        self.refreshTreeview()
    
    def cleanSelection(self):
        self.lineDetector.update( **to_dict(self.clean_params))
        
        l = [ ]
        for index in  self.treeviewOscillations.selectedIndexes() :
            l.append( index.row() )
        self.lineDetector.cleanSelection( l )
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        
        self.refreshTreeview()        




