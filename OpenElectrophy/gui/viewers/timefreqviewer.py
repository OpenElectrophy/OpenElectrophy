# -*- coding: utf-8 -*-
"""
TimeFreqViewer
"""

from tools import *
from guiqwt.styles import CurveParam

from scipy import fftpack
#~ import numpy.fft as fftpack

import time

from PyQt4.Qwt5 import QwtPlot

    

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
        
        
        mainlayout = QHBoxLayout()
        self.setLayout(mainlayout)
        
        self.grid = QGridLayout()
        mainlayout.addLayout(self.grid)
        
        self.global_sampling_rate = self.analogsignals[0].sampling_rate
        
        n = len(analogsignals)
        
        r,c = 0,0
        self.plots = [ ]
        for i, anasig in enumerate(self.analogsignals):
            assert(anasig.sampling_rate==self.global_sampling_rate)
            plot = ImagePlot(yreverse=False,lock_aspect_ratio=False, ylabel = 'freqs')
            self.plots.append(plot)
            self.grid.addWidget(plot, r,c)
            plot.enableAxis(QwtPlot.xBottom, False) # QwtPlot
            plot.enableAxis(QwtPlot.yRight, False) # QwtPlot
            #~ if c!=0: plot.enableAxis(QwtPlot.yLeft, False) # QwtPlot
            
            c+=1
            if c==nb_column:
                c=0
                r+=1
        self.images = [ None for i in range(n)]
        self.maps = [ None for i in range(n)]
        self.is_computing = np.zeros((n), dtype = bool)
        self.range_lines = [ None for i in range(n)]
        self.threads = [ None for i in range(n)]
        
        self.xsize = 5.
        self.params_time_freq = dict(
                                        f_start=3.,
                                        f_stop = 90.,
                                        deltafreq = 2.,
                                        sampling_rate = self.global_sampling_rate.magnitude,#FIXME
                                        f0 = 2.5,
                                        normalisation = 0.,
                                        )
        self.need_recreate_thread = True
        
        self.initialize_time_freq()
        
    def initialize_time_freq(self):
        for plot in self.plots:
            plot.del_all_items()
        
        # we take sampling_rate = f_stop*4 or (original sampling_rate)
        f_stop = self.params_time_freq['f_stop']
        if f_stop*4 < self.analogsignals[0].sampling_rate.magnitude:
            self.params_time_freq['sampling_rate'] = f_stop*4
        
        self.len_wavelet = int(self.xsize*self.params_time_freq['sampling_rate'])
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq).transpose()
        
        self.win = np.hamming(self.len_wavelet)
        for i, plot in enumerate(self.plots):
            self.maps[i] = np.zeros(self.wf.shape)
            image = make.image(self.maps[i], title='TimeFreq',interpolation ='nearest')
            plot.add_item(image)
            self.images[i] =image
            
            self.range_lines[i]  = make.range(0.,0.)
            plot.add_item(self.range_lines[i])
        
        p = self.params_time_freq
        self.freqs = np.arange(p['f_start'],p['f_stop'],p['deltafreq'])
        
        self.need_recreate_thread = True
        
        

    def refresh(self, fast = False):
        #~ print self.is_computing
        if self.is_computing.any():
            self.is_refreshing = False
            return
        
        
        #~ xaxis, yaxis = self.plot.get_active_axes()
        #~ xaxis.hide()
        self.t_start, self.t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        
        for i, anasig in enumerate(self.analogsignals):
            self.is_computing[i] = True
            sl = get_analogsignal_slice(anasig,self.t_start*pq.s, self.t_stop*pq.s,
                                                return_t_vect = False)
            chunk = anasig.magnitude[sl]
            if chunk.size==self.global_sampling_rate*self.xsize:
                if self.need_recreate_thread:
                    self.threads[i] = ThreadComputeTF(chunk, self.wf, self.win,i, parent = self)
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
        #~ print 'i', i
        xaxis, yaxis = self.plots[i].get_active_axes()
        self.plots[i].setAxisScale(yaxis, self.freqs[0], self.freqs[-1])
        self.plots[i].setAxisScale(xaxis,self.t_start, self.t_stop)

        self.images[i].set_ydata(self.freqs[0], self.freqs[-1])
        self.images[i].set_xdata(self.t_start, self.t_stop)
        
        self.images[i].set_data(self.maps[i])
        self.range_lines[i].set_range(self.t,self.t)
        self.plots[i].replot()
        self.is_computing[i] = False
        
        #perfs
        if not hasattr(self, 'last_times'):
            self.last_times = [ ]
        if i==0:
            self.last_times.append(time.time())
            if len(self.last_times)>10:
                self.last_times = self.last_times[-10:]
            print 1./np.mean(np.diff(self.last_times)), 'fps', 'for ', self.maps[0].shape



class ThreadComputeTF(QThread):
    finished = pyqtSignal(int)
    def __init__(self, sig, wf, win,n, parent = None, ):
        super(ThreadComputeTF, self).__init__(parent)
        self.sig = sig
        self.wf = wf
        self.win = win
        self.n = n
        
    def run(self):
        n = self.wf.shape[1]/2
        sigf=fftpack.fft(self.sig)
        sigf = np.concatenate([sigf[:n],  sigf[-n:]])
        sigf *= self.win
        wt_tmp=fftpack.ifft(sigf[np.newaxis,:]*self.wf,axis=1)
        wt = fftpack.fftshift(wt_tmp,axes=[1])
        
        self.parent().maps[self.n] = abs(wt)
        self.finished.emit(self.n)


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
        
        
        
        