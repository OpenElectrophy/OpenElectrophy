import numpy as np
import quantities as pq
from scipy import hamming

class MTEOFilter(object):
    """
    
    This medthod filters the raw signals using the MTEO method proposed by Choi, Jung and Kim IEEE Transactions on biomedical engineering, 53:4 (2006)
    
    The kTEO is known to be very sensitive to spikes, (signals that is concentrated in a short time interval and at a high frequency band
    psy(signal(n)) = (signal(n))**2.-signal(n-k)signal(n+k)
    
    In MTEO, a list of different k is used and and the max of all signals is used as the final filtered signal.
    
    """
    
    name = 'MTEO detection'
    
    def run(self, spikesorter, 
                        k_max=1,
                        k_inc=1,
                        consistent_across_channels = False,
                        consistent_across_segments = True,
                        ):
                        
        sps = spikesorter

        if sps.filtered_sigs is None:
            sps.filtered_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)

        for c,s in np.ndindex(sps.full_band_sigs.shape) :  
            sig = sps.full_band_sigs[c, s]
            for k in range(1,k_max+1,k_inc): #compute all k-TEO, inclunding k_max if possible
                s1 = sig[0:-2*k]
                s2 = sig[k:-k]
                s3 = sig[2*k:]
                kTEO_sig=s2**2-s1*s3 # standard kTEO signal
                kTEO_sig=np.r_[np.zeros(k),kTEO_sig,np.zeros(k)] # extend the filtered sig to match the original size
                hamm = hamming(4*(k+1)+1)#smoothing window
                norm=np.sqrt(3*(hamm**2.)+(hamm.sum())**2.)
                hamm = hamm/norm # normalization of the window proposed by Choi et al. to prevent excess of false detections at small k
                kTEO_sig=np.convolve(kTEO_sig,hamm,'same')
                if k==1:
                    MTEO_sig=kTEO_sig.copy()
                else:
                    MTEO_sig=np.c_[MTEO_sig,kTEO_sig].max(axis=1) #take the max over all kTEO iteratively
            
            sps.filtered_sigs[c,s]=MTEO_sig
