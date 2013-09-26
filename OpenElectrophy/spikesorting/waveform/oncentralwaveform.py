

import quantities as pq
import numpy as np

from tools import initialize_waveform, remove_limit_spikes

from .tools import get_following_peak_multi_channel

from scipy.optimize import minimize
from scipy.interpolate import interp1d

from matplotlib.cm import get_cmap

class AlignWaveformOnCentralWaveform(object):
    """
    This code is the transcription of Christophe Pouzat idea for waveform alignement 
    and jitter cancellation. See here:
    https://github.com/christophe-pouzat/Neuronal-spike-sorting/blob/master/code/sorting.R
    
    The main idea is align waveform in between samples to remove the jitter due to sampling.
    
    """
    name = 'Align waveforms on the central one'
    params = [  
                            #~ {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'left_sweep', 'type': 'quantity', 'value': 1.*pq.ms, 'step' : 100*pq.us },
                            {'name': 'right_sweep', 'type': 'quantity', 'value': 1.*pq.ms,'step' : 100*pq.us },
                            
                            {'name': 'sweep_factor_for_interpolation', 'type': 'float', 'value': 3 },
                            
                            
                            {'name': 'shift_estimation_method', 'type': 'list' , 'value' : 'taylor order1', 'values' : ['taylor order1', 'optimize'] },
                            
                            {'name': 'shift_method', 'type': 'list' , 'value' : 'sinc', 'values' : ['sinc', 'spline', 'lanczos'] },
                            
                            {'name': 'max_iter', 'type': 'int', 'value': 4 },
                            
                            ]
    
    
    mpl_plots = [ 'plot_iterative_centers']

    def run(self, spikesorter,  left_sweep = 1*pq.ms, right_sweep = 1*pq.ms,
                            sweep_factor_for_interpolation = 3,
                            shift_estimation_method = 'taylor order1',
                            shift_method = 'sinc',
                            max_iter= 4,
                            
                            ):
        sps = spikesorter

        sr = sps.sig_sampling_rate
        swl = int((left_sweep*sr).simplified)
        swr = int((right_sweep*sr).simplified)
        #~ print swl, (left_sweep*sr)
        wsize = swl + swr + 1
        trodness = sps.filtered_sigs.shape[0]
        
        # For interpolation we take a larger sweep in a first time.
        swl2 = int(sweep_factor_for_interpolation*swl)
        swr2 = int(sweep_factor_for_interpolation*swr)
        wisze2 = swl2 + swr2 + 1
        
        # clean
        remove_limit_spikes(spikesorter, swl2, swr2)
        
        
        # Initialize
        initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        
        # take waveform in signal
        wfs = spikesorter.spike_waveforms
        trodness = len(spikesorter.rcs)
        n_spike = wfs.shape[0]
        large_wfs = np.empty((n_spike, trodness, wisze2), dtype = float) # non aligned larger waveform
        n = 0
        for s, indexes in enumerate(sps.spike_index_array):
            for ind in indexes :
                for c in range(len(sps.rcs)):
                    sig = sps.filtered_sigs[c, s]
                    wfs[n,c, :] = sig[ind-swl:ind+swr+1]
                    large_wfs[n,c, :] = sig[ind-swl2:ind+swr2+1]
                n += 1
        
        self.deltas = deltas = np.zeros(n_spike)
        self.centers = [ ]
        self.centers_mad = [ ]
        
        for iter in range(max_iter):
            # TODO : sctop criterium
            
            flat_wfs = wfs.reshape(n_spike, -1)
            center = np.median(flat_wfs, axis=0)
            
            # for plotting
            self.centers.append(center)
            self.centers_mad.append(np.median(np.abs(flat_wfs-np.median(flat_wfs,axis=0)), axis=0) / .6745)
            
            
            # shift estimation
            if shift_estimation_method == 'taylor order1':
                center_D = np.r_[0,(center[2:] - center[:-2])/2, 0]
                new_deltas = np.sum((flat_wfs-center)*center_D , axis = 1)/np.sum(center_D**2)
                
            elif shift_estimation_method == 'taylor order2':
                center_D = np.r_[0,(center[2:] - center[:-2])/2, 0]  #first derivative
                center_DD = np.r_[0,(center_D[2:] - center_D[:-2])/2, 0]#second derivative
                new_deltas = np.zeros(n_spike)
                for i in range(n_spike):
                    def error(delta):
                        return np.sum((flat_wfs[i,:]-center-delta*center_D-delta**2*center_DD/2)**2)
                    res = minimize(error,[0.], method = 'BFGS')
                    new_deltas[i] = res.x
            
            elif shift_estimation_method == 'optimize':
                pass#discuter avec CP optimize sur les WF concatenate
                #~ base = np.arange(large_wfs.shape[2])
                #~ new_base = np.arange(swl2+1-swl,swl2+2+swr)
                
                #~ deltas = np.zeros(nb_spikes)
                #~ for i in range(wfs.shape[0]):
                    #~ def error(delta):
                        #~ new_wf = 
                        #~ return np.sum(
                        #~ wfs[i]
                    #~ scipy.optimize.minimize(error, 
                    #~ deltas[i] = 

            print iter
            print np.mean(new_deltas)
            deltas += new_deltas
            print np.mean(deltas)
            
            # apply shift on waveform by interpolation
            base = np.arange(large_wfs.shape[2])
            new_base = np.arange(swl2+1-swl,swl2+2+swr)
            for i in range(n_spike):
                for c in range(large_wfs.shape[1]):
                    if shift_method == 'sinc':
                        pass
                    elif shift_method == 'spline':
                        interpolator = interp1d(base, large_wfs[i,c,:], kind = 1)
                        wfs[i,c,:] = interpolator(new_base-deltas[i])
                    elif shift_method == 'lanczos':
                        pass


    def plot_iterative_centers(self, fig, sps):
        n = len(self.centers)
        cmap = get_cmap('jet' , n)
        
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2, sharey = ax1)
        for i,center in enumerate(self.centers):
            ax1.plot(center, label = str(i), color = cmap(i))
        ax1.legend()
        for i,mad in enumerate(self.centers_mad):
            ax2.plot(mad, label = str(i), color = cmap(i))
        ax2.legend()
        ax1.set_title('Centers')
        ax1.set_title('MAD of Centers')






