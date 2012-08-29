# -*- coding: utf-8 -*-
"""
This example show how to use spike sorting framework in a iptyhon console

from iptyhon 0.11 version you need first to active your GUI::
    %gui qt

See: http://ipython.org/ipython-doc/stable/interactive/reference.html#gui-support


After that each spikesorting widget availbale in main GUI are accesible directly in the console.
You need to instanstiate them with::
    spikesorter = SpikeSorter(...)
    w1 = ASpikeSortingWidget(spikesorter = spikesorter)
    w2 = AnotherSpikeSortingWidget(spikesorter = spikesorter)
    w1.show()
    w2.show()

Each time you apply steps and want to see results:
    w1.refresh()
    w2.refresh()

If you have closed your widget, you can show them again of course::
    w1.show()
    w2.show()

"""


# DO NOT FORGET this IPython comand
%gui qt

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
import quantities as pq
# generate dataset
bl = generate_block_for_sorting(nb_unit = 6,
                                                    duration = 10.*pq.s,
                                                    noise_ratio = 0.2,
                                                    nb_segment = 2,
                                                    )
rcg = bl.recordingchannelgroups[0]
spikesorter = SpikeSorter(rcg, initial_state='full_band_signal')


# Apply a chain
spikesorter.ButterworthFilter( f_low = 200.)
spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')


# display widget interactivively
from OpenElectrophy.gui.spikesorting import AverageWaveforms
w1 = AverageWaveforms(spikesorter = spikesorter)
w1.show()


# test another step methods
spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms)
w1.refresh()







