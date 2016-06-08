# -*- coding: utf-8 -*-
"""
TimeFreqViewer
"""

from .tools import *

from scipy import fftpack
#~ import numpy.fft as fftpack

import time

import pyqtgraph as pg

from .multichannelparam import MultiChannelParam
from ...timefrequency import generate_wavelet_fourier

from matplotlib import cm 
from matplotlib.colors import ColorConverter


param_global = [
    {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1, 'limits' : (.1, 60)},
    {'name': 'nb_column', 'type': 'int', 'value': 1},
    {'name': 'background_color', 'type': 'color', 'value': 'k' },
    {'name': 'colormap', 'type': 'list', 'value': 'jet', 'values' : ['jet', 'gray', 'bone', 'cool', 'hot', ] },
    
    ]

param_timefreq = [ 
    {'name': 'f_start', 'type': 'float', 'value': 3., 'step': 1.},
    {'name': 'f_stop', 'type': 'float', 'value': 90., 'step': 1.},
    {'name': 'deltafreq', 'type': 'float', 'value': 3., 'step': 1.,  'limits' : (0.001, 1.e6)},
    {'name': 'f0', 'type': 'float', 'value': 2.5, 'step': 0.1},
    {'name': 'normalisation', 'type': 'float', 'value': 0., 'step': 0.1},
    ]

param_by_channel = [ 
                #~ {'name': 'channel_name', 'type': 'str', 'value': '','readonly' : True},
                #~ {'name': 'channel_index', 'type': 'str', 'value': '','readonly' : True},
                {'name': 'visible', 'type': 'bool', 'value': True},
                {'name': 'clim', 'type': 'float', 'value': 10.},
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


class MyGraphicsView(pg.GraphicsView):
    clicked = pyqtSignal()
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()    
    def __init__(self, *args, **kwds):
        pg.GraphicsView.__init__(self, *args, **kwds)
    def mousePressEvent(self, ev):
        QGraphicsView.mousePressEvent(self, ev)
        self.clicked.emit()
    def wheelEvent(self, ev):
        if ev.delta()>0:
            self.zoom_in.emit()
        else:
            self.zoom_out.emit()
        ev.accept()

class TimeFreqViewer(ViewerBase):
    """
    This is a time frequancy viewer based on morlet continuous wavelet tranform.
    
    All analogsignals need to have same asmpling_rate.
    
    """
    initialize_tfr_finished = pyqtSignal()
    def __init__(self, parent = None,
                            analogsignals = None,
                            with_time_seeker = False,
                            max_visible_on_open = 16,
                            **kargs
                            ):
                            
        super(TimeFreqViewer,self).__init__(parent)
    
        self.analogsignals = analogsignals

        self.global_sampling_rate = self.analogsignals[0].sampling_rate.rescale('Hz').magnitude
        for i, anasig in enumerate(self.analogsignals):
            assert(anasig.sampling_rate.rescale('Hz').magnitude==self.global_sampling_rate)
        n = len(analogsignals)
        
        
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)

        self.grid = QGridLayout()
        mainlayout.addLayout(self.grid)
        
        #~ nb_column = np.rint(np.sqrt(n))
        nb_column = np.rint(np.sqrt(max_visible_on_open))
        
        
        # Create parameters
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children =param_global)
        self.paramGlobal.param('nb_column').setValue(nb_column)
        
        self.paramTimeFreq = pg.parametertree.Parameter.create( name='Time frequency options', 
                                                    type='group', children = param_timefreq)

        all = [ ]
        for i, ana in enumerate(self.analogsignals):
            if 'channel_index' in ana.annotations:
                name = 'AnalogSignal {} name={} channel_index={}'.format(i, ana.name, ana.annotations['channel_index'])
            else:
                name = 'AnalogSignal {} name={}'.format(i, ana.name)
            all.append({ 'name': name, 'type' : 'group', 'children' : param_by_channel})
        self.paramSignals = pg.parametertree.Parameter.create(name='AnalogSignals', type='group', children=all)
        for p in self.paramSignals.children()[max_visible_on_open:]:
            p.param('visible').setValue(False)
        
        
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', 
                                                        children = [self.paramGlobal,self.paramSignals, self.paramTimeFreq  ])
        
        self.paramControler = TimefreqViewerControler(viewer = self)
        
        self.set_params(**kargs)
        
        self.graphicsviews = [ ]
        #~ self.grid_changing =False
        self.grid_changing =0
        self.create_grid()
        
        self.thread_initialize_tfr = None
        self.need_recreate_thread = True
        
        self.initialize_time_freq(threaded = False)
        self.initialize_tfr_finished.connect(self.refresh)
        
        # this signal is used when trying to change many time tfr params
        self.timer_back_initialize = QTimer(singleShot = True, interval = 300)
        self.timer_back_initialize.timeout.connect(self.initialize_time_freq)
        
        # this signal is a hack when many signal are emited at the same time
        # only the first is taken
        self.need_change_grid.connect(self.do_change_grid, type = Qt.QueuedConnection)
        #~ proxy = pg.SignalProxy(self.need_change_grid, delay=0.2, slot=self.do_change_grid)
        
        self.paramGlobal.sigTreeStateChanged.connect(self.on_param_change)
        self.paramTimeFreq.sigTreeStateChanged.connect(self.initialize_time_freq)
        for p in self.paramSignals.children():
            p.param('visible').sigValueChanged.connect(self.change_grid)
            p.param('clim').sigValueChanged.connect(self.clim_changed)        
        
        #~ self.paramGlobal.param('xsize').sigValueChanged.connect(self.initialize_time_freq)
        #~ self.paramGlobal.param('nb_column').sigValueChanged.connect(self.change_grid)
        #~ self.paramGlobal.param('colormap').sigValueChanged.connect(self.initialize_time_freq)
        #~ self.paramTimeFreq.sigTreeStateChanged.connect(self.initialize_time_freq)
        #~ for p in self.paramSignals.children():
            #~ p.param('visible').sigValueChanged.connect(self.change_grid)
            #~ p.param('clim').sigValueChanged.connect(self.clim_changed)

        if with_time_seeker:
            self.timeseeker = TimeSeeker()
            mainlayout.addWidget(self.timeseeker)
            self.timeseeker.set_start_stop(*find_best_start_stop(analogsignals =analogsignals))
            self.timeseeker.seek(analogsignals[0].t_start.magnitude)
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
        ptimefreq = [ p['name'] for p in param_timefreq]
        
        nb_channel = len(self.analogsignals)
        for k, v in kargs.items():
            if k in pglobal:
                self.paramGlobal.param(k).setValue(v)
            elif k in pchan:
                for channel in range(nb_channel):
                    p  = self.paramSignals.children()[channel]
                    p.param(k[:-1]).setValue(v[channel])
            elif k in ptimefreq:
                self.paramTimeFreq.param(k).setValue(v)
        
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
        for p in param_timefreq:
            v = self.paramTimeFreq[p['name']]
            #~ if 'color' in p['name']:
                #~ v = str(v.name())
            params[p['name']] = v
        
        return params

    def on_param_change(self, params, changes):
        for param, change, data in changes:
            if change != 'value': continue
            if param.name()=='background_color':
                color = data
                for graphicsview in self.graphicsviews:
                    if graphicsview is not None:
                        graphicsview.setBackground(color)
            if param.name()=='xsize':
                self.initialize_time_freq()
            if param.name()=='colormap':
                self.initialize_time_freq()
            if param.name()=='nb_column':
                self.change_grid(None)
            #~ if param.name()=='refresh_interval':
                #~ self.timer.setInterval(data)
    
    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()
    
    
    need_change_grid = pyqtSignal()
    def change_grid(self, param=None):
        #~ print 'change_grid', self.grid_changing
        #~ if not self.grid_changing:
            #~ self.grid_changing = True
            #~ self.need_change_grid.emit()
        self.grid_changing += 1
        if self.grid_changing==1:
            self.need_change_grid.emit()
            #~ print 'emit'
            #~ pass
        
    def do_change_grid(self):
        #~ print 'do_change_grid'
        time.sleep(.2)
        self.grid_changing = 0
        self.create_grid()
        self.initialize_plots()
        #~ self.initialize_time_freq()
        #~ self.initialize_tfr_finished.connect(self.grid_changed_done)
        
    def grid_changed_done(self):
        #~ print 'grid_changed_done'
        self.initialize_tfr_finished.disconnect(self.grid_changed_done)
        #~ self.grid_changing = False
        
    def clim_changed(self, param):
        i = self.paramSignals.children().index( param.parent())
        clim = param.value()
        if self.images[i] is not None:
            self.images[i].setImage(self.maps[i], lut = self.jet_lut, levels = [0,clim])
        
        
    def create_grid(self):
        #~ print 'create_grid'
        color = self.paramGlobal.param('background_color').value()
        #~ self.graphicsview.setBackground(color)

        n = len(self.analogsignals)
        for graphicsview in self.graphicsviews:
            if graphicsview is not None:
                graphicsview.hide()
                self.grid.removeWidget(graphicsview)
        self.plots =  [ None for i in range(n)]
        self.graphicsviews =  [ None for i in range(n)]
        r,c = 0,0
        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals.children()[i].param('visible').value(): continue

            viewBox = MyViewBox()
            viewBox.clicked.connect(self.open_configure_dialog)
            viewBox.zoom_in.connect(lambda : self.paramControler.clim_zoom(1.2))
            viewBox.zoom_out.connect(lambda : self.paramControler.clim_zoom(.8))
            
            graphicsview  = pg.GraphicsView()#useOpenGL = True)
            graphicsview.setBackground(color)
            plot = pg.PlotItem(viewBox = viewBox)
            plot.hideButtons()
            graphicsview.setCentralItem(plot)
            self.graphicsviews[i] = graphicsview
            
            self.plots[i] = plot
            self.grid.addWidget(graphicsview, r,c)
            
            c+=1
            if c==self.paramGlobal.param('nb_column').value():
                c=0
                r+=1
        self.images = [ None for i in range(n)]
        self.maps = [ None for i in range(n)]
        self.is_computing = np.zeros((n), dtype = bool)
        self.threads = [ None for i in range(n)]
        
    
    def initialize_time_freq(self, threaded = True):
        #~ print 'initialize_time_freq', threaded
        if threaded:
            if self.thread_initialize_tfr is not None or self.is_computing.any():
                # needd to come back later ...
                if not self.timer_back_initialize.isActive():
                    self.timer_back_initialize.start()
                return
        
        # create self.params_time_freq
        p = self.params_time_freq = { }
        for param in self.paramTimeFreq.children():
            self.params_time_freq[param.name()] = param.value()
        
        
        # we take sampling_rate = f_stop*4 or (original sampling_rate)
        if p['f_stop']*4 < self.global_sampling_rate:
            p['sampling_rate'] = p['f_stop']*4
        else:
            p['sampling_rate']  = self.global_sampling_rate
        self.factor = p['sampling_rate']/self.global_sampling_rate # this compensate unddersampling in FFT.
        
        self.xsize2 = self.xsize
        self.len_wavelet = int(self.xsize2*p['sampling_rate'])
        self.win = fftpack.ifftshift(np.hamming(self.len_wavelet))
        
        if threaded:
            self.thread_initialize_tfr = ThreadInitializeWavelet(len_wavelet = self.len_wavelet, 
                                                                params_time_freq = p, parent = self )
            self.thread_initialize_tfr.finished.connect(self.initialize_tfr_done)
            self.thread_initialize_tfr.start()
        else:
            self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq)
            self.initialize_plots()
        
    
    def initialize_tfr_done(self):
        #~ print 'initialize_tfr_done'
        
        self.wf = self.thread_initialize_tfr.wf
        
        self.initialize_plots()
        
        self.thread_initialize_tfr = None
        self.initialize_tfr_finished.emit()
    
    def initialize_plots(self):
        #~ print 'initialize_plots'
        colormap = self.paramGlobal.param('colormap').value()
        lut = [ ]
        cmap = cm.get_cmap(colormap , 10000)
        for i in range(10000):
            r,g,b =  ColorConverter().to_rgb(cmap(i) )
            lut.append([r*255,g*255,b*255])
        self.jet_lut = np.array(lut, dtype = np.uint8)
        
        p = self.params_time_freq
        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals.children()[i].param('visible').value(): continue
            plot = self.plots[i]
            self.maps[i] = np.zeros(self.wf.shape)
            if self.images[i] is not None:# for what ???
                plot.removeItem(self.images[i])# for what ???
            image = pg.ImageItem()
            plot.addItem(image)
            plot.setYRange(p['f_start'], p['f_stop'])
            self.images[i] =image
            clim = self.paramSignals.children()[i].param('clim').value()
            self.images[i].setImage(self.maps[i], lut = self.jet_lut, levels = [0,clim])
            
            self.t_start, self.t_stop = self.t-self.xsize2/3. , self.t+self.xsize2*2./3.
            f_start, f_stop = p['f_start'], p['f_stop']
            image.setRect(QRectF(self.t_start, f_start,self.xsize, f_stop-f_start))
        
        self.sig_chunk_size = int(np.rint(self.xsize2*self.global_sampling_rate))
        self.empty_sigs = [np.zeros(self.sig_chunk_size, dtype = ana.dtype) for ana in self.analogsignals]
        
        self.freqs = np.arange(p['f_start'],p['f_stop'],p['deltafreq'])
        self.need_recreate_thread = True
    
    
    
    def refresh(self, fast = False):
        if self.thread_initialize_tfr is not None or self.is_computing.any():
            self.is_refreshing = False
            return
        if self.timer_back_initialize.isActive():
            self.is_refreshing = False
            return
        
        self.t_start, self.t_stop = self.t-self.xsize2/3. , self.t+self.xsize2*2./3.

        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals.children()[i].param('visible').value(): continue
            if self.need_recreate_thread:
                    self.threads[i] = ThreadComputeTF(None, self.wf, self.win,i, self.factor, parent = self)
                    self.threads[i].finished.connect(self.map_computed)
            self.is_computing[i] = True
            sl = get_analogsignal_slice(anasig,self.t_start*pq.s, self.t_stop*pq.s,
                                                return_t_vect = False,clip = True)
            chunk = anasig.magnitude[sl]
            if np.abs(chunk.size-self.sig_chunk_size)>=1.:
                sl2 = get_analogsignal_slice(anasig,self.t_start*pq.s, self.t_stop*pq.s,
                                                return_t_vect = False, clip = False)                
                chunk2 = self.empty_sigs[i]
                chunk2[:]=0
                i1 = -sl2.start if sl2.start<0 else 0
                i2 = i1+chunk.size
                if chunk.ndim==2:
                    chunk = chunk[:, 0]
                chunk2[i1:i2] = chunk
                chunk = chunk2
            self.threads[i].sig = chunk
            
            #~ self.vline.setPos(self.t)
            self.plots[i].setXRange( self.t_start, self.t_stop)
            
            f_start, f_stop = self.params_time_freq['f_start'], self.params_time_freq['f_stop']
            self.images[i].setRect(QRectF(self.t_start, f_start,self.xsize2, f_stop-f_start))
            self.threads[i].start()
        
        self.need_recreate_thread = False
        self.is_refreshing = False

    def map_computed(self, i):
        if self.sender() is not self.threads[i]:# thread have changes
            self.is_computing[i] = False
            return
        if not self.grid_changing and self.thread_initialize_tfr is None:
            if self.images[i] is not None:
                self.images[i].updateImage(self.maps[i])
        self.is_computing[i] = False


class ThreadComputeTF(QThread):
    finished = pyqtSignal(int)
    def __init__(self, sig, wf, win,n, factor, parent = None, ):
        super(ThreadComputeTF, self).__init__(parent)
        self.sig = sig
        self.wf = wf
        self.win = win
        self.n = n
        self.factor = factor # this compensate subsampling
        
    def run(self):
        #~ print 'run', self.n, self.wf.shape, self.sig.shape
        t1 = time.time()
        sigf=fftpack.fft(self.sig)
        n = self.wf.shape[0]
        sigf = np.concatenate([sigf[0:(n+1)/2],  sigf[-(n-1)/2:]])*self.factor
        #~ sigf *= self.win
        wt_tmp=fftpack.ifft(sigf[:,np.newaxis]*self.wf,axis=0)
        wt = fftpack.fftshift(wt_tmp,axes=[0])
        
        self.parent().maps[self.n] = np.abs(wt)
        t2 = time.time()
        #~ print 'run', self.n, self.wf.shape, self.sig.shape, t2-t1
        self.finished.emit(self.n)

class ThreadInitializeWavelet(QThread):
    finished = pyqtSignal()
    def __init__(self, len_wavelet = None, params_time_freq = {}, parent = None, ):
        super(ThreadInitializeWavelet, self).__init__(parent)
        self.len_wavelet = len_wavelet
        self.params_time_freq = params_time_freq
        
    def run(self):
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq)
        self.finished.emit()
        


class TimefreqViewerControler(QWidget):
    def __init__(self, parent = None, viewer = None):
        super(TimefreqViewerControler, self).__init__(parent)

        self.viewer = viewer

        #layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = u'Options for AnalogSignals'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)

        v = QVBoxLayout()
        h.addLayout(v)
        
        self.treeParamGlobal = pg.parametertree.ParameterTree()
        self.treeParamGlobal.header().hide()
        v.addWidget(self.treeParamGlobal)
        self.treeParamGlobal.setParameters(self.viewer.paramGlobal, showTop=True)
        
        self.treeParamTimeFreq = pg.parametertree.ParameterTree()
        self.treeParamTimeFreq.header().hide()
        v.addWidget(self.treeParamTimeFreq)
        self.treeParamTimeFreq.setParameters(self.viewer.paramTimeFreq, showTop=True)
        
        v.addWidget(QLabel(self.tr('<b>Automatic color scale:<\b>'),self))
        but = QPushButton('Identic')
        but.clicked.connect(lambda: self.auto_clim( identic = True))
        v.addWidget(but)
        but = QPushButton('Independent')
        but.clicked.connect(lambda: self.auto_clim( identic = False))
        v.addWidget(but)
        
        h2 = QHBoxLayout()
        v.addLayout(h2)
        but = QPushButton('-')
        but.clicked.connect(lambda : self.clim_zoom(.8))
        h2.addWidget(but)
        but = QPushButton('+')
        but.clicked.connect(lambda : self.clim_zoom(1.2))
        h2.addWidget(but)        
        
        self.treeParamSignal = pg.parametertree.ParameterTree()
        self.treeParamSignal.header().hide()
        h.addWidget(self.treeParamSignal)
        self.treeParamSignal.setParameters(self.viewer.paramSignals, showTop=True)
        
        if len(self.viewer.analogsignals)>1:
            self.multi = MultiChannelParam( all_params = self.viewer.paramSignals, param_by_channel = param_by_channel)
            h.addWidget(self.multi)

    def auto_clim(self, identic = True):
        
        if identic:
            all = [ ]
            for i, p in enumerate(self.viewer.paramSignals.children()):
                if p.param('visible').value():
                    all.append(np.max(self.viewer.maps[i]))
            clim = np.max(all)*1.1
            for i, p in enumerate(self.viewer.paramSignals.children()):
                if p.param('visible').value():
                    p.param('clim').setValue(clim)
        else:
            for i, p in enumerate(self.viewer.paramSignals.children()):
                if p.param('visible').value():
                    clim = np.max(self.viewer.maps[i])*1.1
                    p.param('clim').setValue(clim)
    
    def clim_zoom(self, factor):
        for i, p in enumerate(self.viewer.paramSignals.children()):
            p.param('clim').setValue(p.param('clim').value()*factor)
