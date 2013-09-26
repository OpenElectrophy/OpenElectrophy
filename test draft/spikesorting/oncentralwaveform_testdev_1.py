import sys
sys.path.append('../..')

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy import *

import quantities as pq
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib import pyplot

def test1():
    bl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 10.*pq.s,
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    rcg = bl.recordingchannelgroups[0]

    spikesorter = SpikeSorter(rcg)

    spikesorter.ButterworthFilter( f_low = 200.)
    #~ spikesorter.RelativeThresholdDetection(sign= '-', relative_thresh = 4.,noise_estimation = 'MAD', threshold_mode = 'crossing')
    spikesorter.RelativeThresholdDetection(sign= '-', relative_thresh = 4.,noise_estimation = 'MAD', threshold_mode = 'peak')
    
    #~ spikesorter.AlignWaveformOnDetection(left_sweep = 1.5*pq.ms , right_sweep = 2.5*pq.ms, sign = '-')
    #~ spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-', peak_method = 'biggest_amplitude')
    #~ spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-', peak_method = 'closer')
    spikesorter.AlignWaveformOnCentralWaveform(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, 
                                                                                             #~ shift_estimation_method = 'taylor order1', 
                                                                                             shift_estimation_method = 'taylor order2', 
                                                                                             #~ shift_estimation_method ='optimize',
                                                                                             shift_method = 'spline',
                                                                                             max_iter = 6)
    
    step = spikesorter.history[-1]
    instance =  step['methodInstance']
    
    
    fig = pyplot.figure()
    instance.plot_iterative_centers(fig, spikesorter)
    
    
    pyplot.show()
    
    
    
    
    print spikesorter

    spikesorter.check_display_attributes()
    from OpenElectrophy.gui.spikesorting import AverageWaveforms, AllWaveforms

    app = QApplication([ ])
    w1 = AverageWaveforms(spikesorter = spikesorter)
    w1.refresh()
    w1.show()
    w2 = AllWaveforms(spikesorter = spikesorter)
    w2.refresh()
    w2.show()
    app.exec_()
    
    



if __name__ =='__main__':
    test1()
    
    

 
