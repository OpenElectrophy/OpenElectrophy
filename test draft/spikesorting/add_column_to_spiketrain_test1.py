import sys
sys.path.append('../..')

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy import *

import quantities as pq
import numpy as np


    
def test1():
    # open DB and create new column
    url = 'sqlite:///test_spikesorter.sqlite'
    dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
    session = dbinfo.Session()
    

    for attrname, attrtype in dbinfo.classes_by_name['SpikeTrain'].usable_attributes.items():
        print attrname, attrtype

    
    #Create acolumn on table SpikeTrain (maybe this could be store at Unit level)
    create_column_if_not_exists(dbinfo.metadata.tables['SpikeTrain'],'detection_thresholds', np.ndarray)
    
    #test is creation is OK
    for attrname, attrtype in dbinfo.classes_by_name['SpikeTrain'].usable_attributes.items():
        print attrname, attrtype
    
    
    
    
    # re open DB for sorting
    url = 'sqlite:///test_spikesorter.sqlite'
    dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
    session = dbinfo.Session()
    print dbinfo.classes_by_name['SpikeTrain']
    for attrname, attrtype in dbinfo.classes_by_name['SpikeTrain'].usable_attributes.items():
        print attrname, attrtype
    
    
    neobl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 10.*pq.s,
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    neorcg = neobl.recordingchannelgroups[0]
    bl = OEBase.from_neo(neobl, dbinfo.mapped_classes, cascade =True)
    bl.save()
    rcg = OEBase.from_neo(neorcg, dbinfo.mapped_classes, cascade =True)
    rcg_id = rcg.id
    
    # spike sorting chain
    spikesorter = SpikeSorter(neorcg)
    spikesorter.ButterworthFilter( f_low = 200.)
    spikesorter.RelativeThresholdDetection(sign= '-', relative_thresh = 6.,)
    spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
    spikesorter.PcaFeature(n_components = 4)
    spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
    spikesorter.SklearnKMeans(n_cluster = 3)
    spikesorter.save_in_database(session, dbinfo)
    
    
    # Note that threshold is per channel/segment
    for unit in rcg.units:
        for sptr in unit.spiketrains:
            print 'writte threshold on spiketrain.id',sptr.id
            print spikesorter.detection_thresholds
            sptr.detection_thresholds = spikesorter.detection_thresholds
    session.commit()

    
    # re open DB for sorting for reading
    dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
    session = dbinfo.Session()
    rcg = RecordingChannelGroup.load(rcg_id)
    for unit in rcg.units:
        for sptr in unit.spiketrains:
            print 'read threshold on spiketrain.id',sptr.id
            print sptr.detection_thresholds



if __name__ =='__main__':
    test1()