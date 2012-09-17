# -*- coding: utf-8 -*-


from .waveforms import AverageWaveforms, AllWaveforms
from .features import FeaturesParallelPlot, FeaturesWilsonPlot, Features3D, FeaturesEvolutionInTime, FeaturesNDViewer
from .lists import SpikeList, UnitList
from .misc import Summary, PlotIsi, PlotCrossCorrelogram
from .signals import FullBandSignal, FilteredBandSignal, SignalStatistics

spikesorting_widget_list = [ AverageWaveforms, AllWaveforms,
                                                    FeaturesParallelPlot, FeaturesWilsonPlot, Features3D,FeaturesEvolutionInTime,FeaturesNDViewer,
                                                    SpikeList, UnitList, 
                                                    Summary, PlotIsi, PlotCrossCorrelogram,
                                                    FullBandSignal, FilteredBandSignal, SignalStatistics, 
                                                ]


