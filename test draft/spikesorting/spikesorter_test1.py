import sys
sys.path.append('../..')

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy import *

import quantities as pq
import numpy as np



def test1():
    bl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 10.*pq.s,
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    rcg = bl.recordingchannelgroups[0]

    spikesorter = SpikeSorter(rcg)

    spikesorter.ButterworthFilter( f_low = 200.)
    spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
    spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
    spikesorter.PcaFeature(n_components = 4)
    spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
    spikesorter.SklearnKMeans(n_cluster = 3)


    for u, unit in enumerate(rcg.units):
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print 'u', u, 's', s, seg.spiketrains[u] is unit.spiketrains[s], sptr.size


    rcg = spikesorter.populate_recordingchannelgroup()
    
    print 
    
    for u, unit in enumerate(rcg.units):
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print 'u', u, 's', s, seg.spiketrains[u] is unit.spiketrains[s], sptr.size
    
    
    
def test2():
    url = 'sqlite:///test_spikesorter.sqlite'
    dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
    session = dbinfo.Session()
    
    bl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 10.*pq.s,
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    rcg = bl.recordingchannelgroups[0]
    oebl = OEBase.from_neo(bl, dbinfo.mapped_classes, cascade =True)
    #~ print oebl is  bl.OEinstance
    oebl.save()
    id_bl = oebl.id

    for u, unit in enumerate(rcg.units):
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print 'u', u, 's', s, seg.spiketrains[u] is unit.spiketrains[s], sptr.size
    
    
    spikesorter = SpikeSorter(rcg)

    spikesorter.ButterworthFilter( f_low = 200.)
    spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
    spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
    spikesorter.PcaFeature(n_components = 4)
    spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
    spikesorter.SklearnKMeans(n_cluster = 3)


    spikesorter.save_in_database(session, dbinfo)
    
    dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
    session = dbinfo.Session()
    oebl = Block.load(id_bl)
    
    rcg = oebl.recordingchannelgroups[0]
    for s, seg in enumerate(rcg.block.segments):
        print 's', s, len(seg.spiketrains)
    
    for u, unit in enumerate(rcg.units):
        print 'u',u,  len(unit.spiketrains)
    
    for u, unit in enumerate(rcg.units):
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print 'u', u, 's', s, seg.spiketrains[u] is unit.spiketrains[s], sptr.to_neo().size
    


if __name__ =='__main__':
    #~ test1()
    test2()