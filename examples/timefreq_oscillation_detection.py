# -*- coding: utf-8 -*-
"""
Transient oscillation detection
-----------------------------------------------

OpenElectrophy offers a tool for detection of transient oscillations based on ridge detection
on a morlet scalogram and represents oscillations as complex-valued time-frequency lines.

This tools is accessible througth the UI.

If you want to play with this framework through a script it is possible with:
LineDetector class for computing
and
PlotLineDetector class for plotting results.



"""

import sys
sys.path.append('..')


if __name__== '__main__':
    from OpenElectrophy.timefrequency import LineDetector, PlotLineDetector
    from OpenElectrophy import TryItIO
    from matplotlib import pyplot
    import numpy as np
    import quantities as pq

    
    
    bl = TryItIO().read(nb_segment=1, duration = 10)
    ana = bl.segments[0].analogsignals[0]    


    linedetector  = LineDetector(ana, 
                 f_start=5.,
                 f_stop=100.,
                 deltafreq = 1.,
                 sampling_rate = 400.,
                 f0=2.5, 
                 normalisation = 0.,
                 detection_zone = [ 0, np.inf, 25, 80.],
                 manual_threshold = False,
                 abs_threshold = np.nan,
                 std_relative_threshold = 6.,
                 reference_zone = [ -np.inf, 0,25., 80.],
                 minimum_cycle_number= 0.,
                 eliminate_simultaneous = True,
                 regroup_full_overlap = True , 
                 eliminate_partial_overlap = True)        
    linedetector.computeAllStep()
    
    fig = pyplot.figure()
    pld = PlotLineDetector(figure = fig, lineDetector = linedetector)
    pld.reDrawAll()
    pyplot.show()
