# -*- coding: utf-8 -*-
"""
A widget for apply spike sorting chain and related parameters.
"""

from collections import OrderedDict
from .parameters import *

class SpikeSortingToolChain(object):
    """
    a SpikeSortingToolChain is define by a suite of of methods available in OpenElectrophy.spikesortign.methods
    Example 1, from full band signal to clustered spike:
      * [ButterworthFilter] > [MedianThresholdDetection or StdThresholdDetection ] >
          [AlignWaveformOnPeak or AlignWaveformOnDetection] > [PcaFeature or IcaFeature] > [SklearnKMeans or SklearnGaussianMixtureEm]
    Example 2, only detection on onready filterred signal
      * MedianThresholdDetection or StdThresholdDetection
    
    """
    name = ''
    chain = [ ]


# famillies
filters = [ ButterworthFilter, ]
detections = [  MedianThresholdDetection, StdThresholdDetection, ManualThresholdDetection, MTEODetection]
waveforms = [ AlignWaveformOnDetection, AlignWaveformOnPeak ]
features = [ PcaFeature, IcaFeature,CombineFeature, AllPeak, PeakToValley, HaarWaveletFeature]
sorting = [SklearnGaussianMixtureEm, SklearnKMeans, SklearnMiniBatchKMeans, SklearnMeanShift ]



class FromFullBandSignalToClustered(SpikeSortingToolChain):
    name = 'from full band signal to clustered spike'
    chain = OrderedDict([
                                            [ 'filters', filters],
                                            [ 'detections', detections],
                                            [ 'waveforms', waveforms],
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])

class FromFilteredBandSignalToClustered(SpikeSortingToolChain):
    name = 'from filtered band signal to clustered spike'
    chain = OrderedDict([
                                            [ 'detections', detections],
                                            [ 'waveforms', waveforms],
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])
    


class FromWaveformToClustered(SpikeSortingToolChain):
    name = 'from waveform to clustered spike'
    chain = OrderedDict([
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])


#~ # This is for you Chris:
class FromFeatureToClustered(SpikeSortingToolChain):
    name = 'from feature to clustered spike'
    chain = OrderedDict([
                                            [ 'sorting', sorting],
                                            ])


class FromFullBandSignalToDetection(SpikeSortingToolChain):
    name = 'from full band signal to detected spike'
    chain = OrderedDict([
                                            [ 'filters', filters],
                                            [ 'detections', detections],
                                            ])

    

all_toolchain = [FromFullBandSignalToClustered, FromFilteredBandSignalToClustered,
                            FromWaveformToClustered, FromFeatureToClustered, FromFullBandSignalToDetection,
                            ]


class MultiMethodsParamWidget(QWidget):
    def __init__(self, parent = None, settings = None, title = None,
                            methods = [ ]):
        super(MultiMethodsParamWidget, self).__init__(parent =parent)
        
        self.settings = settings
        self.methods = methods
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        if title is not None:
            self.mainLayout.addWidget(QLabel(title))
            
        self.param_widget = None
        
        self.combo = QComboBox()
        self.mainLayout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.display_params)
        self.combo.addItems([ method.name for method in self.methods])
    
    def display_params(self, pos):
        if self.param_widget is not None :
            self.param_widget.setVisible(False)
            self.mainLayout.removeWidget(self.param_widget)
        if pos<0: return
        self.method = self.methods[pos]
        if self.method.dataset is not None:
            self.param_widget  = ParamWidget( self.method.dataset, title = self.method.name,
                                                    settings = self.settings, settingskey = 'spikesortings/methods/'+self.method.name)
        else:
            self.param_widget = QWidget()
        self.mainLayout.addWidget(self.param_widget,1)
        
    #~ def get_method(self) :
        #~ return self.method
    
    #~ def get_name(self):
        #~ return self.method.name
    
    def get_dict(self) :
        if self.method.dataset is not None:
            return self.param_widget.to_dict()
        else:
            return {}

class ToolChainWidget(QWidget):
    def __init__(self, parent = None, spikesorter = None, settings = None):
        super(ToolChainWidget, self).__init__(parent =parent)
        self.spikesorter = spikesorter
        self.settings = settings
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.toolbox = None
    
    def change_toolchain(self, toolchain):
        self.toolchain = toolchain
        if self.toolbox is not None:
            self.toolbox.setVisible(False)
            self.mainLayout.removeWidget(self.toolbox)
        
        self.toolbox = QToolBox()
        self.mainLayout.addWidget(self.toolbox)
        i = 0
        for name, methods in toolchain.chain.items():
            i+=1
            w = MultiMethodsParamWidget(methods = methods, settings = self.settings)
            self.toolbox.addItem(w,QIcon(':/'+name+'.png'), '{} - {}'.format(i,name))
            
            
        
        
        



