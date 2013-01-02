# -*- coding: utf-8 -*-
"""
Time frequency and matplotlib
-----------------------------------------------

The TimeFreq class offer a simple way to compute morlet scalogram of an analogsignal and 
plot it in matplotlib.

Note that TimeFreq deal with neo object.


"""

import sys
sys.path.append('..')

if __name__== '__main__':

    
    from OpenElectrophy.timefrequency import TimeFreq
    from OpenElectrophy import TryItIO
    from matplotlib import pyplot
    
    bl = TryItIO().read(nb_segment=1, duration = 10)
    ana = bl.segments[0].analogsignals[0]    
    
    
    # compute the map
    tfr = TimeFreq(ana,
                            f_start = 10.,
                            f_stop = 93.,
                            deltafreq = .5,
                            f0 = 2.5,
                            )
    print tfr.freqs
    print tfr.times
    print tfr.map.shape, tfr.map.dtype
    
    
    # plot it
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    tfr.plot(ax,  clim = [0,3])
    pyplot.show()