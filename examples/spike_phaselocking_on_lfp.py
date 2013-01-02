# -*- coding: utf-8 -*-
"""
Spike phase locking on LFP
-----------------------------------------------

The question of what is the preferred discharge phase on LFP oscillation of a particular neuron is largely covered by the
bibliography. Many people extract the phase with Hilbert transform and get the phase for each spike.
Other people do spike trigger averaging  hoping that a neighborhood will transduce an attractive phase of the oscillation.

This question can also be approached in OpenElectrophy with the `S. Roux method <http://www.ncbi.nlm.nih.gov/pubmed/17049617>`_


You can have 2 cases :
 * the phase of a SpikeTrain on the LFP of its own electrode
 * 2 different electrodes: one for spikes and one for LFP oscillation

Read carefully the oscillation page before.

In short, after pre-processing, you have a database now filled with:
 * detected spike trains
 * detected transitory oscillations

To get the instantaneous phase is a child play because the Oscillation object contains **value_line** and **time_line**
 and **freq_line** vectors. **value_line** is complex and can give the instantaneous phase point by point of the **time_line**.
 
The Oscillation object also offers the method Oscillation.phase_of_times( a_time_serie) that return the corresponding phases for any time serie.
For all point outside time_start ~ time_stop a *nan* is return otherwise the instantaneous phase is returned.




"""



import sys
sys.path.append('..')


if __name__== '__main__':
    
    # imports
    from OpenElectrophy import *
    from OpenElectrophy.timefrequency import LineDetector, PlotLineDetector
    from OpenElectrophy.spikesorting import SpikeSorter
    
    from matplotlib import pyplot
    from scipy import *
    import numpy as np
    import quantities as pq
    

    dbinfo = open_db( url = 'sqlite:///spike_and_lfp.sqlite', myglobals= globals(), use_global_session = True)
 
    
    ## GENERATING DATASET
    neo_bl = TryItIO().read(nb_segment=1, duration = 10)
    neo_ana = neo_bl.segments[0].analogsignals[0]
    
    bl = neo_to_oe(neo_bl, cascade = True)
    bl.save()

    ## detect  oscillations
    linedetector  = LineDetector(neo_ana, 
                 f_start=5.,
                 f_stop=100.,
                 deltafreq = 1.,
                 sampling_rate = 400.,
                 f0=2.5, 
                 normalisation = 0.,
                 detection_zone = [ 0, np.inf, 25, 80.],
                 manual_threshold = False,
                 abs_threshold = np.nan,
                 std_relative_threshold = 6.,
                 reference_zone = [ -np.inf, 0,25., 80.],
                 minimum_cycle_number= 0.,
                 eliminate_simultaneous = True,
                 regroup_full_overlap = True , 
                 eliminate_partial_overlap = True)        
    linedetector.computeAllStep()
    
    fig = pyplot.figure()
    pld = PlotLineDetector(figure = fig, lineDetector = linedetector)
    pld.reDrawAll()

    ## detect spikes
    neo_rcg = neo_bl.recordingchannelgroups[0]
    spikesorter = SpikeSorter(neo_rcg)
    spikesorter.ButterworthFilter( f_low = 200.)
    spikesorter.MedianThresholdDetection(sign= '-',median_thresh = 6)
    spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms ,right_sweep = 2*pq.ms)
    spikesorter.PcaFeature(n_components = 6)
    spikesorter.SklearnGaussianMixtureEm(n_cluster = 6, n_iter = 200 )    
    
    neo_rcg = spikesorter.populate_recordingchannelgroup()


    ##  PHASE LOCKING : loop over neuron and oscillation
    for unit in neo_rcg.units:
        all_phase = [ ]
        # we have only one segment sso only one spiketrain by unit
        sptr = unit.spiketrains[0]
        for osc in linedetector.list_oscillation:
            # sampling_rate is the precision of the oscillation
            # you can put the original data sampling rate but 1000 (1 ms) is good enought)
            phase = osc.phase_of_times( sptr.rescale('s').magnitude , sampling_rate = 1000.)
            # remove nan
            all_phase.append(phase[~np.isnan(phase)])
        all_phase = np.concatenate(all_phase, axis = 0)
        
        binsize = pi/10
        bins = arange(-pi , pi + binsize , binsize)
        count , bins2 = histogram( all_phase , bins = bins)

        fig = pyplot.figure()
        ax = fig.add_subplot(1,1,1)
        ax.set_title('Phase of neuron {}'.format(unit.name))
        ax.bar( bins2[:-1] , count , width  = binsize*0.9)
        ax.set_xlim(-pi , pi)

    pyplot.show()
    
