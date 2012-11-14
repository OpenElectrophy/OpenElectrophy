# -*- coding: utf-8 -*-
"""
Signal viewers
"""

#TODO: look at signal proxy for fast and slow refresh when global parmaters change

from tools import *
import pyqtgraph as pg
#~ from pyqtgraph.parametertree import Parameter, ParameterTree



from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter




class SignalViewer(ViewerBase):
    """
    A multi signal viewer trying to be efficient for very big data.
    
    Trick:
       * fast refresh with pure decimation (= bad for aliasing)
       * slow refresh with all point when not moving.
       * if AnaloSignal share same t_start and sampling_rate =>  same time vector
    
    
    
    """
    def __init__(self, parent = None,
                            analogsignals = [ ],
                            spiketrains_on_signals = None,
                            xsize = 10.,
                            ylims ='auto',
                            max_point_if_decimate = 2000,
                            show_toolbar = True,
                            **kargs
                            ):
                            
        super(SignalViewer,self).__init__(parent)
        
        self.max_point_if_decimate = max_point_if_decimate

        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        #~ if ylims =='auto' and len(analogsignals)>0:
            #~ ylims = [0,0]
            #~ for ana in analogsignals:
                #~ ylims[1] = max([max(ana.magnitude) , ylims[1]])
                #~ ylims[0] = min([min(ana.magnitude), ylims[0]])
        #~ elif type(ylims) == list:
            #~ ylims = list(ylims)
        #~ else:
            #~ ylims = [-10,10]
        #~ self.ylims_changer.set_ylims(ylims)
        
        viewBox = OptionsViewBox()
        viewBox.clicked.connect(self.open_configure_dialog)
        
        self.graphicsview  = pg.GraphicsView()#useOpenGL = True)
        self.mainlayout.addWidget(self.graphicsview)
        
        self.plot = pg.PlotItem(viewBox = viewBox)
        self.graphicsview.setCentralItem(self.plot)

        
        

        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = [ {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
                                                                        {'name': 'ylims', 'type': 'range', 'value': [-10., 10.] },
                                                                        {'name': 'background_color', 'type': 'color', 'value': 'k' },
                                                                    ])
        
        
        
        # inialize
        self.clear_all()
        self.set_analosignals(analogsignals)
        self.set_spiketrains_on_signals(spiketrains_on_signals)
        self.set_xsize(xsize)
        self.set_ylims([-10, 10])
        
        self.paramGlobal.sigTreeStateChanged.connect(lambda : self.refresh(fast = True))
    
    def get_xsize(self):
        return self.paramGlobal.param('xsize').value()
    def set_xsize(self, xsize):
        self.paramGlobal.param('xsize').setValue(xsize)
    xsize = property(get_xsize, set_xsize)

    def get_ylims(self):
        return self.paramGlobal.param('ylims').value()
    def set_ylims(self,ylims):
        self.paramGlobal.param('ylims').setValue(ylims)
    ylims = property(get_ylims, set_ylims)
    
    def clear_all(self):
        self.plot.clear()
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = 'g')
        self.plot.addItem(self.vline)
        self.spikeonsignal_curves = [ ]
        self.analogsignal_curves = [ ]
        

    def set_analosignals(self, analogsignals):
        self.analogsignals = analogsignals
        
        self.signalViewerParameters = SignalViewerParameters(paramGlobal = self.paramGlobal, analogsignals = analogsignals, parent= self)
        self.signalViewerParameters.setWindowFlags(Qt.Window)
        self.paramSignals = self.signalViewerParameters.paramSignals
        
        
        
        
        self.analogsignal_curves = [ ]
        self.times_familly = { }# signal sharing same size sampling and t_start are in the same familly
        for i,anasig in enumerate(analogsignals):
            key = (float(anasig.t_start.rescale('s').magnitude), float(anasig.sampling_rate.rescale('Hz').magnitude), anasig.size)
            if  key in self.times_familly:
                self.times_familly[key].append(i)
            else:
                self.times_familly[key] = [ i ]
            color = anasig.annotations.get('color', 'w')
            curve = self.plot.plot([np.nan], [np.nan], pen = color)
            self.analogsignal_curves.append(curve)
            self.paramSignals[i].param('color').setValue(color)
        
        for p in self.paramSignals:
            p.sigTreeStateChanged.connect(self.refreshColorAndStyle)
        
    
    def set_spiketrains_on_signals(self, spiketrains_on_signals):
        self.spiketrains_on_signals = spiketrains_on_signals
        if spiketrains_on_signals is None: return
        for c, curves in enumerate(self.spikeonsignal_curves):
            for s, curve in enumerate(curves):
                self.plot.delItem(curve)
        assert len(spiketrains_on_signals)==len(self.analogsignals), 'must have same size'
        self.spikeonsignal_curves = [ ]
        for c,spiketrains in enumerate(spiketrains_on_signals):
            self.spikeonsignal_curves.append([])
            for s,sptr in enumerate(spiketrains):
                color = sptr.annotations.get('color', ['red', 'green', 'blue', ][s%3])
                if type(color) == tuple or type(color) == list:
                    r,g,b = color
                    color = QColor( r*255,g*255,b*255  )
                else:
                    color = QColor(color)

                markersize = sptr.annotations.get('markersize', 7)
                # Note symbolPen = autour      symbolBrush = dedans
                curve =  pg.ScatterPlotItem(x=[ 0], y=[ 0], pen=None, brush=color, size=10, pxMode = True)
                self.plot.addItem(curve)
                self.spikeonsignal_curves[-1].append(curve)
                
                # compute index and signal value for times
                ana = self.analogsignals[c]
                spike_indexes = np.round(((sptr-ana.t_start)*ana.sampling_rate).simplified.magnitude).astype(int)
                spike_values = ana[spike_indexes].magnitude
        
    def open_configure_dialog(self):
        self.signalViewerParameters.setWindowFlags(Qt.Window)
        self.signalViewerParameters.show()
    
    def refreshColorAndStyle(self, param, changes):
        n = self.paramSignals.index(param)
        #~ pen = pg.mkPen(color = param.param('color').value(),  width = param.param('width').value())
        pen = pg.mkPen(color = param.param('color').value())
        self.analogsignal_curves[n].setPen(pen)
        self.refresh(fast = True)
    
    def refresh(self, fast = False):
        """
        When fast it do decimate.
        """
        #~ t1 = time.time()
        #~ print 'self.refresh', fast
        
        color = self.paramGlobal.param('background_color').value()
        self.graphicsview.setBackground(color)
        
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        for key, sig_nums in self.times_familly.items():
            if fast:
                decimate = self.max_point_if_decimate
            else:
                decimate = None
            t_vect, sl = get_analogsignal_slice(self.analogsignals[sig_nums[0]], t_start*pq.s, t_stop*pq.s,
                                                        return_t_vect = True,decimate = decimate,)
            for c in sig_nums:
                curve = self.analogsignal_curves[c]
                if not self.paramSignals[c].param('visible').value():
                    curve.setData([np.nan], [np.nan])
                    continue
                ana = self.analogsignals[c]
                chunk = ana.magnitude[sl]
                
                if chunk.size==0:
                    curve.setData([np.nan], [np.nan])
                else:
                    g = self.paramSignals[c].param('gain').value()
                    o = self.paramSignals[c].param('offset').value()
                    curve.setData(t_vect, chunk*g+o)
                
        if self.spiketrains_on_signals is not None:
            for c, curves in enumerate(self.spikeonsignal_curves):
                for s, curve in enumerate(curves):
                    sptr = self.spiketrains_on_signals[c][s]
                    ana = self.analogsignals[c]
                    times = sptr[(sptr>=t_start*pq.s) & (sptr<t_stop*pq.s)]
                    pos = np.round(((times-ana.t_start)*ana.sampling_rate).simplified.magnitude).astype(int)
                    curve.setData(times, ana.magnitude[pos])
                
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( *self.ylims )
        
        # 700ms
        #~ self.plot.replot()
        #~ t2 = time.time()
        #~ print fast, self.__class__, t2-t1
        #~ print
        
        self.is_refreshing = False




class SignalViewerParameters(QWidget):
    def __init__(self, parent = None, analogsignals = [ ], paramGlobal = None):
        super(SignalViewerParameters, self).__init__(parent)
        
        param_by_channel = [ 
                        {'name': 'channel_name', 'type': 'str', 'value': '','readonly' : True},
                        {'name': 'channel_index', 'type': 'str', 'value': '','readonly' : True},
                        {'name': 'color', 'type': 'color', 'value': "FF0"},
                        #~ {'name': 'width', 'type': 'int', 'value': 2},
                        #~ {'name': 'style', 'type': 'list', 
                                    #~ 'values': OrderedDict([ ('SolidLine', Qt.SolidLine), ('DotLine', Qt.DotLine), ('DashLine', Qt.DashLine),]), 
                                    #~ 'value': Qt.SolidLine},
                        {'name': 'gain', 'type': 'float', 'value': 1, 'step': 0.1},
                        {'name': 'offset', 'type': 'float', 'value': 0., 'step': 0.1},
                        {'name': 'visible', 'type': 'bool', 'value': True},
                    ]        
        
        self.analogsignals = analogsignals
        self.paramGlobal = paramGlobal
        
        #~ self.all_abs_max = np.array([ np.max(np.abs(anasig.magnitude)) for anasig in self.analogsignals ])
        self.all_abs_max = np.array([ np.abs(np.std(anasig.magnitude)) for anasig in self.analogsignals ])
        
        

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = u'Options for AnalogSignals'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.paramRoot = pg.parametertree.Parameter.create(name='AnalogSignals', type='group', children=[ ])
        self.paramSignals = [ ]
        for i, anasig in enumerate(self.analogsignals):
            pSignal = pg.parametertree.Parameter.create( name='AnalogSignal {}'.format(i), type='group', children = param_by_channel)
            for k in ['channel_name', 'channel_index']:
                if k in anasig.annotations:
                    pSignal.param(k).setValue(anasig.annotations[k])
            self.paramSignals.append(pSignal)
            self.paramRoot.addChild(pSignal)
        
        self.tree2 = pg.parametertree.ParameterTree()
        self.tree2.header().hide()
        h.addWidget(self.tree2, 4)
        self.tree2.setParameters(self.paramRoot, showTop=True)
        self.tree2.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        for pSignal in self.paramSignals:
            treeitem = pSignal.items.keys()[0]
            if treeitem is not None:
                treeitem.setExpanded(False)

        
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.tree3 = pg.parametertree.ParameterTree()
        self.tree3.header().hide()
        v.addWidget(self.tree3)
        self.tree3.setParameters(self.paramGlobal, showTop=True)

        self.paramSelection = pg.parametertree.Parameter.create( name='Multiple change for selection', type='group',
                                                    children = param_by_channel[2:], tip= u'This options apply on selection AnalogSignal on left list')
        self.paramSelection.sigTreeStateChanged.connect(self.paramSelectionChanged)
        self.tree1 = pg.parametertree.ParameterTree()
        self.tree1.header().hide()
        v.addWidget(self.tree1)
        self.tree1.setParameters(self.paramSelection, showTop=True)
        
        # Gain and offset
        v.addWidget(QLabel(u'<b>Automatic gain and offset:<\b>'))
        but = QPushButton('Center all (gain = 1, offset = 0)')
        but.clicked.connect(self.center_all)
        v.addWidget(but)        
        for apply_for_selection, labels in enumerate([[ 'Spread all identical gain', 'Spread all adapted gain'],
                                                            ['Spread selection identical gain', 'Spread selection adapted gain' ]] ):
            for gain_adaptated, label in enumerate(labels):
                but = QPushButton(label)
                but.gain_adaptated  = gain_adaptated
                but.apply_for_selection  = apply_for_selection
                but.clicked.connect(self.automatic_gain_offset)
                v.addWidget(but)

        v.addWidget(QLabel(self.tr('<b>Automatic color:<\b>'),self))
        but = QPushButton('Progressive')
        but.clicked.connect(self.automatic_color)
        v.addWidget(but)

    def center_all(self):
        for pSignal in self.paramSignals:
            pSignal.param('gain').setValue(1)
            pSignal.param('offset').setValue(0)
            pSignal.param('visible').setValue(True)
    
    def automatic_gain_offset(self):
        selected =  np.ones(len(self.paramSignals), dtype = bool)
        gains = np.zeros(len(self.paramSignals), dtype = float)
        if self.sender().apply_for_selection :
            ind = np.zeros(len(self.paramSignals), dtype = bool)
            for i, pSignal in enumerate(self.paramSignals):
                treeitem = pSignal.items.keys()[0]
                selected[i] = treeitem in self.tree2.selectedItems()
            if not selected.any(): return
        
        n = np.sum(selected)
        ylims  = self.paramGlobal.param('ylims').value()
        dy = np.diff(ylims)[0]/(n+1)
        gains = np.zeros(self.all_abs_max.size, dtype = float)
        if self.sender().gain_adaptated:
            gains = dy/n/self.all_abs_max
        else:
            gains = np.ones(self.all_abs_max.size, dtype = float) * dy/n/max(self.all_abs_max[selected])
        
        o = .5
        for i, pSignal in enumerate(self.paramSignals):
            pSignal.param('visible').setValue(selected[i])
            if selected[i]:
                pSignal.param('gain').setValue(gains[i]*2)
                pSignal.param('offset').setValue(dy*o+ylims[0])
                o+=1
    
    def automatic_color(self):
        n = len(self.analogsignals)
        cmap = get_cmap('jet' , n)
        for i, pSignal in enumerate(self.paramSignals):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            pSignal.param('color').setValue(color)
       
            
    def paramSelectionChanged(self, param, changes):
        for pSignal in self.paramSignals:
            treeitem =  pSignal.items.keys()[0]
            for param, change, data in changes:
                if treeitem in self.tree2.selectedItems():
                    pSignal.param(param.name()).setValue(data)        



