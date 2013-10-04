# -*- coding: utf-8 -*-


from .waveforms import AverageWaveforms, AllWaveforms
from .features import FeaturesParallelPlot, FeaturesWilsonPlot, Features3D, FeaturesEvolutionInTime, FeaturesNDViewer
from .lists import SpikeList, UnitList
from .misc import Summary, PlotIsi, PlotCrossCorrelogram
from .signals import FullBandSignal, FilteredBandSignal, SignalStatistics

spikesorting_widget_list = [ AverageWaveforms, AllWaveforms,
                                                    FeaturesNDViewer, FeaturesParallelPlot, FeaturesWilsonPlot, Features3D,FeaturesEvolutionInTime,
                                                    SpikeList, UnitList, 
                                                    Summary, PlotIsi, PlotCrossCorrelogram,
                                                    FullBandSignal, FilteredBandSignal, SignalStatistics, 
                                                ]

for w in spikesorting_widget_list:
    w.prefered_position = 'UpperRight'
    w.tabified_with =[ ]


SpikeList.prefered_position = 'AboveToolChain'
UnitList.prefered_position = 'AboveToolChain'



AverageWaveforms.tabified_with = [ AllWaveforms ]
FeaturesNDViewer.tabified_with = [  FeaturesParallelPlot, FeaturesWilsonPlot, Features3D,FeaturesEvolutionInTime ]
FullBandSignal.tabified_with =[ FilteredBandSignal ]
PlotCrossCorrelogram.tabified_with = [Summary, PlotIsi, SignalStatistics]

# make it bi directional
for w1 in spikesorting_widget_list:
    for w2 in w1.tabified_with:
        if w1 not in w2.tabified_with:
            w2.tabified_with.append(w1)
    #~ print w1, w1.tabified_with

