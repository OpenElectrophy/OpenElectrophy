"""
This module collects all methods in the framework.



Here a wish list of what we plan to implement:

  * Pouzat 2005 MCMC  "Efficient spike-sorting of multi-state neurons using
     inter-spike intervals information"
  * KTEO of Joo Choi T Kim
  * "A nonparametric Bayesian alternative to spike sorting" (Frank Wood )
  * "An online spike detection and spike classification algorithm
    capable of instantaneous resolution of overlapping spikes", F Franke
  * Waveform alignement that minimize variance
  * Automated spike sorting algorithm based on laplacian
    eigenmaps and k-means clustering (E Chah)
  * Spike sorting: Bayesian clustering of non-stationary data (Aharon Bar-Hillel a)
  *  "Dependent Dirichlet Process Spike Sorting" , Jan Gasthaus>>> The author release to us the code as open source!!!
  * Kalman filter mixture model for spike sorting of non-stationary data, Ana Calabrese 
  * "Unsupervised Spike Detection and Sorting with Wavelets and
    Superparamagnetic Clustering", R. Quian Quiroga


"""



from .filter.butterworth import ButterworthFilter
from .filter.derivative import DerivativeFilter
from .filter.slidingmedian import SlidingMedianFilter
from .detection.relativethreshold import RelativeThresholdDetection
from .detection.manualthreshold import ManualThresholdDetection
from .detection.mteo import MTEODetection
from .waveform.ondetection import AlignWaveformOnDetection
from .waveform.onpeak import AlignWaveformOnPeak
from .waveform.oncentralwaveform import AlignWaveformOnCentralWaveform
from .feature.pcafeature import PcaFeature
from .feature.icafeature import IcaFeature
from .feature.combine import CombineFeature
from .feature.allpeak import AllPeak
from .feature.peaktovalley import PeakToValley
from .feature.haarwavelet import HaarWaveletFeature
from .sorting.gmm_em import SklearnGaussianMixtureEm
from .sorting.kmeans import SklearnKMeans
from .sorting.minibatchkmeans import SklearnMiniBatchKMeans
from .sorting.meanshift import SklearnMeanShift
from .clean.outtemplate import OutsideTemplateCleaning


all_methods = [ ButterworthFilter,
                DerivativeFilter,
                SlidingMedianFilter,
                RelativeThresholdDetection,
                ManualThresholdDetection,
                MTEODetection,
                AlignWaveformOnDetection,
                AlignWaveformOnPeak,
                AlignWaveformOnCentralWaveform,
                CombineFeature, 
                AllPeak,
                PeakToValley,
                PcaFeature,
                IcaFeature,
                HaarWaveletFeature,
                SklearnGaussianMixtureEm,
                SklearnKMeans,
                SklearnMiniBatchKMeans,
                SklearnMeanShift,
                OutsideTemplateCleaning,
                ]



