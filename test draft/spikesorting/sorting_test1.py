import sys
sys.path.append('../..')

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy import *

import quantities as pq
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def test1():
    bl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 10.*pq.s,
                                                        noise_ratio = 0.7,
                                                        nb_segment = 2,
                                                        )
    rcg = bl.recordingchannelgroups[0]

    spikesorter = SpikeSorter(rcg)

    spikesorter.ButterworthFilter( f_low = 200.)
    spikesorter.RelativeThresholdDetection(sign= '-', relative_thresh = 3.5,noise_estimation = 'MAD', threshold_mode = 'peak', peak_span = 0.4*pq.ms)
    spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-', peak_method = 'biggest_amplitude')
    spikesorter.PcaFeature(n_components = 4)
    spikesorter.SklearnGaussianMixtureEm(n_cluster = 5)
    
    

    
    spikesorter.check_display_attributes()
    from OpenElectrophy.gui.spikesorting import FilteredBandSignal, AverageWaveforms
    app = QApplication([ ])
    w1 = AverageWaveforms(spikesorter = spikesorter)
    w1.refresh()
    w1.show()
    
    w2 = FilteredBandSignal(spikesorter = spikesorter)
    w2.refresh()
    w2.show()
    app.exec_()


if __name__ =='__main__':
    test1()
    
    

 
