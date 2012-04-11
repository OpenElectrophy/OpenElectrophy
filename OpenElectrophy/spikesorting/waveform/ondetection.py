



import quantities as pq
import numpy as np


class AlignWaveformOnDetection:
    """
    Align spike waveform on the point where the spike has been detected.
    So it can be the threshold point but for some method it can be something else.
    
    
    """
    name = 'Align waveform on detection index'

    def run(self, spikesorter, left_sweep = 1*pq.ms, right_sweep = 1*pq.ms):
        s = spikesorter

        sr = s.signalSamplingRate
        swL = int(left_sweep*sr)
        swR = int(right_sweep*sr)
        wsize = swL + swR + 1
        trodness = s.filteredBandAnaSig.shape[0]
        
        # Initialize
        initialize_waveform(spikesorter, wisze)
        s.waveformSamplingRate = s.signalSamplingRate
        s.leftSweep =swL
        s.rightSweep = swR
        
        # take individual waveform
        n = 0
        for seg, indexes in enumerate(self.spikeIndexArray):
            for ind in peak_indexes :
                for rc in range(len(s.recordingChannels)):
                    sig = s.filteredBandAnaSig[rc, seg]
                    s.spikeWaveforms[:,rc, n] = sig[ind-swL:ind+swR+1]
                n += 1


