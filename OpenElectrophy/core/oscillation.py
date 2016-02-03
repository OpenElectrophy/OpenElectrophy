#encoding : utf-8 

import quantities as pq
from datetime import datetime
import numpy as np

from .base import OEBase

import scipy.signal

class Oscillation(OEBase):
    """
    Class to handle a transient oscillation.
    Can old the full line in time, frequency and complexe morlet value.
    Detected from morlet scalogram.
    
    See also: 
    """

    tablename = 'Oscillation'
    neoclass = None
    attributes =[ ('name', str),
                                                ('time_start', float),
                                                ('time_stop', float),
                                                ('freq_start', float),
                                                ('freq_stop', float),
                                                ('time_max', float),
                                                ('freq_max', float),
                                                ('amplitude_max', float),
                                                ('time_line', pq.Quantity, 1),
                                                ('freq_line', pq.Quantity, 1),
                                                ('value_line', np.ndarray, 1),
                                                ]
    one_to_many_relationship = [ ]
    many_to_one_relationship = [ 'AnalogSignal' ]
    many_to_many_relationship = [ ]
    inheriting_quantities = None


    def phase_of_times(self,  times , sampling_rate = 1000.):
        """
        Give the phases of the oscillation at the specific 'times'
        
        The under underlying precision of phase sampling is given by 'sampling_rate'
        
        Return 'nan' for timepoints outside the range where the oscillation phase is known (Oscillation.time_line)
        
        Note: an oscillation detected with a very small sampling rate compared to its frequency will have a drift in its reconstructed phase. 
        It is advised to have an original sampling rate of at least 4 times the oscillation frequency
        """
        if self.time_line.size>1:
            old_dt = (self.time_line[1]-self.time_line[0]).rescale('s').magnitude
            x = np.arange(self.time_start, self.time_stop+old_dt, 1./sampling_rate)
        else:
            x=self.time_line
        v = self.value_line
        

        # Before resampling, in order to avoid slow down due the use of ifft in scipy.resample
        # y is padded with 0 proportionnally to the distance from x.size to the next 2**N 
        # QUESTION: does it lead to some strange edge effects???
        N=int(np.ceil(np.log2(x.size)))
        vv=np.r_[v,np.zeros(v.size*(2**N-x.size)//x.size)]
        vv = scipy.signal.resample( vv, 2**N)
        v = vv[:x.size]

        y2 = np.angle(v)



        d = np.digitize( times , x )
        d[d==len(v)] = 0 # points above the highest time value where the oscillation phase is known
        phases = y2[d]
        phases[ d==0 ] = np.nan # all points outside the range where the oscillation is known
        return phases

    def plot_line_on_signal(self,   color ='m',
                                                    sampling_rate = None,
                                                    **kargs):
        if 'ax'in kargs:
            ax = kargs['ax']
        
        if sampling_rate is None:
            x = self.time_line
            v = self.value_line
            y = np.cos(np.angle(v))*np.abs(v)
        else :
            if self.time_line.size>1:
                old_dt = (self.time_line[1]-self.time_line[0]).rescale('s').magnitude
                x = np.arange(self.time_start, self.time_stop+old_dt, 1./sampling_rate.rescale('Hz').magnitude)
                #~ l = int((self.time_stop-self.time_start)*sampling_rate.rescale('Hz').magnitude)
                #~ x = self.time_start + np.arange(l) / sampling_rate.rescale('Hz').magnitude
                
            else:
                x=self.time_line
            v = self.value_line
            y = np.cos(np.angle(v))*np.abs(v)
            
            # Before resampling, in order to avoid slow down due the use of ifft in scipy.resample
            # y is padded with 0 proportionnally to the distance from x.size to the next 2**N 
            # QUESTION: does it lead to some strange edge effects???
            N=int(np.ceil(np.log2(x.size)))
            yy=np.r_[y,np.zeros(y.size*(2**N-x.size)//x.size)]
            yy = scipy.signal.resample( yy, 2**N)
            y = yy[:x.size]
        
        l = ax.plot(x,y  , linewidth = 1, color=color)
        return l


    