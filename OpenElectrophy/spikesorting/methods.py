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



from filter.butterworth import ButterworthFilter
from filter.MTEO import MTEOFilter
from detection.medianthreshold import MedianThresholdDetection 
from detection.stdthreshold import StdThresholdDetection
from waveform.ondetection import AlignWaveformOnDetection
from waveform.onpeak import AlignWaveformOnPeak
from feature.pcafeature import PcaFeature
from sorting.gmm_em import SklearnGaussianMixtureEm
from sorting.kmeans import SklearnKMeans
from sorting.minibatchkmeans import SklearnMiniBatchKMeans
from sorting.meanshift import SklearnMeanShift

all_methods = [ ButterworthFilter,
                MTEOFilter,
                StdThresholdDetection,
                MedianThresholdDetection,
                AlignWaveformOnDetection,
                AlignWaveformOnPeak,
                PcaFeature,
                SklearnGaussianMixtureEm,
                SklearnKMeans,
                SklearnMiniBatchKMeans,
                SklearnMeanShift,
                ]



