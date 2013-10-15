

import quantities as pq
import numpy as np

from tools import initialize_waveform, remove_limit_spikes

from .tools import get_following_peak_multi_channel


# FIXME!!!!!
try:
    from scipy.optimize import minimize
except:
    print 'no scipy.optimize.minimize'

from scipy.interpolate import interp1d
from scipy.signal import convolve

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
                            
                            
                            {'name': 'shift_estimation_method', 'type': 'list' , 'value' : 'taylor order1', 'values' : ['taylor order1'] }, #, 'optimize'
                            
                            {'name': 'shift_method', 'type': 'list' , 'value' : 'sinc', 'values' : ['sinc', 'spline', 'lanczos'] },
                            
                            {'name': 'max_iter', 'type': 'int', 'value': 1 },
                            
                            ]
    
    
    mpl_plots = [ 'plot_iterative_centers']

    def run(self, spikesorter,  left_sweep = 1*pq.ms, right_sweep = 1*pq.ms,
                            sweep_factor_for_interpolation = 3,
                            shift_estimation_method = 'taylor order1',
                            shift_method = 'sinc',
                            max_iter= 1,
                            
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
        wfs = initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        
        # take waveform in signal
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
        
        clusters = self.clusters = sps.cluster_names.keys()
        self.deltas = deltas = np.zeros(n_spike)
        
        self.all_centers =  [ ]
        self.all_centers_mad = [ ]
        self.all_deltas = [ ]
        
        
        for iter in range(max_iter):
            print iter
            # TODO : sctop criterium
            flat_wfs = wfs.reshape(n_spike, -1)
           
            centers = { }
            mads = { }
            for c in clusters:
                ind = sps.spike_clusters==c
                centers[c] = np.median(flat_wfs[ind,:], axis=0)
                mads[c] = np.median(np.abs(flat_wfs[ind,:]-centers[c]), axis=0) / .6745
            
            
            # for plotting
            self.all_centers.append(centers)
            self.all_centers_mad.append(mads)
            
            # shift estimation by clusters
            new_deltas = np.zeros(n_spike)
            for c in clusters:
                ind = sps.spike_clusters==c
                if shift_estimation_method == 'taylor order1':
                    center_D = np.r_[0,(centers[c][2:] - centers[c][:-2])/2, 0]#first derivative
                    new_deltas[ind] = np.sum((flat_wfs[ind]-centers[c])*center_D , axis = 1)/np.sum(center_D**2)
                    
                elif shift_estimation_method == 'taylor order2':
                    center_D = np.r_[0,(centers[c][2:] - centers[c][:-2])/2, 0] #first derivative
                    center_DD = np.r_[0,(center_D[2:] - center_D[:-2])/2, 0]#second derivative
                    #~ for i in range(n_spike):
                    for i in np.where(ind):
                        def error(delta):
                            return np.sum((flat_wfs[i,:]-centers[c]-delta*center_D-delta**2*center_DD/2)**2)
                        res = minimize(error,[0.], method = 'BFGS')
                        new_deltas[i] = res.x

            
            deltas += new_deltas
            self.all_deltas.append(deltas.copy())


            base = np.arange(large_wfs.shape[2])
            new_base = np.arange(swl2+1-swl,swl2+2+swr)
            # apply shift on waveform by interpolation
            if shift_method == 'sinc':
                for i in range(n_spike):
                    for c in range(large_wfs.shape[1]):
                        half = base.size//2
                        kernel = np.sinc(np.arange(-half, half)-deltas[i]+1)
                        wfs[i,c,:] = convolve(large_wfs[i,c,:], kernel, mode = 'same')[swl2+1-swl:swl2+2+swr]
                
            elif shift_method == 'spline':
                for i in range(n_spike):
                    for c in range(large_wfs.shape[1]):
                        interpolator = interp1d(base, large_wfs[i,c,:], kind = 1)
                        wfs[i,c,:] = interpolator(new_base-deltas[i])
            
            elif shift_method == 'lanczos':
                #TODO!!!
                pass
        
        spikesorter.spike_waveforms = wfs

    def plot_iterative_centers(self, fig, sps):
        N = 10.
        n = len(self.all_centers)
        cmap = get_cmap('jet' , int(N+1))
        step = max(int(n/N),1)
        
        ax1 = fig.add_subplot(2,2,1)
        ax2 = fig.add_subplot(2,2,2, sharey = ax1)
        ax3 = fig.add_subplot(2,1,2)
        for c in self.clusters:
            for i in range(0,n,step):
                label = 'Iter {}'.format(i*step) if c== self.clusters[0] else None
                ax1.plot(self.all_centers[i][c], label = label, color = cmap(i))
                ax2.plot(self.all_centers_mad[i][c], label = label, color = cmap(i))
        ax1.legend()
        ax2.legend()
        for i,deltas in enumerate(self.all_deltas[::step]):
            y,x = np.histogram(deltas, bins = 100)
            ax3.plot(x[:-1], y, color = cmap(i))
        ax1.set_title('Centers')
        ax2.set_title('MAD of Centers')
        ax3.set_title('Deltas distrib')
            



def interpolate_sinc(x,y,x2):
    
    def func(u):
        np.sum(y*np.sinc(x-u))



