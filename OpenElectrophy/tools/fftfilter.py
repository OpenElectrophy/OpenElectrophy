# -*- coding: utf-8 -*-
"""

"""

import numpy as np

def fft_passband_filter(sig,
        f_low =0,f_high=1,
        axis = 0,
        ) :
    """
    Pass band filter using fft for real 1D signal.
    
    sig : a numpy.array signal
    f_low : low pass niquist frequency (1 = samplin_rate/2)
    f_high : high  cut niquist frequency (1 = samplin_rate/2)
    """
    n = sig.shape[axis]
    N = int(2**(np.ceil(np.log(n)/np.log(2))))
    SIG = np.fft.fft(sig,n = N , axis = axis)

    n_low = int(np.floor((N-1)*f_low/2)+1)
    fract_low = 1-((N-1)*f_low/2-np.floor((N-1)*f_low/2))
    n_high = int(np.floor((N-1)*f_high/2)+1)
    fract_high = 1-((N-1)*f_high/2-np.floor((N-1)*f_high/2))

    s = [ slice(None) for i in range(sig.ndim) ]
    if f_low >0 :
        s[axis] = 0
        SIG[s] = 0
        
        s[axis] = slice(1,n_low)
        SIG[ s ] = 0
        
        s[axis] = n_low
        SIG[s] *= fract_low
        
        s[axis] = -n_low
        SIG[s] *= fract_low
        
        if n_low !=1 :
            s[axis] = slice(-n_low+1, None)
            SIG[s] = 0

    if f_high <1 :
        s[axis] = n_high
        SIG[s] *= fract_high
        
        s[axis] = slice(n_high+1,-n_high)
        SIG[ s ] = 0
        
        s[axis] = -n_high
        SIG[s] *= fract_high

    s[axis] = slice(0,n)
    
    return np.real(np.fft.ifft(SIG , axis=axis)[s])
