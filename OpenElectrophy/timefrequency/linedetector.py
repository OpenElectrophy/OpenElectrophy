# -*- coding: utf-8 -*-
"""

High level object for the detection of lines in the scalogram which 
represent transient oscillations.

"""



import numpy
from numpy import inf, nan




from .timefreq import TimeFreq, assume_quantity
from .maxdetection import max_detection
from .linedetection import detect_oscillations
from .clean import clean_oscillations_list

class LineDetector():
    """ 
    LineDetector(anaSig, 
                 scalogram_method = 'convolution_freq',
                 f_start=5.,
                 f_stop=100.,
                 deltafreq = 1.,
                 sampling_rate = 200.,
                 t_start = -inf, 
                 t_stop = inf,
                 f0=2.5, 
                 normalisation = 0.,
                 linedetection_method = 'detect_line_from_max',
                 detection_zone = [ 0, inf, 5, 100.],
                 manual_threshold = False,
                 abs_threshold = nan,
                 std_relative_threshold = 6.,
                 reference_zone = [ -inf, 0,5., 100.],
                 minimum_cycle_number= 0.,
                 eliminate_simultaneous = True,
                 regroup_full_overlap = True , 
                 eliminate_partial_overlap = True)    
    
    Class for line detection in the scalogram. 
    """
    def __init__(self,
                        anaSig,
                        
                        scalogram_method = 'convolution_freq',
                        #scalogram
                        f_start=5.,
                        f_stop=100.,
                        deltafreq = 1.,
                        sampling_rate = 200.,
                        t_start = -inf, 
                        t_stop = inf,
                        f0=2.5, 
                        normalisation = 0.,
                        optimize_fft=False,
                        
                        #~ linedetection_method = 'detect_all_lines',
                        linedetection_method = 'detect_line_from_max',
                        
                        
                        # detection_zone
                        detection_zone = [ 0, inf, 5, 100.],
                        
                        # threshold
                        manual_threshold = False,
                        abs_threshold = nan,
                        std_relative_threshold = 6.,
                        reference_zone = [ -inf, 0,5., 100.],
                        
                        # clean 
                        minimum_cycle_number= 0.,
                        eliminate_simultaneous = True,
                        regroup_full_overlap = True , 
                        eliminate_partial_overlap = True,                        
                        
                        ):
        """ 
    Construct a :class:`.LineDetector` object.
        
    Parameters
    ----------
    anaSig : AnalogSignal
        The AnalogSignal in which oscillations will be detected.    
    
    Scalogram parameters:
    
    f_start : float, optional
        Lower frequency bound (Hz) of scalogram
    f_stop : float, optional
        Upper frequency bound (Hz) of scalogram
    deltafreq : float, optional
        Frequency resolution of scalogram
    sampling_rate : float, optional
        Sampling rate of scalogram (Hz)
    t_start : float, optional
        Starting point of scalogram (s)
    t_stop : float, optional
        End point of scalogram (s)
    f0 : float, optional
        Number of cycles within one standard deviation of the Morlet wavelet.
    normalisation : float, optional
        Normalisation exponent along the frequency dimension. Negative 
        (positive) values stress lower (higher) frequencies.
    optimize_fft : False, optional
        Pad signal with 0 to have a size like 2**k before computing the time 
        frequency map, return the map truncated to original size
    
    Detection parameters
    
    detection_zone : array-like
        Time-frequency zone for oscillations detection of shape
        [t_start, t_stop, f_start, f_stop]        
    manual_threshold : bool, optional
        Boolean switch for manual thresholding 
    abs_threshold : float, optional
        Absolute power threshold for maxima detection
    std_relative_threshold : float, optional
        Threshold in units of of standard deviations from mean value in 
        reference_zone 
    reference_zone : array-like, optional
        Time-frequency reference zone for relative thresholding of shape
        [t_start, t_stop, f_start, f_stop]        
     
    Cleaning parameters
    
    minimum_cycle_number : float, optional
        Minimum number of cycles for cleaning of spurious oscillations
    eliminate_simultaneous : bool, optional
        Eliminate the less powerful oscillation of two oscillations overlapping
        in time but not in frequency, e.g. for the elimination of harmonics        
    regroup_full_overlap : bool, optional
        Merge oscillations completely overlapping in time and frequency, e.g.
        when one oscillations has several maximas in its envelope
    eliminate_partial_overlap : bool, optional
        Keep the more powerful oscillation of two partially overlapping
        oscillations, e.g. for the case of two forking ones
        
    Examples
    --------
    >>> ana = AnalogSignal.load(id)    
    >>> lid = LineDetector(ana)
    >>> lid.computeAllStep()        
        
        
        """
        self.anaSig = anaSig
        
        self.scalogram_method = scalogram_method
        
        self.f_start = f_start
        self.f_stop = f_stop
        self.deltafreq = deltafreq
        self.sampling_rate = sampling_rate
        self.t_start = t_start
        self.t_stop = t_stop
        self.f0= f0
        self.normalisation = normalisation
        self.optimize_fft = optimize_fft

        #~ self.t_start = max(self.t_start , self.anaSig.t_start)
        #~ self.t_stop = min(self.t_stop , self.anaSig.t()[-1] )
        
        self.linedetection_method = linedetection_method

        # detection_zone
        self.detection_zone = detection_zone
        
        #~ self.detection_zone[1] = min(self.detection_zone[1], self.anaSig.t()[-1] )
        
        # threshold
        self.manual_threshold = manual_threshold
        self.abs_threshold = abs_threshold
        self.std_relative_threshold = std_relative_threshold
        self.reference_zone = reference_zone

        # clean 
        self.minimum_cycle_number= minimum_cycle_number
        self.eliminate_simultaneous =eliminate_simultaneous
        self.regroup_full_overlap = regroup_full_overlap
        self.eliminate_partial_overlap = eliminate_partial_overlap
        
        self.checkParam()

        self.timeFreq = None
        self.threshold = inf
        self.list_max = None
    
    def update(self, **params):
        for k, v in params.items():
            setattr(self, k, v)
        #~ self.__dict__.update(params)
    
    def __setattr__(self,k,v):
        # here we check if quantites or not
        # for compatibilities
        if k in [ 'f_start', 'f_stop', 'sampling_rate', 'deltafreq' ]:
            self.__dict__[k] = assume_quantity(v, units = 'Hz')
        elif k in [ 't_start', 't_stop' ]:
            self.__dict__[k] = assume_quantity(v, units = 's')
        elif k in ['detection_zone', 'reference_zone']:
            v2 = [None]*4
            v2[0] = assume_quantity(v[0], units = 's')
            v2[1] = assume_quantity(v[1], units = 's')
            v2[2] = assume_quantity(v[2], units = 'Hz')
            v2[3] = assume_quantity(v[3], units = 'Hz')
            #~ print k, v2
            self.__dict__[k] = v2
        else:
            self.__dict__[k] = v
        #~ object.__setattr__(self,k,v)
    
    def checkParam(self):
        """ Perform checks and corrections to parameters t_start, t_stop, 
        sampling_rate, detection_zone[0] and detection_zone[1]. """
        self.t_start = max(self.t_start , self.anaSig.t_start)
        #~ self.t_stop = min(self.t_stop , self.anaSig.t()[-1]+1./self.anaSig.sampling_rate )
        self.t_stop = min(self.t_stop , self.anaSig.t_stop+self.anaSig.sampling_period )
        self.sampling_rate = max(self.f_stop*2, self.sampling_rate)
        
        #~ self.detection_zone[1] = min(self.detection_zone[1], self.anaSig.t()[-1]+1./self.anaSig.sampling_rate )
        self.detection_zone[1] = min(self.detection_zone[1], self.anaSig.t_stop+self.anaSig.sampling_period )
        self.reference_zone[0] = max(self.reference_zone[0], self.anaSig.t_start )
        #~ print  self.reference_zone
        
    
    def computeAllStep(self):
        """ Compute the scalogram (:func:`computeTimeFreq`), detects maxima 
        (:func:`detectMax`) and lines (:func:`detectLine`), and cleans the 
        detected oscillations (:func:`cleanLine`. """
        #~ self.checkParam()
        self.computeTimeFreq()
        self.detectMax()
        self.detectLine()
        self.cleanLine()        
    
    def computeTimeFreq(self):
        """ Compute the scalogram and returns a :class:`TimeFreq` object as
        self.timeFreq. """
        self.timeFreq  = TimeFreq(   self.anaSig,
                                                    f_start=self.f_start,
                                                    f_stop=self.f_stop,
                                                    deltafreq = self.deltafreq,
                                                    sampling_rate = self.sampling_rate,
                                                    t_start = self.t_start,
                                                    t_stop = self.t_stop,
                                                    f0=self.f0,
                                                    normalisation = self.normalisation,
                                                    optimize_fft=self.optimize_fft,
                                                )
    
    def computeThreshold(self):
        """ Either set self.threshold to the specified self.abs_threshold or 
        (re)compute the relative threshold and sets it. In both cases the 
        the threshold is returned. """
        if self.manual_threshold:
            self.threshold = self.abs_threshold
        else:
            map = self.timeFreq.map
            t = self.timeFreq.times
            f = self.timeFreq.freqs
            t1,t2,f1,f2 = self.reference_zone
            subMap =  map[ (t>=t1) & (t<t2), :][: ,  (f>=f1) & (f<f2)]
            #~ print subMap.shape, t1, t2
            subMap = abs(subMap)
            self.threshold = numpy.mean(subMap) + self.std_relative_threshold*numpy.std(subMap)
        return self.threshold
        
        
    
    def detectMax(self):
        """ Detect the maxima in the scalogram using :func:`max_detection`."""
        map = self.timeFreq.map
        t = self.timeFreq.times
        f = self.timeFreq.freqs
        t1,t2,f1,f2 = self.detection_zone
        subMap =  map[ (t>=t1) & (t<t2), :][: ,  (f>=f1) & (f<f2)]
        
        new_t =  t[ (t>=t1) & (t<t2) ]
        new_f = f[ (f>=f1) & (f<f2)]
        #~ print self.threshold
        self.computeThreshold()
        
        ind_t,ind_f = numpy.array(max_detection(abs(subMap),threshold= self.threshold))
        self.list_max = numpy.recarray(ind_t.size , formats = ['f8', 'f8'], names=['time', 'freq'] , )
        self.list_max.time  = new_t[ind_t].rescale('s').magnitude
        self.list_max.freq  = new_f[ind_f].rescale('Hz').magnitude
        
        
    def detectLine(self):
        """ Detect lines in the scalogram using self.linedetection_method. """
        map = self.timeFreq.map
        t = self.timeFreq.times
        f = self.timeFreq.freqs
        t1,t2,f1,f2 = self.detection_zone
        subMap =  map[ (t>=t1) & (t<t2), :][: ,  (f>=f1) & (f<f2)]
        new_t =  t[ (t>=t1) & (t<t2) ]
        new_f = f[ (f>=f1) & (f<f2)]
        
        self.computeThreshold()
        self.list_oscillation = detect_oscillations(subMap,
            new_t[0].rescale('s').magnitude,   #self.detection_zone[0],
            self.sampling_rate.rescale('Hz').magnitude,
            new_f[0].rescale('Hz').magnitude,   #self.detection_zone[3],
            self.deltafreq.rescale('Hz').magnitude,
            self.threshold,
            list_max =self.list_max,
            )

    def recomputeSelection(self , ind):
        pass


    def cleanLine(self):
        """ Clean all oscillations with selected parameters and sort them in time. """
        self.list_oscillation = clean_oscillations_list(self.list_oscillation,
            minimum_cycle_number=self.minimum_cycle_number,
            eliminate_simultaneous = self.eliminate_simultaneous,
            regroup_full_overlap = self.regroup_full_overlap,
            eliminate_partial_overlap = self.eliminate_partial_overlap,
                    )
        self.sortOscillations()
    
    
    def cleanSelection(self, ind):
        """ Clean only selected oscillations and sort them in time. """
        not_selected = [ ]
        selected = []
        for i in range(len(self.list_oscillation)):
            if i  in ind:
                selected.append( self.list_oscillation[i] )
            else:
                not_selected.append( self.list_oscillation[i] )
        
        list_cleaned = clean_oscillations_list(selected,
               minimum_cycle_number=self.minimum_cycle_number,
               eliminate_simultaneous = self.eliminate_simultaneous,
               regroup_full_overlap = self.regroup_full_overlap,
               eliminate_partial_overlap = self.eliminate_partial_overlap,
               )
        self.list_oscillation = list_cleaned + not_selected
        self.sortOscillations()
        
    
    def sortOscillations(self):
        """ Sort the detected oscillations by time. """
        t = [ ]
        for osci in self.list_oscillation:
            t.append( osci.time_max )
        ind = numpy.argsort(t)
        sorted = [ self.list_oscillation[i] for i in ind ]
        self.list_oscillation = sorted
            
        
        



