# -*- coding: utf-8 -*-
"""
TimeFreqViewer
"""

from tools import *

#~ from scipy import fftpack
import numpy.fft as fftpack

import time

import pyqtgraph as pg

from .multichannelparam import MultiChannelParam
from ...timefrequency import generate_wavelet_fourier

from matplotlib import cm 
from matplotlib.colors import ColorConverter
lut = [ ]
cmap = cm.get_cmap('jet' , 10000)
for i in range(10000):
    r,g,b =  ColorConverter().to_rgb(cmap(i) )
    lut.append([r*255,g*255,b*255])
jet_lut = np.array(lut, dtype = np.uint8)


param_global = [
    {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1, 'limits' : (.1, 60)},
    {'name': 'nb_column', 'type': 'int', 'value': 1},
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
    def __init__(self, parent = None,
                            analogsignals = None,
                            with_time_seeker = False,
                            ):
                            
        super(TimeFreqViewer,self).__init__(parent)
    
        self.analogsignals = analogsignals

        self.global_sampling_rate = self.analogsignals[0].sampling_rate.magnitude
        for i, anasig in enumerate(self.analogsignals):
            assert(anasig.sampling_rate==self.global_sampling_rate)
        n = len(analogsignals)
        
        
        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)

        self.grid = QGridLayout()
        mainlayout.addLayout(self.grid)
        
        nb_column = np.rint(np.sqrt(n))
        
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
        
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', 
                                                        children = [self.paramGlobal,self.paramSignals, self.paramTimeFreq  ])
        
        self.paramControler = TimefreqViewerControler(viewer = self)
        
        self.graphicsviews = [ ]
        self.grid_changing =QReadWriteLock()
        self.create_grid()
        
        self.need_recreate_thread = True
        self.initialize_time_freq()
        
        # this signal is a hack when many signal are emited at the same time
        # only the first is taken
        self.need_change_grid.connect(self.do_change_grid, type = Qt.QueuedConnection)
        
        self.paramGlobal.param('xsize').sigValueChanged.connect(self.initialize_time_freq_and_refresh)
        self.paramGlobal.param('nb_column').sigValueChanged.connect(self.change_grid)
        self.paramTimeFreq.sigTreeStateChanged.connect(self.initialize_time_freq_and_refresh)
        for p in self.paramSignals.children():
            p.param('visible').sigValueChanged.connect(self.change_grid)
            p.param('clim').sigValueChanged.connect(self.clim_changed)

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
    
    
    need_change_grid = pyqtSignal()
    def change_grid(self, param):
        if  self.grid_changing.tryLockForWrite():
            self.need_change_grid.emit()
    def do_change_grid(self):
        self.create_grid()
        self.initialize_time_freq()
        self.refresh()
        self.grid_changing.unlock()
    def initialize_time_freq_and_refresh(self):
        self.initialize_time_freq()
        self.refresh()
        
    def clim_changed(self, param):
        i = self.paramSignals.children().index( param.parent())
        clim = param.value()
        self.images[i].setImage(self.maps[i], lut = jet_lut, levels = [0,clim])
        
    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()
        
    def create_grid(self):
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
            plot = pg.PlotItem(viewBox = viewBox)
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
        
    
    def initialize_time_freq(self):
        # create self.params_time_freq
        p = self.params_time_freq = { }
        for param in self.paramTimeFreq.children():
            self.params_time_freq[param.name()] = param.value()
        
        # we take sampling_rate = f_stop*4 or (original sampling_rate)
        if p['f_stop']*4 < self.global_sampling_rate:
            p['sampling_rate'] = p['f_stop']*4
        else:
            p['sampling_rate']  = self.global_sampling_rate
        self.factor = p['sampling_rate']/self.global_sampling_rate # this compenate unddersampling in FFT.
        
        self.len_wavelet = int(self.xsize*p['sampling_rate'])
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq)#[:,::-1]# reversed for plotting
        self.win = fftpack.ifftshift(np.hamming(self.len_wavelet))
        
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
            self.images[i].setImage(self.maps[i], lut = jet_lut, levels = [0,clim])
            
            self.t_start, self.t_stop = self.t-self.xsize/3. , self.t+self.xsize*2./3.
            f_start, f_stop = self.params_time_freq['f_start'], self.params_time_freq['f_stop']
            image.setRect(QRectF(self.t_start, f_start,self.xsize, f_stop-f_start))
            
        
        self.freqs = np.arange(p['f_start'],p['f_stop'],p['deltafreq'])
        self.need_recreate_thread = True
        
        self.sig_chunk_size = int(np.rint(self.xsize*self.global_sampling_rate))
        self.empty_sigs = [np.zeros(self.sig_chunk_size, dtype = ana.dtype) for ana in self.analogsignals]
    
    def refresh(self, fast = False):
        if self.is_computing.any():
            self.is_refreshing = False
            return
        
        self.t_start, self.t_stop = self.t-self.xsize/3. , self.t+self.xsize*2./3.

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
                chunk2[i1:i2] = chunk
                chunk = chunk2
            self.threads[i].sig = chunk
            self.threads[i].start()

            #~ self.vline.setPos(self.t)
            self.plots[i].setXRange( self.t_start, self.t_stop)
            
            f_start, f_stop = self.params_time_freq['f_start'], self.params_time_freq['f_stop']
            self.images[i].setRect(QRectF(self.t_start, f_start,self.xsize, f_stop-f_start))

        
        self.need_recreate_thread = False
        self.is_refreshing = False

    def map_computed(self, i):
        if self.grid_changing.tryLockForRead():
            if self.images[i] is not None:
                #~ f_start, f_stop = self.params_time_freq['f_start'], self.params_time_freq['f_stop']
                #~ self.images[i].setRect(QRectF(self.t_start, f_start,self.xsize, f_stop-f_start))
                self.images[i].updateImage(self.maps[i])
            self.is_computing[i] = False
            self.grid_changing.unlock()



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
        
        sigf=fftpack.fft(self.sig)
        n = self.wf.shape[0]
        sigf = np.concatenate([sigf[0:(n+1)/2],  sigf[-(n-1)/2:]])*self.factor
        #~ sigf *= self.win
        wt_tmp=fftpack.ifft(sigf[:,np.newaxis]*self.wf,axis=0)
        wt = fftpack.fftshift(wt_tmp,axes=[0])
        
        self.parent().maps[self.n] = abs(wt)
        self.finished.emit(self.n)
        #~ self.parent().grid_changing.unlock()


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
