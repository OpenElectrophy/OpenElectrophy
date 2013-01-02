# -*- coding: utf-8 -*-
"""
SpikeSorter and viewer
-----------------------------------------------

In IPython you can also open Qt widget.

So it is possible to use SpikeSorter object with console and see the result in 
Qt widget.

All widget are the same than in the main UI.


"""

import sys
sys.path.append('..')

if __name__== '__main__':

    import quantities as pq
    from OpenElectrophy.spikesorting import (generate_block_for_sorting, SpikeSorter)
    
    from OpenElectrophy.gui.spikesorting import AverageWaveforms, FeaturesNDViewer, FilteredBandSignal
        
    # read or create datasets
    bl = generate_block_for_sorting(nb_unit = 6,
                                duration = 5.*pq.s,
                                noise_ratio = 0.2,
                                )
    rcg = bl.recordingchannelgroups[0]
    spikesorter = SpikeSorter(rcg)
    
    # Apply a chain
    spikesorter.ButterworthFilter( f_low = 200.)
    # equivalent to
    # spikesorter.run_step(ButterworthFilter, f_low = 200.)
    spikesorter.MedianThresholdDetection(sign= '-',median_thresh = 6)
    spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms ,right_sweep = 2*pq.ms)
    spikesorter.PcaFeature(n_components = 6)
    spikesorter.SklearnGaussianMixtureEm(n_cluster = 6, n_iter = 200 )

    from PyQt4.QtGui import QApplication
    app = QApplication([ ])
    
    spikesorter.check_display_attributes()
    
    w1 = AverageWaveforms(spikesorter = spikesorter)
    w2 = FeaturesNDViewer(spikesorter = spikesorter)
    w3 = FilteredBandSignal(spikesorter = spikesorter)
    
    all=[w1, w2, w3]
    for w in all:
        w.refresh()
        w.show()
    
    
    app.exec_()
    
    
    
    
    
