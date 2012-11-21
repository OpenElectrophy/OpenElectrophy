# -*- coding: utf-8 -*-


"""
widget for managing several matplotlib figure
"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy

from guiutil.icons import icons
#~ from guiutil.globalapplicationdict import *
from guiutil.paramwidget import ParamWidget, LimitWidget
from enhancedmatplotlib import *
import numpy
from numpy import inf

from ..classes import allclasses, Oscillation, AnalogSignal
from ..computing.timefrequency import LineDetector, PlotLineDetector
from enhancedmatplotlib import SimpleCanvasAndTool
from queryresultbox import QueryResultBox

from sqlalchemy import and_, or_


morletParams = [ ['f_start' , {'value' : 5. }],
                            ['f_stop' , {'value' : 100. }],
                            ['deltafreq' , {'value' : 1. }],
                            ['sampling_rate' , {'value' : 200.  }],
                            #~ ['t_start' , {'value' :  -inf}],
                            #~ ['t_stop' , {'value' :  inf}],
                            ['t_start' , {'value' :  0.}],
                            ['t_stop' , {'value' :  10.}],
                            ['f0' , {'value' :  2.5}],
                            ['normalisation' , {'value' :  0.}],
                        ]

detectionZoneParams = [  ['t1' , {'value' :0. ,  }],
                                        ['t2' , {'value' : inf ,  } ],
                                        ['f1' , {'value' : 20. ,  } ],
                                        ['f2' , {'value' : 80 ,   }],
                                        #~ ['time_lim' , {'value' : [0, inf ] , 'widgettype' : LimitWidget } ],
                                        #~ ['freq_lim' , {'value' : [20, 80 ] , 'widgettype' : LimitWidget  }],
                                    ]

thresholdParams =[  ['manual_threshold' , {'value' :  True}],
                                ['abs_threshold' , {'value' : 1.}],
                                ['t1' , {'value' :-inf ,  }],
                                ['t2' , {'value' : 0.,  } ],
                                ['f1' , {'value' : 20. ,  } ],
                                ['f2' , {'value' : 80. ,   }],
                                #~ ['time_lim' , {'value' : [0, inf ] , 'widgettype' : LimitWidget } ],
                                #~ ['freq_lim' , {'value' : [-inf, 0 ] , 'widgettype' : LimitWidget  }],
                                ['std_relative_threshold' , {'value' : 6., 'label' : 'std_threshold'}],
                            ]

cleanParams = [ ['minimum_cycle_number' , {'value' : 2. }],
                            ['eliminate_simultaneous' , {'value' : True }],
                            ['regroup_full_overlap' , {'value' : True }],
                            ['eliminate_partial_overlap' , {'value' : True  }],
                        ]



class OscillationDetection(QDialog) :
    """
    Scroll area resazible for stacking matplotlib canvas
    
    """
    def __init__(self  , parent = None ,
                            metadata =None,
                            Session = None,
                            globalApplicationDict = None,
                            id_analogsignal = None,
                            tablename = None,
                            mode = 'all signal',
                            ):
        QDialog.__init__(self, parent)
        self.metadata = metadata
        self.session = Session()
        self.globalApplicationDict = globalApplicationDict
        
        self.anaSig = self.session.query(AnalogSignal).filter_by(id=id_analogsignal).one()
        self.mode = mode


        #FIXME: do not work:
        self.setModal(False)
        self.setWindowModality (  Qt.NonModal )

        self.setWindowTitle(self.tr('OpenElectrophy Edit oscillation for %d'%(self.anaSig.id) ))
        self.setWindowIcon(QIcon(':/oscillation.png'))
        
        
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.tab = QTabWidget()
        self.mainLayout.addWidget(self.tab)
        
        if self.mode == 'around epoch' :
            fr = QFrame()
            self.tab.addTab(fr,'Epoch list')
            v1 = QVBoxLayout()
            fr.setLayout(v1)
            
            #~ default_query = "SELECT id_epoch FROM epoch WHERE epoch.id_trial = %d "  % (self.elec.id_trial)
            #~ self.queryBoxEpoch = QueryResultBox(table = 'epoch', field_list = Epoch.list_field, default_query = default_query )
            #~ v1.addWidget(self.queryBoxEpoch)
            #~ self.queryBoxEpoch.treeview_result.setSelectionMode(QAbstractItemView.SingleSelection)
            #~ self.connect(self.queryBoxEpoch.treeview_result , SIGNAL('itemSelectionChanged()') , self.changeEpoch)

            query = "SELECT event.id \nFROM event \nWHERE event.id_segment = %s\n"%( self.anaSig.id_segment)
            self.queryEvent = QueryResultBox(
                                                                metadata = self.metadata,
                                                                session = self.session,
                                                                globalApplicationDict = self.globalApplicationDict,
                                                                table = 'event',
                                                                orientation = Qt.Horizontal,
                                                                query = query,
                                                                )
            v1.addWidget(self.queryEvent,2)
            self.queryEvent.tree.treeview.setSelectionMode(QAbstractItemView.SingleSelection)
            self.connect(self.queryEvent.tree.treeview , SIGNAL('clicked( QModelIndex )') , self.changeSelectedEvent)
            
            
            #~ params = [
                                #~ ('t_start', {'value' : -1., }),
                                #~ ('t_stop', {'value' : 3., }),
                            #~ ]
            #~ self.paramEvent = ParamWidget(params ,
                                                            #~ applicationdict = self.globalApplicationDict,
                                                            #~ keyformemory = 'linedetector/event_window' ,
                                                            #~ title = 'Choose the window',
                                                            #~ )
            #~ v1.addWidget(self.paramEvent,0)
            v1.addSpacing(0)
            self.activeEvent = None
            
            
            
            
        
        fr = QFrame()
        self.tab.addTab(fr,'Oscillations')
        h= QHBoxLayout()
        fr.setLayout(h)
        
        # Scalogram
        v = QVBoxLayout()
        h.addLayout(v)
        self.paramMorlet = ParamWidget(morletParams ,
                                                            applicationdict = globalApplicationDict,
                                                            keyformemory = 'linedetector/morlet' ,
                                                            title = 'Parameters for scalogram',
                                                            )
        v.addWidget(self.paramMorlet)
        hb = QHBoxLayout()
        v.addLayout(hb)
        hb.addStretch(0)
        but = QPushButton(QIcon(':/'), 'Compute scalogram')
        self.connect(but, SIGNAL('clicked()'), self.computeScalogram)
        hb.addWidget(but)
        
        
        # detection zone
        v.addSpacing(20)
        self.paramDetectionZone = ParamWidget(detectionZoneParams ,
                                                            applicationdict = globalApplicationDict,
                                                            keyformemory = 'linedetector/detection_zone' ,
                                                            title = 'Detection zone',
                                                            )
        v.addWidget(self.paramDetectionZone)
        self.connect(self.paramDetectionZone, SIGNAL('paramChanged( QString )'), self.plotDetectionZone)
        hb = QHBoxLayout()
        v.addLayout(hb)
        hb.addStretch(0)
        but = QPushButton(QIcon(':/'), 'Redraw signal')
        self.connect(but, SIGNAL('clicked()'), self.redrawSignal)
        hb.addWidget(but)
        
        
        
        
        v.addStretch(0)
        
        # threshold
        v = QVBoxLayout()
        h.addLayout(v) 
        self.paramThreshold = ParamWidget(thresholdParams ,
                                                            applicationdict = globalApplicationDict,
                                                            keyformemory = 'linedetector/threshold' ,
                                                            title = 'Threshold',
                                                            )
        v.addWidget(self.paramThreshold)
        self.connect(self.paramThreshold, SIGNAL('paramChanged( QString )'), self.refreshThreshold)
        hb = QHBoxLayout()
        v.addLayout(hb)
        hb.addStretch(0)
        but = QPushButton(QIcon(':/'), 'Detect maximas')
        self.connect(but, SIGNAL('clicked()'), self.detectMaximas)
        hb.addWidget(but)
        but = QPushButton(QIcon(':/'), 'Compute lines')
        self.connect(but, SIGNAL('clicked()'), self.computeLines)
        hb.addWidget(but)        

        # clean
        v.addSpacing(20)
        self.paramClean = ParamWidget(cleanParams ,
                                                            applicationdict = globalApplicationDict,
                                                            keyformemory = 'linedetector/clean' ,
                                                            title = 'Clean',
                                                            )
        v.addWidget(self.paramClean)            
        hb = QHBoxLayout()
        v.addLayout(hb)
        hb.addStretch(0)
        but = QPushButton(QIcon(':/'), 'Clean list')
        hb.addWidget(but)
        self.connect(but, SIGNAL('clicked()'), self.cleanList)
        
        v.addSpacing(27)
        but = QPushButton(QIcon(':/'), 'Compute all')
        v.addWidget(but)
        self.connect(but, SIGNAL('clicked()'), self.computeAll)

        
        v.addStretch(0)
        
        # center
        #~ v = QVBoxLayout()
        #~ h.addLayout(v)
        spv = QSplitter(Qt.Vertical)
        #~ spv.setOpaqueResize(False)
        h.addWidget(spv, 10)
        
        self.treeviewOscillations = QTreeWidget()
        self.treeviewOscillations.setColumnCount(3)
        self.treeviewOscillations.setHeaderLabels(['oscillation' , 'time_max', 'freq_max','amplitude_max' ])
        self.treeviewOscillations.setSelectionMode(QAbstractItemView.ExtendedSelection)
        spv.addWidget(self.treeviewOscillations)

        self.treeviewOscillations.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.treeviewOscillations,SIGNAL('customContextMenuRequested( const QPoint &)'),self.contextMenuTreeviewOscillation)
        self.connect(self.treeviewOscillations,SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),self.zoomOscillationOnDoubleClick)
        self.connect(self.treeviewOscillations,SIGNAL('itemSelectionChanged()'),self.selectionOscillationChanged)


        
        # right side
        #~ v = QHBoxLayout()
        #~ h.addLayout(v)
        self.canvas = SimpleCanvasAndTool(orientation = Qt.Vertical )
        self.fig = self.canvas.fig
        spv.addWidget(self.canvas)
        
        # button
        buttonBox = QDialogButtonBox()
        
        but = QPushButton(QIcon(':/document-save.png'),'Save to DB (no delete)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.save_to_db_no_delete)
        
        but = QPushButton(QIcon(':/document-save.png'),'Save to DB (delete old in interest zone)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.save_to_db_and_delete)
        
        but = QPushButton(QIcon(':/reload.png'),'Reload from DB')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.reload_from_db_all)
        
        but = QPushButton(QIcon(':/reload.png'),'Reload from DB (only interest zone)')
        buttonBox.addButton(but , QDialogButtonBox.ActionRole)
        self.connect(but, SIGNAL('clicked()'), self.reload_from_db_only_zone)

        but = QPushButton(QIcon(':/window-close.png') , 'Quit')
        buttonBox.addButton(but , QDialogButtonBox.RejectRole)
        self.connect(but, SIGNAL('clicked()'), self.close)
        self.mainLayout.addWidget(buttonBox)
        
        
        #context menu
        self.menu = QMenu()
        act = self.menu.addAction(self.tr('Delete'))
        self.connect(act,SIGNAL('triggered()') ,self.deleteSelection)
        act = self.menu.addAction(self.tr('Recompute'))
        self.connect(act,SIGNAL('triggered()') ,self.recomputeSelection)
        act = self.menu.addAction(self.tr('Clean'))
        self.connect(act,SIGNAL('triggered()') ,self.cleanSelection)
        
        
        # 
        self.lineDetector = LineDetector(self.anaSig,)
        self.plotLineDetector = PlotLineDetector(figure = self.fig , 
                                                                lineDetector = self.lineDetector,)
                                                                
        self.checkParam()

    def save_to_db(self, delete_old = False ) :
        
        t1,t2,f1,f2 = self.lineDetector.detection_zone
        if self.mode == 'all signal' or self.mode == 'around epoch'  :
            # delete old oscillations in database
            if delete_old :
                query = self.session.query(Oscillation)
                query = query.filter(Oscillation.id_analogsignal==self.anaSig.id)
                query = query.filter( Oscillation.freq_max>= f1 ).filter( Oscillation.freq_max<= f2 )
                query = query.filter( Oscillation.time_max>= t1 ).filter( Oscillation.time_max<= t2 )
                for osci in query.all():
                    self.session.delete(osci)
                self.session.commit()
                
            #create new ones
            for o,osci in enumerate(self.lineDetector.list_oscillation) :
                #~ if osci in self.session:
                    #~ self.session.expunge( osci )
                    #~ self.session.commit()
                #~ osci.id = None
                #~ osci.id_analogsignal = self.anaSig.id
                #~ self.session.merge(osci)
                
                
                #~ osci2 = osci.copy()
                #~ osci2.id_analogsignal = self.anaSig.id
                #~ self.session.add(osci2)
                self.anaSig._oscillations.append(osci.copy())
                self.session.commit()
        
    def save_to_db_no_delete(self) :
        self.save_to_db( delete_old = False)

    def save_to_db_and_delete(self):
        self.save_to_db( delete_old = True)



    def reload_from_db(self , only_by_zone = True):
        
        t1,t2,f1,f2 = self.lineDetector.detection_zone
        if self.mode == 'all signal' or self.mode == 'around epoch':
            self.lineDetector.list_oscillation = []
            query = self.session.query(Oscillation)
            query = query.filter(Oscillation.id_analogsignal==self.anaSig.id)
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


    
    def changeSelectedEvent(self, index):
        #~ print 'change', index.row()
        ev = index.internalPointer()
        if self.activeEvent is  None:
            shift = ev.time
        else:
            shift = ev.time - self.activeEvent.time
        self.paramMorlet.update(    {
                                                    't_start' : self.paramMorlet['t_start']+shift,
                                                    't_stop' : self.paramMorlet['t_stop']+shift,
                                                    }
                                            )
        self.paramDetectionZone.update( {
                                                                't1' : self.paramDetectionZone['t1']+shift,
                                                                't2' : self.paramDetectionZone['t2']+shift,
                                                                }
                                                        )
                                            
        self.paramThreshold.update( {
                                                                't1' : self.paramThreshold['t1']+shift,
                                                                't2' : self.paramThreshold['t2']+shift,
                                                                }
                                                        )
        self.plotLineDetector.clear()
        self.canvas.draw()
        self.checkParam()
        self.activeEvent = ev
        self.plotLineDetector.axMap.axvline( ev.time, color = 'c' , linewidth = 2)
        self.plotLineDetector.axSig.axvline( ev.time, color = 'c' , linewidth = 2)
        self.redrawSignal()
        self.computeScalogram()
        


    def checkParam(self):
        # get from UI
        self.lineDetector.update( **self.paramMorlet.get_dict() )
        
        self.lineDetector.detection_zone = [ ]
        for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            self.lineDetector.detection_zone += [ self.paramDetectionZone[k] ]
        
        for k in  ['manual_threshold', 'abs_threshold', 'std_relative_threshold']:
            setattr(self.lineDetector , k, self.paramThreshold[k])
        self.lineDetector.reference_zone = [ ]
        for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            self.lineDetector.reference_zone += [ self.paramThreshold[k] ]
            
        self.lineDetector.update( **self.paramClean.get_dict() )
        
        #check
        self.lineDetector.checkParam()
        
        # refresh UI
        for k in self.paramMorlet.get_dict():
            self.paramMorlet[k] = self.lineDetector.__dict__[k]        
        for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            self.paramDetectionZone[k] = self.lineDetector.detection_zone[i]
        for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            self.paramThreshold[k] = self.lineDetector.reference_zone[i]
        enabled = not(self.paramThreshold['manual_threshold'])
        for i,k in enumerate(['t1', 't2', 'f1', 'f2']) :
            self.paramThreshold.params[k]['widget'].setEnabled( enabled )
        self.paramThreshold.params['abs_threshold']['widget'].setEnabled( not(enabled) )
        self.paramThreshold.params['std_relative_threshold']['widget'].setEnabled( enabled )

    def computeScalogram(self):
        self.checkParam()
        self.lineDetector.computeTimeFreq()
        self.plotLineDetector.plotMap()
        self.canvas.draw()
        if self.mode == 'around epoch' and self.activeEvent is not None:
            self.plotLineDetector.axMap.axvline( self.activeEvent.time, color = 'c' , linewidth = 2)
            #~ self.plotLineDetector.axSig.axvline( self.activeEvent.time, color = 'c' , linewidth = 2)

    def plotDetectionZone(self, *name):
        self.checkParam()
        #~ self.plotLineDetector.plotFilteredSig()
        self.plotLineDetector.plotDetectionZone()
        self.canvas.draw()
        
    def redrawSignal(self):
        self.checkParam()
        self.plotLineDetector.plotFilteredSig()
        self.plotLineDetector.plotDetectionZone()
        self.canvas.draw()
        if self.mode == 'around epoch' and self.activeEvent is not None:
            #~ self.plotLineDetector.axMap.axvline( self.activeEvent.time, color = 'c' , linewidth = 2)
            self.plotLineDetector.axSig.axvline( self.activeEvent.time, color = 'c' , linewidth = 2) 
    
    def refreshThreshold(self, *name):
        self.checkParam()
        
        self.paramThreshold['abs_threshold'] = self.lineDetector.computeThreshold()
        self.plotLineDetector.plotReferenceZone()
        self.plotLineDetector.plotThreshold()
        self.canvas.draw()
        
        
    def detectMaximas(self):
        self.refreshThreshold()
        #~ self.lineDetector.computeThreshold()
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
        self.lineDetector.update( **self.paramClean.get_dict() )
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
        #~ print self.lineDetector.sampling_rate
        #~ print self.plotLineDetector.lineDetector.sampling_rate
        
        
    def refreshTreeview(self):
        self.treeviewOscillations.clear()
        for o,osci in enumerate(self.lineDetector.list_oscillation) :
            item = QTreeWidgetItem(["oscillation %s" % o  ,str(osci.time_max) , str(osci.freq_max) , str(osci.amplitude_max) ] )
            self.treeviewOscillations.addTopLevelItem(item)

    
    def contextMenuTreeviewOscillation(self , point) :
        #~ for item in  self.treeviewOscillations.selectedItems() :
            #~ pos = self.treeviewOscillations.indexFromItem(item).row()
            
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
        self.lineDetector.update( **self.paramClean.get_dict() )
        
        l = [ ]
        for index in  self.treeviewOscillations.selectedIndexes() :
            l.append( index.row() )
        self.lineDetector.cleanSelection( l )
        self.plotLineDetector.plotOscillations()
        self.canvas.draw()        
        self.refreshTreeview()        




