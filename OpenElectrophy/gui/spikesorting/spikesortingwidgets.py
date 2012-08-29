# -*- coding: utf-8 -*-


from .waveforms import AverageWaveforms, AllWaveforms
from .features import FeaturesParallelPlot, FeaturesWilsonPlot

spikesorting_widget_list = [ AverageWaveforms, AllWaveforms,
                                                FeaturesParallelPlot, FeaturesWilsonPlot, 
                                                ]
                                        #~ FullBandSignal , FilteredSignal ,   SignalStatistics,
                                        #~ FeaturesNDViewer,  Features3D , 
                                        #~ SpikeList, UnitList,
                                        #~ PlotIsi,PlotCrossCorrelogram, FeaturesEvolutionInTime,
                                        #~ Summary,
                                        #~ ]