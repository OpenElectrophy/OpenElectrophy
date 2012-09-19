# -*- coding: utf-8 -*-
"""
This module provide guidataDataSet for gui parameters for all spikesorting.methods.
"""



from ..guiutil.myguidata import *
from ...spikesorting.methods import *


####
## Detection
class ButterworthFilter_DataSet(DataSet):
    f_low = FloatItem('Low cut frequency',200.)
    N = IntItem('order N', 5)
ButterworthFilter.dataset = ButterworthFilter_DataSet

class MedianThresholdDetection_DataSet(DataSet):
    sign = ChoiceItem('Sign of peak', ['-', '+'])
    median_thresh = FloatItem('Median threshold',5.)
    consistent_across_channels = BoolItem('Consistent across channels', default = False)
    consistent_across_segments = BoolItem('Consistent across segments', default = True)
    #~ merge_method = 'fast'
    # TODO Quantities item
    #~ sweep_clean_size = 0.8*pq.ms
MedianThresholdDetection.dataset = MedianThresholdDetection_DataSet

class StdThresholdDetection_DataSet(DataSet):
    sign = ChoiceItem('Sign of peak', ['-', '+'])
    std_thresh = FloatItem('Std threshold',5.)
    consistent_across_channels = BoolItem('Consistent across channels', default =  False)
    consistent_across_segments = BoolItem('Consistent across segments', default = True)
    # TODO Quantities item
    #~ sweep_clean_size = 0.8*pq.ms
StdThresholdDetection.dataset = StdThresholdDetection_DataSet

class ManualThresholdDetection_DataSet(DataSet):
    sign = ChoiceItem('Sign of FRONT', ['-', '+'])
    std_thresh = FloatItem('Absolut threshold (can be + or -) ',-1)
    # TODO Quantities item
    #~ sweep_clean_size = 0.8*pq.ms
ManualThresholdDetection.dataset = ManualThresholdDetection_DataSet

class MTEODetection_DataSet(DataSet):
    k_max= IntItem( 'k_max',1)
    k_inc= IntItem( 'k_inc',1)
    from_fullband=BoolItem('From full band',default =  False)
    median_thresh = FloatItem('Median threshold',5.)
    consistent_across_channels = BoolItem('Consistent across channels', default = False)
    consistent_across_segments = BoolItem('Consistent across segments', default = True)
    # TODO Quantities item
    #~ sweep_clean_size = 0.8*pq.ms
MTEODetection.dataset = MTEODetection_DataSet

####
## Waveform alignement
class AlignWaveformOnDetection_DataSet(DataSet):
    sign = ChoiceItem('Sign of peak', ['-', '+'])
    #~ left_sweep = 1*pq.ms
    #~ right_sweep = 1*pq.ms
AlignWaveformOnDetection.dataset = AlignWaveformOnDetection_DataSet

class AlignWaveformOnPeak_DataSet(DataSet):
    sign = ChoiceItem('Sign of peak', ['-', '+'])
    #~ left_sweep = 1*pq.ms
    #~ right_sweep = 1*pq.ms
AlignWaveformOnPeak.dataset = AlignWaveformOnPeak_DataSet

####
## Features extraction
class PcaFeature_DataSet(DataSet):
    n_components = IntItem( 'n_components',4)
PcaFeature.dataset = PcaFeature_DataSet

class IcaFeature_DataSet(DataSet):
    n_components = IntItem( 'n_components',4)
IcaFeature.dataset = IcaFeature_DataSet

class AllPeak_DataSet(DataSet):
    sign = ChoiceItem('Sign of peak', ['-', '+'])
AllPeak.dataset = AllPeak_DataSet

class PeakToValley_DataSet(DataSet):
    pass
PeakToValley.dataset = None

class HaarWaveletFeature_DataSet(DataSet):
    n_components = IntItem( 'n_components',4)
    level = IntItem( 'level',4)
    std_restrict = FloatItem('std_restrict', 3.)
HaarWaveletFeature.dataset = HaarWaveletFeature_DataSet

class CombineFeature_DataSet(DataSet):
    use_peak = BoolItem('use_peak', True)
    use_peak_to_valley = BoolItem('use_peak_to_valley',default =  True)
    n_pca = IntItem( 'n_pca',4)
    n_ica = IntItem( 'n_ica',4)
    n_haar = IntItem( 'n_haar',4)
    sign = ChoiceItem('Sign of peak', ['-', '+'])
CombineFeature.dataset = CombineFeature_DataSet


####
## Sorting
class SklearnGaussianMixtureEm_DataSet(DataSet):
    n_cluster = IntItem( 'n_cluster', 4)
    n_iter = IntItem( 'n_iter', 20)
SklearnGaussianMixtureEm.dataset = SklearnGaussianMixtureEm_DataSet

class SklearnKMeans_DataSet(DataSet):
    n_cluster = IntItem( 'n_cluster', 8)    
    init =  ChoiceItem('Initilisation method', ['k-means++', 'random'])
    n_init = IntItem( 'n_init', 10)
    max_iter = IntItem( 'max_iter', 300)
SklearnKMeans.dataset = SklearnKMeans_DataSet

class SklearnMiniBatchKMeans_DataSet(DataSet):
    n_cluster = IntItem( 'n_cluster', 8)    
    init =  ChoiceItem('Initilisation method', ['k-means++', 'random'])
    batch_size = IntItem( 'batch_size', 100)
    max_iter = IntItem( 'max_iter', 300)
SklearnMiniBatchKMeans.dataset = SklearnMiniBatchKMeans_DataSet

class SklearnMeanShift_DataSet(DataSet):
    quantile = FloatItem('quantile', 0.2)
    n_samples = IntItem('n_samples', 500)
    bin_seeding = BoolItem('bin_seeding', default = True)
    cluster_all = BoolItem('cluster_all',default = False)
SklearnMeanShift.dataset = SklearnMeanShift_DataSet



