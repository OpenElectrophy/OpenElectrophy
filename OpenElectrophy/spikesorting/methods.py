



from filter.butterworth import ButterworthFilter
from detection.medianthreshold import MedianThresholdDetection 
from detection.stdthreshold import StdThresholdDetection
from waveform.ondetection import AlignWaveformOnDetection
from waveform.onpeak import AlignWaveformOnPeak
from feature.pcafeature import PcaFeature
from sorting.gmm_em import SklearnGaussianMixtureEm

all_methods = [ ButterworthFilter,
                StdThresholdDetection,
                MedianThresholdDetection,
                AlignWaveformOnDetection,
                AlignWaveformOnPeak,
                PcaFeature,
                SklearnGaussianMixtureEm,
                ]

