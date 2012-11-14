# -*- coding: utf-8 -*-
"""
TimeFreqViewer
"""

from tools import *

#~ from scipy import fftpack
import numpy.fft as fftpack

import time

import pyqtgraph as pg


from matplotlib import cm 
from matplotlib.colors import ColorConverter
lut = [ ]
cmap = cm.get_cmap('jet' , 10000)
for i in range(10000):
    r,g,b =  ColorConverter().to_rgb(cmap(i) )
    lut.append([r*255,g*255,b*255])
jet_lut = np.array(lut, dtype = np.uint8)



class OptionsGraphicsView(pg.GraphicsView):
    clicked = pyqtSignal()
    def __init__(self, *args, **kwds):
        pg.GraphicsView.__init__(self, *args, **kwds)
    def mousePressEvent(self, ev):
        QGraphicsView.mousePressEvent(self, ev)
        self.clicked.emit()


class TimeFreqViewer(ViewerBase):
    """
    This is a time frequancy viewer based on morlet continuous wavelet tranform.
    
    All analogsignals need to have same asmpling_rate.
    
    """
    def __init__(self, parent = None,
                            analogsignals = None,
                            nb_column = 4,
                            ):
                            
        super(TimeFreqViewer,self).__init__(parent)
    
        self.analogsignals = analogsignals

        self.global_sampling_rate = self.analogsignals[0].sampling_rate.magnitude
        for i, anasig in enumerate(self.analogsignals):
            assert(anasig.sampling_rate==self.global_sampling_rate)
        n = len(analogsignals)
        
        
        mainlayout = QHBoxLayout()
        self.setLayout(mainlayout)

        self.grid = QGridLayout()
        mainlayout.addLayout(self.grid)
        
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = [ {'name': 'xsize', 'type': 'float', 'value': 10., 'step': 0.1, 'limits' : (.1, 60)},
                                                                        {'name': 'f_start', 'type': 'float', 'value': 3., 'step': 1.},
                                                                        {'name': 'f_stop', 'type': 'float', 'value': 90., 'step': 1.},
                                                                        {'name': 'deltafreq', 'type': 'float', 'value': 3., 'step': 1.,  'limits' : (0.001, 1.e6)},
                                                                        {'name': 'f0', 'type': 'float', 'value': 2.5, 'step': 0.1},
                                                                        #~ {'name': 'sampling_rate', 'type': 'float', 'value': self.global_sampling_rate.magnitude, 'step':  10},
                                                                        {'name': 'normalisation', 'type': 'float', 'value': 0., 'step': 0.1},
                                                                        
                                                                        {'name': 'nb_column', 'type': 'int', 'value': 2},
                                                                        
                                                                    ])
        
        self.timefreqViewerParameters = TimefreqViewerParameters(paramGlobal = self.paramGlobal, analogsignals = analogsignals, parent= self)
        self.timefreqViewerParameters.setWindowFlags(Qt.Window)
        self.paramSignals = self.timefreqViewerParameters.paramSignals

        self.views = [ ]
        self.grid_changing =QReadWriteLock()
        self.create_grid()
        
        self.set_xsize(5.)
        self.need_recreate_thread = True
        
        self.paramGlobal.sigTreeStateChanged.connect(self.paramChanged)
        for p in self.paramSignals:
            p.sigTreeStateChanged.connect(self.paramChanged)
        self.initialize_time_freq()

    def get_xsize(self):
        return self.paramGlobal.param('xsize').value()
    def set_xsize(self, xsize):
        self.paramGlobal.param('xsize').setValue(xsize)
    xsize = property(get_xsize, set_xsize)

    def paramChanged(self):
        self.grid_changing.lockForWrite()
        self.create_grid()
        self.initialize_time_freq()
        self.refresh()
        self.grid_changing.unlock()

    def open_configure_dialog(self):
        self.timefreqViewerParameters.setWindowFlags(Qt.Window)
        self.timefreqViewerParameters.show()
        
    
    def create_grid(self):
        n = len(self.analogsignals)
        for view in self.views:
            if view is not None:
                view.hide()
                self.grid.removeWidget(view)
        self.views =  [ None for i in range(n)]
        r,c = 0,0
        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals[i].param('visible').value(): continue
            view = OptionsGraphicsView()
            view.clicked.connect(self.open_configure_dialog)
            self.views[i] = view
            self.grid.addWidget(view, r,c)
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
        for param in self.paramGlobal.children():
            self.params_time_freq[param.name()] = param.value()
        self.params_time_freq.pop('xsize')
        self.params_time_freq.pop('nb_column')
        
        # we take sampling_rate = f_stop*4 or (original sampling_rate)
        if p['f_stop']*4 < self.global_sampling_rate:
            p['sampling_rate'] = p['f_stop']*4
        else:
            p['sampling_rate']  = self.global_sampling_rate
        self.factor = p['sampling_rate']/self.global_sampling_rate # this compenate unddersampling in FFT.
        
        self.len_wavelet = int(self.xsize*p['sampling_rate'])
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq)[:,::-1]# reversed for plotting
        self.win = fftpack.ifftshift(np.hamming(self.len_wavelet))
        
        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals[i].param('visible').value(): continue
            view = self.views[i]
            self.maps[i] = np.zeros(self.wf.shape)
            if self.images[i] is not None:# for what ???
                view.removeItem(self.images[i])# for what ???
            image = pg.ImageItem(border='w')
            view.addItem(image)
            self.images[i] =image
            clim = self.paramSignals[i].param('clim').value()
            self.images[i].setImage(self.maps[i], lut = jet_lut, levels = [0,clim])
            view.setRange(QRectF(0, 0, self.wf.shape[0],self.wf.shape[1] ))
        
        self.freqs = np.arange(p['f_start'],p['f_stop'],p['deltafreq'])
        self.need_recreate_thread = True
    
    def refresh(self, fast = False):
        if self.is_computing.any():
            self.is_refreshing = False
            return
        
        self.t_start, self.t_stop = self.t-self.xsize/3. , self.t+self.xsize*2./3.

        for i, anasig in enumerate(self.analogsignals):
            if not self.paramSignals[i].param('visible').value(): continue
            self.is_computing[i] = True
            sl = get_analogsignal_slice(anasig,self.t_start*pq.s, self.t_stop*pq.s,
                                                return_t_vect = False)
            chunk = anasig.magnitude[sl]
            if np.abs(chunk.size-self.global_sampling_rate*(self.t_stop-self.t_start))<1.:
                if self.need_recreate_thread:
                    self.threads[i] = ThreadComputeTF(chunk, self.wf, self.win,i, self.factor, parent = self)
                    self.threads[i].finished.connect(self.map_computed)
                else:
                    self.threads[i].sig = chunk
                self.threads[i].start()
            else:
                self.maps[i][:] = 0.
                self.map_computed(i)
        
        self.need_recreate_thread = False
        self.is_refreshing = False

    def map_computed(self, i):
        if self.grid_changing.tryLockForRead():
            if self.images[i] is not None:
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
        self.factor = factor # thsi compensate subsampling
        
    def run(self):
        
        sigf=fftpack.fft(self.sig)
        n = self.wf.shape[0]
        sigf = np.concatenate([sigf[0:(n+1)/2],  sigf[-(n-1)/2:]])*self.factor
        #~ sigf *= self.win
        wt_tmp=fftpack.ifft(sigf[:,np.newaxis]*self.wf,axis=0)
        wt = fftpack.fftshift(wt_tmp,axes=[0])
        
        self.parent().maps[self.n] = abs(wt)
        self.finished.emit(self.n)
        self.parent().grid_changing.unlock()


class TimefreqViewerParameters(QWidget):
    def __init__(self, parent = None, analogsignals = [ ], paramGlobal = None):
        super(TimefreqViewerParameters, self).__init__(parent)
        
        param_by_channel = [ 
                        {'name': 'channel_name', 'type': 'str', 'value': '','readonly' : True},
                        {'name': 'channel_index', 'type': 'str', 'value': '','readonly' : True},
                        {'name': 'visible', 'type': 'bool', 'value': True},
                        {'name': 'clim', 'type': 'float', 'value': 10.},
                    ]
        
        self.analogsignals = analogsignals
        self.paramGlobal = paramGlobal
        

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        t = u'Options for Time Frequency maps'
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

    def paramSelectionChanged(self, param, changes):
        for pSignal in self.paramSignals:
            treeitem =  pSignal.items.keys()[0]
            for param, change, data in changes:
                if treeitem in self.tree2.selectedItems():
                    pSignal.param(param.name()).setValue(data)     




#TODO remove this when tiomefreq module is donne
def generate_wavelet_fourier(len_wavelet,
            f_start,
            f_stop,
            deltafreq,
            sampling_rate,
            f0,
            normalisation,
            ):
    """
    Compute the wavelet coefficients at all scales and makes its Fourier transform.
    When different signal scalograms are computed with the exact same coefficients, 
        this function can be executed only once and its result passed directly to compute_morlet_scalogram
        
    Output:
        wf : Fourier transform of the wavelet coefficients (after weighting), Fourier frequencies are the first 
    """
    # compute final map scales
    scales = f0/np.arange(f_start,f_stop,deltafreq)*sampling_rate
    # compute wavelet coeffs at all scales
    xi=np.arange(-len_wavelet/2.,len_wavelet/2.)
    xsd = xi[:,np.newaxis] / scales
    wavelet_coefs=np.exp(complex(1j)*2.*np.pi*f0*xsd)*np.exp(-np.power(xsd,2)/2.)

    weighting_function = lambda x: x**(-(1.0+normalisation))
    wavelet_coefs = wavelet_coefs*weighting_function(scales[np.newaxis,:])

    # Transform the wavelet into the Fourier domain
    #~ wf=fft(wavelet_coefs.conj(),axis=0) <- FALSE
    wf=fftpack.fft(wavelet_coefs,axis=0)
    wf=wf.conj() # at this point there was a mistake in the original script
    
    return wf
        
        
        
        