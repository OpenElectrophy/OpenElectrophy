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
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    rcg = bl.recordingchannelgroups[0]

    spikesorter = SpikeSorter(rcg)

    #~ spikesorter.ButterworthFilter( f_low = 200.)
    #~ spikesorter.DerivativeFilter()
    spikesorter.SlidingMedianFilter(window_size =  50.*pq.ms,
                             sliding_step =  25.*pq.ms, interpolation = 'spline')
    
    
    spikesorter.RelativeThresholdDetection(sign= '-', relative_thresh = 4.,noise_estimation = 'MAD', threshold_mode = 'peak',  peak_span = 0.5*pq.ms)
    
    
    print spikesorter

    spikesorter.check_display_attributes()
    
    from OpenElectrophy.gui.spikesorting import FilteredBandSignal

    app = QApplication([ ])
    w1 = FilteredBandSignal(spikesorter = spikesorter)
    w1.refresh()
    w1.show()
    app.exec_()
    
    



if __name__ =='__main__':
    test1()
    
    

 
