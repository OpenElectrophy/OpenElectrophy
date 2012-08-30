# -*- coding: utf-8 -*-


from .waveforms import AverageWaveforms, AllWaveforms
from .features import FeaturesParallelPlot, FeaturesWilsonPlot, Features3D, FeaturesEvolutionInTime, FeaturesNDViewer

spikesorting_widget_list = [ AverageWaveforms, AllWaveforms,
                                                FeaturesParallelPlot, FeaturesWilsonPlot, Features3D,FeaturesEvolutionInTime,FeaturesNDViewer, 
                                                ]
                                        #~ FullBandSignal , FilteredSignal ,   SignalStatistics,
                                        #~ SpikeList, UnitList,
                                        #~ PlotIsi,PlotCrossCorrelogram, ,
                                        #~ Summary,
                                        #~ ]