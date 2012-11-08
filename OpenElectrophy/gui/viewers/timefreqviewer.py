# -*- coding: utf-8 -*-
"""
TimeFreqViewer
"""

from tools import *
from guiqwt.styles import CurveParam

from scipy import fftpack
#~ import numpy.fft as fftpack

import time

class TimeFreqViewer(ViewerBase):
    """
    This is a time frequancy viewer based on morlet continuous wavelet tranform.
    
    """
    def __init__(self, parent = None,
                            analogsignal = None,
                            
                            ):
                            
        super(TimeFreqViewer,self).__init__(parent)
    
        self.analogsignal = analogsignal
        
        mainlayout = QHBoxLayout()
        self.setLayout(mainlayout)
        
        self.plot = ImagePlot(yreverse=False,lock_aspect_ratio=False)
        mainlayout.addWidget(self.plot)
        
        
        self.image = None
        self.xsize = 2.
        self.params_time_freq = dict(
                                        f_start=3.,
                                        f_stop = 90.,
                                        deltafreq = 1.,
                                        sampling_rate = self.analogsignal.sampling_rate.magnitude,#FIXME
                                        f0 = 2.5,
                                        normalisation = 0.,
                                        )
        self.need_recreate_thread = True
        self.is_computing = False
        self.initialize_time_freq()
        
    def initialize_time_freq(self):
        self.plot.del_all_items()
        
        # we take sampling_rate = f_stop*4 or (original sampling_rate)
        f_stop = self.params_time_freq['f_stop']
        if f_stop*4 < self.analogsignal.sampling_rate.magnitude:
            self.params_time_freq['sampling_rate'] = f_stop*4
        
        self.len_wavelet = int(self.xsize*self.params_time_freq['sampling_rate'])
        self.wf = generate_wavelet_fourier(len_wavelet= self.len_wavelet, ** self.params_time_freq).transpose()
        
        self.win = np.hamming(self.len_wavelet)
        self.map = np.zeros(self.wf.shape)
        self.image = make.image(self.map, title='TimeFreq',interpolation ='nearest')
        self.plot.add_item(self.image)
        
        p = self.params_time_freq
        self.freqs = np.arange(p['f_start'],p['f_stop'],p['deltafreq'])
        
        self.range_line = make.range(0.,0.)
        self.plot.add_item(self.range_line)
        
        
        

    def refresh(self, fast = False):
        if self.is_computing:
            return
        self.isComputing = True
        
        #~ xaxis, yaxis = self.plot.get_active_axes()
        self.t_start, self.t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        sl = get_analogsignal_slice(self.analogsignal,self.t_start*pq.s, self.t_stop*pq.s,
                                                return_t_vect = False)
        chunk = self.analogsignal.magnitude[sl]
        
        if chunk.size==self.analogsignal.sampling_rate.magnitude*self.xsize:
        
            if self.need_recreate_thread:
                self.thread = ThreadComputeTF(chunk, self.wf, self.win, parent = self)
                self.thread.finished.connect(self.map_computed)
                self.need_recreate_thread = False
            else:
                self.thread.sig = chunk
            self.thread.start()
        else:
            self.map[:] = 0.
            self.map_computed()
            
        
        self.is_refreshing = False

    
    def map_computed(self):
        
        xaxis, yaxis = self.plot.get_active_axes()
        self.plot.setAxisScale(yaxis, self.freqs[0], self.freqs[-1])
        self.plot.setAxisScale(xaxis,self.t_start, self.t_stop)

        self.image.set_ydata(self.freqs[0], self.freqs[-1])
        self.image.set_xdata(self.t_start, self.t_stop)
        
        self.image.set_data(self.map)
        self.range_line.set_range(self.t,self.t)
        self.plot.replot()
        self.isComputing = False
        
        if not hasattr(self, 'last_times'):
            self.last_times = [ ]
        self.last_times.append(time.time())
        if len(self.last_times)>10:
            self.last_times = self.last_times[-10:]
        print 1./np.mean(np.diff(self.last_times)), 'fps', 'for ', self.map.shape



class ThreadComputeTF(QThread):
    finished = pyqtSignal()
    def __init__(self, sig, wf, win, parent = None, ):
        super(ThreadComputeTF, self).__init__(parent)
        self.sig = sig
        self.wf = wf
        self.win = win
        
    def run(self):
        n = self.wf.shape[1]/2
        sigf=fftpack.fft(self.sig)
        sigf = np.concatenate([sigf[:n],  sigf[-n:]])
        sigf *= self.win
        wt_tmp=fftpack.ifft(sigf[np.newaxis,:]*self.wf,axis=1)
        wt = fftpack.fftshift(wt_tmp,axes=[1])
        
        self.parent().map = abs(wt)
        self.finished.emit()


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
        
        
        
        