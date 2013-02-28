# -*- coding: utf-8 -*-
"""
Signal viewers
"""


from tools import *
import pyqtgraph as pg

from .multichannelparam import MultiChannelParam

from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter

param_global = [
    {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
    {'name': 'ylims', 'type': 'range', 'value': [-10., 10.] },
    {'name': 'background_color', 'type': 'color', 'value': 'k' },
    ]

param_by_channel = [ 
    #~ {'name': 'channel_name', 'type': 'str', 'value': '','readonly' : True},
    #~ {'name': 'channel_index', 'type': 'str', 'value': '','readonly' : True},
    {'name': 'color', 'type': 'color', 'value': "FF0"},
    #~ {'name': 'width', 'type': 'float', 'value': 1. , 'step': 0.1},
    #~ {'name': 'style', 'type': 'list', 
                #~ 'values': OrderedDict([ ('SolidLine', Qt.SolidLine), ('DotLine', Qt.DotLine), ('DashLine', Qt.DashLine),]), 
                #~ 'value': Qt.SolidLine},
    {'name': 'gain', 'type': 'float', 'value': 1, 'step': 0.1},
    {'name': 'offset', 'type': 'float', 'value': 0., 'step': 0.1},
    {'name': 'visible', 'type': 'bool', 'value': True},
    ]        

class MyViewBox(pg.ViewBox):
    clicked = pyqtSignal()
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
    def mouseClickEvent(self, ev):
        self.clicked.emit()
        ev.accept()
    def mouseDragEvent(self, ev):
        ev.ignore()
    def wheelEvent(self, ev):
        if ev.delta()>0:
            self.zoom_in.emit()
        else:
            self.zoom_out.emit()
        ev.accept()


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
                            max_point_if_decimate = 2000,
                            with_time_seeker = False,
                            **kargs
                            ):
                            
        super(SignalViewer,self).__init__(parent)
        
        self.max_point_if_decimate = max_point_if_decimate

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.viewBox = MyViewBox()
        self.viewBox.clicked.connect(self.open_configure_dialog)
        
        self.graphicsview  = pg.GraphicsView()#useOpenGL = True)
        self.mainlayout.addWidget(self.graphicsview)
        
        self.plot = pg.PlotItem(viewBox = self.viewBox)
        self.graphicsview.setCentralItem(self.plot)
        
        
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options',
                                                    type='group', children =param_global)
        
        
        
        # inialize
        self.clear_all()
        self.set_analosignals(analogsignals)
        self.set_xsize(xsize)
        
        
        if with_time_seeker:
            self.timeseeker = TimeSeeker()
            self.mainlayout.addWidget(self.timeseeker)
            self.timeseeker.set_start_stop(*find_best_start_stop(analogsignals =analogsignals))
            self.timeseeker.time_changed.connect(self.seek)
            self.timeseeker.fast_time_changed.connect(self.fast_seek)
            
        
    
    def get_xsize(self):
        return self.paramGlobal.param('xsize').value()
    def set_xsize(self, xsize):
        self.paramGlobal.param('xsize').setValue(xsize)
    xsize = property(get_xsize, set_xsize)

    
    def clear_all(self):
        self.plot.clear()
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = 'g')
        self.plot.addItem(self.vline)
        self.spikeonsignal_curves = [ ]
        self.analogsignal_curves = [ ]
        

    def set_analosignals(self, analogsignals, magic_color = True, magic_scale = True):
        self.analogsignals = analogsignals
        
        # pre compute std and max
        self.all_std = np.array([ np.std(anasig.magnitude) for anasig in self.analogsignals ])
        self.all_max = np.array([ np.max(anasig.magnitude) for anasig in self.analogsignals ])
        self.all_min = np.array([ np.min(anasig.magnitude) for anasig in self.analogsignals ])
        
        ylims = [np.min(self.all_min), np.max(self.all_max) ]
        self.paramGlobal.param('ylims').setValue(ylims)
        
        # Create parameters
        all = [ ]
        for i, ana in enumerate(self.analogsignals):
            if 'channel_index' in ana.annotations:
                name = 'AnalogSignal {} name={} channel_index={}'.format(i, ana.name, ana.annotations['channel_index'])
            else:
                name = 'AnalogSignal {} name={}'.format(i, ana.name)
            all.append({ 'name': name, 'type' : 'group', 'children' : param_by_channel})
        self.paramSignals = pg.parametertree.Parameter.create(name='AnalogSignals', type='group', children=all)
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', children = [self.paramGlobal,self.paramSignals  ])
        
        self.paramControler = SignalViewerControler(viewer = self)
        self.viewBox.zoom_in.connect(lambda : self.paramControler.gain_zoom(.8))
        self.viewBox.zoom_out.connect(lambda : self.paramControler.gain_zoom(1.2))
        
        if magic_color:
            self.paramControler.automatic_color(cmap_name = 'jet')
        if magic_scale:
            self.paramControler.automatic_gain_offset(gain_adaptated = False, apply_for_selection = False)
        
        # Create curve items
        self.analogsignal_curves = [ ]
        # signal sharing same size sampling and t_start are in the same familly
        self.times_familly = { }
        for i,anasig in enumerate(analogsignals):
            key = (float(anasig.t_start.rescale('s').magnitude), float(anasig.sampling_rate.rescale('Hz').magnitude), anasig.size)
            if  key in self.times_familly:
                self.times_familly[key].append(i)
            else:
                self.times_familly[key] = [ i ]
            color = anasig.annotations.get('color', None)
            if color is not None:
                self.paramSignals.children()[i].param('color').setValue(color)
            else:
                color = self.paramSignals.children()[i].param('color').value()
            curve = self.plot.plot([np.nan], [np.nan], pen = color)
            self.analogsignal_curves.append(curve)
        
        self.paramSignals.sigTreeStateChanged.connect(self.refreshColors)
        self.proxy = pg.SignalProxy(self.allParams.sigTreeStateChanged, rateLimit=5, delay=0.1, slot=lambda : self.refresh(fast = False))

    
    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()
    
    def refreshColors(self):
        for i,anasig in enumerate(self.analogsignals):
            p = self.paramSignals.children()[i]
            #~ pen = pg.mkPen(color = p.param('color').value(),  width = p.param('width').value())
            pen = pg.mkPen(color = p.param('color').value())
            self.analogsignal_curves[i].setPen(pen)
    
    def refresh(self, fast = False):
        """
        When fast it do decimate.
        """
        t1 = time.time()
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
                p = self.paramSignals.children()[c]
                if not p.param('visible').value():
                    curve.setData([np.nan], [np.nan])
                    continue
                ana = self.analogsignals[c]
                chunk = ana.magnitude[sl]
                
                if chunk.size==0:
                    curve.setData([np.nan], [np.nan])
                else:
                    g = p.param('gain').value()
                    o = p.param('offset').value()
                    curve.setData(t_vect, chunk*g+o)
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        ylims  = self.paramGlobal.param('ylims').value()
        self.plot.setYRange( *ylims )
        
        self.is_refreshing = False




class SignalViewerControler(QWidget):
    def __init__(self, parent = None, viewer = None):
        super(SignalViewerControler, self).__init__(parent)
        
        self.viewer = viewer

        #layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = u'Options for AnalogSignals'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.treeParamSignal = pg.parametertree.ParameterTree()
        self.treeParamSignal.header().hide()
        h.addWidget(self.treeParamSignal)
        self.treeParamSignal.setParameters(self.viewer.paramSignals, showTop=True)
        
        if len(self.viewer.analogsignals)>1:
            self.multi = MultiChannelParam( all_params = self.viewer.paramSignals, param_by_channel = param_by_channel)
            h.addWidget(self.multi)
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.treeParamGlobal = pg.parametertree.ParameterTree()
        self.treeParamGlobal.header().hide()
        v.addWidget(self.treeParamGlobal)
        self.treeParamGlobal.setParameters(self.viewer.paramGlobal, showTop=True)

        # Gain and offset
        v.addWidget(QLabel(u'<b>Automatic gain and offset:<\b>'))
        but = QPushButton('Real scale (gain = 1, offset = 0)')
        but.clicked.connect(self.center_all)
        v.addWidget(but)        
        for apply_for_selection, labels in enumerate([[ 'fake scale (all  + same gain)', 'fake scale (all)'],
                                                            ['fake scale (selection  + same gain)', 'fake scale (selection)' ]] ):
            for gain_adaptated, label in enumerate(labels):
                but = QPushButton(label)
                but.gain_adaptated  = gain_adaptated
                but.apply_for_selection  = apply_for_selection
                but.clicked.connect(self.automatic_gain_offset)
                v.addWidget(but)

        v.addWidget(QLabel(self.tr('<b>Automatic color:<\b>'),self))
        but = QPushButton('Progressive')
        but.clicked.connect(lambda : self.automatic_color(cmap_name = None))
        v.addWidget(but)

        v.addWidget(QLabel(self.tr('<b>Gain zoom (mouse wheel on graph):<\b>'),self))
        h = QHBoxLayout()
        v.addLayout(h)
        but = QPushButton('-')
        but.clicked.connect(lambda : self.gain_zoom(1.2))
        h.addWidget(but)
        but = QPushButton('+')
        but.clicked.connect(lambda : self.gain_zoom(.8))
        h.addWidget(but)
        

    def center_all(self):
        ylims = [np.min(self.viewer.all_min), np.max(self.viewer.all_max) ]
        self.viewer.paramGlobal.param('ylims').setValue(ylims)
        for p in self.viewer.paramSignals.children():
            p.param('gain').setValue(1)
            p.param('offset').setValue(0)
            p.param('visible').setValue(True)
    
    def automatic_gain_offset(self, gain_adaptated = None, apply_for_selection = None):
        if gain_adaptated is None:
            gain_adaptated = self.sender().gain_adaptated
        if apply_for_selection is None:
            apply_for_selection = self.sender().apply_for_selection
        
        nsig = len(self.viewer.analogsignals)
        gains = np.zeros(nsig, dtype = float)
        
        if apply_for_selection :
            selected =  np.zeros(nsig, dtype = bool)
            selected[self.multi.selectedRows()] = True
            if not selected.any(): return
        else:
            selected =  np.ones(nsig, dtype = bool)
        
        n = np.sum(selected)
        ylims  = [-.5, nsig-.5 ]
        self.viewer.paramGlobal.param('ylims').setValue(ylims)
        
        dy = np.diff(ylims)[0]/(n)
        gains = np.zeros(self.viewer.all_std.size, dtype = float)
        if gain_adaptated:
            gains = dy/n/self.viewer.all_std
        else:
            gains = np.ones(self.viewer.all_std.size, dtype = float) * dy/n/max(self.viewer.all_std[selected])
        gains *= .3
        
        #~ o = .5
        o = n-.5
        for i, p in enumerate(self.viewer.paramSignals.children()):
            p.param('visible').setValue(selected[i])
            if selected[i]:
                p.param('gain').setValue(gains[i]*2)
                p.param('offset').setValue(dy*o+ylims[0])
                #~ o+=1
                o-=1
    
    def automatic_color(self, cmap_name = None):
        if cmap_name is None:
            cmap_name = 'jet'
        nsig = len(self.viewer.analogsignals)
        cmap = get_cmap(cmap_name , nsig)
        for i, p in enumerate(self.viewer.paramSignals.children()):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            p.param('color').setValue(color)
    
    def gain_zoom(self, factor):
        for i, p in enumerate(self.viewer.paramSignals.children()):
            p.param('gain').setValue(p.param('gain').value()*factor)
            