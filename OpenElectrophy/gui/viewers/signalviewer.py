# -*- coding: utf-8 -*-
"""
Signal viewers
"""


from .tools import *
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
    doubleclicked = pyqtSignal()
    #~ zoom_in = pyqtSignal()
    #~ zoom_out = pyqtSignal()
    #~ fast_zoom_in = pyqtSignal()
    #~ fast_zoom_out = pyqtSignal()
    zoom = pyqtSignal(float)
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
    def mouseClickEvent(self, ev):
        self.clicked.emit()
        ev.accept()
    def mouseDoubleClickEvent(self, ev):
        self.doubleclicked.emit()
        ev.accept()
    def mouseDragEvent(self, ev):
        ev.ignore()
    def wheelEvent(self, ev):
        if ev.modifiers() ==  Qt.ControlModifier:
            z = 10 if ev.delta()>0 else 1/10.
        else:
            z = 1.3 if ev.delta()>0 else 1/1.3
        self.zoom.emit(z)
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
        self.viewBox.doubleclicked.connect(self.open_configure_dialog)
        
        self.graphicsview  = pg.GraphicsView()#useOpenGL = True)
        self.mainlayout.addWidget(self.graphicsview)
        
        self.plot = pg.PlotItem(viewBox = self.viewBox)
        self.plot.hideButtons()
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

    def set_params(self, **kargs):
        pglobal = [ p['name'] for p in param_global]
        pchan = [ p['name']+'s' for p in param_by_channel]
        nb_channel = len(self.analogsignals)
        for k, v in kargs.items():
            if k in pglobal:
                self.paramGlobal.param(k).setValue(v)
            elif k in pchan:
                for channel in range(nb_channel):
                    p  = self.paramSignals.children()[channel]
                    p.param(k[:-1]).setValue(v[channel])
        
    def get_params(self):
        nb_channel = len(self.analogsignals)
        params = { }
        for p in param_global:
            v = self.paramGlobal[p['name']]
            if 'color' in p['name']:
                v = str(v.name())
            params[p['name']] = v
        for p in param_by_channel:
            values = [ ]
            for channel in range(nb_channel):
                v= self.paramSignals.children()[channel][p['name']]
                if 'color' in p['name']:
                    v = str(v.name())
                values.append(v)
            params[p['name']+'s'] = values
        return params    

    
    def clear_all(self):
        self.plot.clear()
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = 'g')
        self.plot.addItem(self.vline)
        self.spikeonsignal_curves = [ ]
        self.analogsignal_curves = [ ]
        

    def set_analosignals(self, analogsignals, magic_color = True, magic_scale = True):
        self.analogsignals = analogsignals
        
        # pre compute std and max
        self.autoestimate_scales()
        
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
        
        #~ self.paramControler = SignalViewerControler(viewer = self)
        self.paramControler = SignalViewerControler(parent = self)
        self.paramControler.setWindowFlags(Qt.Window)
        self.viewBox.zoom.connect(self.gain_zoom)
        
        if magic_color:
            self.automatic_color(cmap_name = 'jet')
        if magic_scale:
            self.auto_gain_and_offset(mode = 2)
            #~ self.automatic_gain_offset(gain_adaptated = False, apply_for_selection = False)
        
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
        
        #~ self.paramSignals.sigTreeStateChanged.connect(self.refreshColors)
        #~ self.all_param_color = []
        #~ for i, p in enumerate(self.paramSignals.children()):
            #~ self.all_param_color.append(p.param('color'))
            #~ p.param('color').sigValueChanged.connect(self.refreshColors)
        
        #~ self.proxy = pg.SignalProxy(self.allParams.sigTreeStateChanged, rateLimit=5, delay=0.1, slot=lambda : self.refresh(fast = False))
        self.allParams.sigTreeStateChanged.connect(self.on_param_change)

    
    def open_configure_dialog(self):
        self.paramControler.show()
        self.paramControler.activateWindow()

    def on_param_change(self, params, changes):
        for param, change, data in changes:
            if change != 'value': continue
            
            if param.name() =='color':
                i = self.paramSignals.children().index(param.parent())
                pen = pg.mkPen(color = param.value())
                self.analogsignal_curves[i].setPen(pen)
            else:
                pass
        self.delayed_refresh()
    
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
                    if chunk.ndim==2:
                        chunk = chunk[:, 0]
                    curve.setData(t_vect, (chunk*g+o))
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        ylims  = self.paramGlobal.param('ylims').value()
        self.plot.setYRange( *ylims )
        
        self.is_refreshing = False

    #
    def autoestimate_scales(self):
        maxpoint = 10000
        #~ self.all_mean = np.array([ np.mean(anasig.magnitude[:maxpoint]) for anasig in self.analogsignals ])
        self.all_mean = np.array([ np.median(anasig.magnitude[:maxpoint]) for anasig in self.analogsignals ])
        self.all_std = np.array([ np.std(anasig.magnitude[:maxpoint]) for anasig in self.analogsignals ])
        self.all_max = np.array([ np.max(anasig.magnitude[:maxpoint]) for anasig in self.analogsignals ])
        self.all_min = np.array([ np.min(anasig.magnitude[:maxpoint]) for anasig in self.analogsignals ])
        return self.all_mean, self.all_std

    
    def auto_gain_and_offset(self, mode = 0, selected = None):
        """
        mode = 0, 1, 2
        """
        nb_channel = len(self.analogsignals)
        if selected is None:
            selected = np.ones(nb_channel, dtype = bool)
        
        n = np.sum(selected)
        if n==0: return
        
        av, sd = self.autoestimate_scales()
        if av is None: return
        
        if mode==0:
            ylims = [np.min(av[selected]-3*sd[selected]), np.max(av[selected]+3*sd[selected]) ]
            gains = np.ones(nb_channel, dtype = float)
            offsets = np.zeros(nb_channel, dtype = float)
        elif mode in [1, 2]:
            ylims  = [-.5, n-.5 ]
            gains = np.ones(nb_channel, dtype = float)
            if mode==1 and max(sd[selected])!=0:
                gains = np.ones(nb_channel, dtype = float) * 1./(6.*max(sd[selected]))
            elif mode==2 :
                gains[sd!=0] = 1./(6.*sd[sd!=0])
            offsets = np.zeros(nb_channel, dtype = float)
            offsets[selected] = range(n)[::-1] - av[selected]*gains[selected]
        
        # apply
        self.set_params(gains = gains, offsets = offsets, visibles = selected,
                                        ylims = ylims)

    def automatic_color(self, cmap_name = None, selected = None):
        nb_channel = len(self.analogsignals)
        if selected is None:
            selected = np.ones(nb_channel, dtype = bool)
        
        if cmap_name is None:
            cmap_name = 'jet'
        n = np.sum(selected)
        if n==0: return
        cmap = get_cmap(cmap_name , n)
        colors = self.get_params()['colors']
        s=0
        for i in range(nb_channel):
            if selected[i]:
                colors[i] = [ int(c*255) for c in ColorConverter().to_rgb(cmap(s)) ]
                s += 1
        self.set_params(colors = colors)
        
    def gain_zoom(self, factor):
        for i, p in enumerate(self.paramSignals.children()):
            if self.all_mean is not None:
                p['offset'] = p['offset'] + self.all_mean[i]*p['gain'] - self.all_mean[i]*p['gain']*factor
            p['gain'] = p['gain']*factor
    




class SignalViewerControler(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        
        self.viewer = parent

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
        
        nb_channel = len(self.viewer.analogsignals)
        if nb_channel>1:
            self.multi = MultiChannelParam( all_params = self.viewer.paramSignals, param_by_channel = param_by_channel)
            h.addWidget(self.multi)
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.treeParamGlobal = pg.parametertree.ParameterTree()
        self.treeParamGlobal.header().hide()
        v.addWidget(self.treeParamGlobal)
        self.treeParamGlobal.setParameters(self.viewer.paramGlobal, showTop=True)

        # Gain and offset
        v.addWidget(QLabel(u'<b>Automatic gain and offset on selection:<\b>'))
        for i,text in enumerate(['Real scale (gain = 1, offset = 0)',
                            'Fake scale (same gain for all)',
                            'Fake scale (gain per channel)',]):
            but = QPushButton(text)
            v.addWidget(but)
            but.mode = i
            but.clicked.connect(self.on_auto_gain_and_offset)

        v.addWidget(QLabel(self.tr('<b>Automatic color on selection:<\b>'),self))
        h = QHBoxLayout()
        but = QPushButton('Progressive')
        but.clicked.connect(self.on_automatic_color)
        h.addWidget(but,4)
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems(['jet', 'prism', 'spring', 'spectral', 'hsv', 'autumn', 'spring', 'summer', 'winter', 'bone'])
        h.addWidget(self.combo_cmap,1)
        v.addLayout(h)

        v.addWidget(QLabel(self.tr('<b>Gain zoom (mouse wheel on graph):<\b>'),self))
        h = QHBoxLayout()
        v.addLayout(h)
        for label, factor in [ ('--', 1./10.), ('-', 1./1.3), ('+', 1.3), ('++', 10.),]:
            but = QPushButton(label)
            but.factor = factor
            but.clicked.connect(self.on_gain_zoom)
            h.addWidget(but)
    
    def on_auto_gain_and_offset(self):
        mode = self.sender().mode
        nb_channel = len(self.viewer.analogsignals)
        if nb_channel>1:
            selected = self.multi.selected()
        else:
            selected = np.ones(1, dtype = bool)
        self.viewer.auto_gain_and_offset(mode = mode, selected = selected)
    
    def on_automatic_color(self, cmap_name = None):
        cmap_name = str(self.combo_cmap.currentText())
        nb_channel = len(self.viewer.analogsignals)
        if nb_channel>1:
            selected = self.multi.selected()
        else:
            selected = np.ones(1, dtype = bool)
        self.viewer.automatic_color(cmap_name = cmap_name, selected = selected)
            
    def on_gain_zoom(self):
        factor = self.sender().factor
        self.viewer.gain_zoom(factor)


    
