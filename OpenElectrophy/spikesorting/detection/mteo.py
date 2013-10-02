import numpy as np
import numexpr as ne
import quantities as pq
from scipy import hamming
from .tools import threshold_detection_multi_channel_multi_segment

class MTEODetection(object):
    """
    
    This medthod filters the signals using the MTEO method proposed by Choi, Jung and Kim IEEE Transactions on biomedical engineering, 53:4 (2006)
    and detect spikes on it
    
    The kTEO is known to be very sensitive to spikes, (signals that is concentrated in a short time interval and at a high frequency band
    psy(signal(n)) = (signal(n))**2.-signal(n-k)signal(n+k)
    
    In MTEO, a list of different k is used and and the max of all signals is used as the final filtered signal to detect spikes.
    
    In the current version, a median threshold is applied to MTEO signals.
    
    Parameters:
    k_max,k_inc: choice of k used to compute MTEO signal, range(1,k_max,k-inc)
    from_fullband: if True, compute MTEO from the fullband_sigs, otherwise from filtered_sigs (if it exists)
    
    """
    
    name = 'MTEO detection'
    params = [  {'name': 'k_max', 'type': 'int', 'value': 1 },
                            {'name': 'k_inc', 'int': 'float', 'value':1},
                            {'name': 'from_fullband', 'type': 'bool', 'value': True, },
                            {'name': 'median_thresh', 'type': 'float', 'value': 5., 'step' : 0.1},
                            {'name': 'consistent_across_channels', 'type': 'bool', 'value': False, },
                            {'name': 'consistent_across_segments', 'type': 'bool', 'value': True, },
                            ]
    
    def run(self, spikesorter, 
                        k_max=1,
                        k_inc=1,
                        from_fullband=False,
                        median_thresh=5.,
                        consistent_across_channels = False,
                        consistent_across_segments = True,
                        ):
                        
        sps = spikesorter

        # What is the source signal?
        if (from_fullband or (sps.filtered_sigs is None)):
            MTEO_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)
            sigs=sps.full_band_sigs
        else:
            MTEO_sigs = np.empty( sps.filtered_sigs.shape, dtype = object)
            sigs=sps.filtered_sigs

        # Compute MTEO signals
        for c,s in np.ndindex(sigs.shape) :  
            sig = sigs[c, s]
            kTEO_sig=np.zeros(sig.size)
            #compute all k-TEO, including k_max if possible
            for k in range(1,k_max+1,k_inc): 
                s1 = sig[0:-2*k]
                s2 = sig[k:-k]
                s3 = sig[2*k:]
                # standard kTEO signal
                kTEO_sig[k:-k]=ne.evaluate("s2**2-s1*s3") 
                hamm = hamming(4*(k+1)+1)#smoothing window
                norm=np.sqrt(3*(hamm**2.)+(hamm.sum())**2.)
                hamm = hamm/norm # normalization of the window 
                #proposed by Choi et al. to prevent excess of false detections at small k
                kTEO_sig=np.convolve(kTEO_sig,hamm,'same')
                if k==1:
                    MTEO_sig=kTEO_sig.copy()
                else:
                    #take the max over all kTEO iteratively
                    MTEO_sig=ne.evaluate("where(MTEO_sig<kTEO_sig,kTEO_sig,MTEO_sig)") 
                        
            MTEO_sigs[c,s]=MTEO_sig

        # Threshold estimation
        thresholds = np.zeros(MTEO_sigs.shape, dtype = float)
        for c, s in np.ndindex(MTEO_sigs.shape):
            sig = MTEO_sigs[c, s]
            thresholds[c, s] = abs(median_thresh) * np.median(abs(sig)) / .6745
        
        # Detect
        #~ sweep_size = int((sps.sig_sampling_rate*sweep_clean_size).simplified)
        #~ sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                #~ MTEO_sigs, thresholds, '+', 
                                #~ consistent_across_channels,consistent_across_segments,
                                #~ sweep_size, merge_method = merge_method,)


        
        # Detect
        sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                MTEO_sigs, thresholds, '+', 
                                consistent_across_channels,consistent_across_segments,
                                'crossing', None)
        sps.detection_thresholds = None
