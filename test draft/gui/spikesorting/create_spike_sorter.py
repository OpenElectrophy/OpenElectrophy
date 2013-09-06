import sys
sys.path.append('../../..')

from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings
from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy.core import OEBase, open_db
#~ from OpenElectrophy.core.base import OEBase
import os

import quantities as pq
import numpy as np

#~ if os.path.exists('test_spikesorting.sqlite'):
    #~ os.remove('test_spikesorting.sqlite')



url = 'sqlite:///test_spikesorting.sqlite'
dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
session = dbinfo.Session()
oebl = session.query(Block).first()
if oebl is None:
    print 'do not exists: so create'
    bl = generate_block_for_sorting(nb_unit = 6,
                                                        duration = 30.*pq.s,
                                                        noise_ratio = 0.2,
                                                        nb_segment = 2,
                                                        )
    #~ for s, seg in enumerate(bl.segments):
        #~ for k, sptr in enumerate(seg.spiketrains):
            #~ print 's', s, 'k', k, sptr.size
    print bl.recordingchannelgroups
    oebl = OEBase.from_neo(bl, dbinfo.mapped_classes, cascade =True)
    print oebl.recordingchannelgroups
    oebl.save()
else:
    print 'exist : transform to neo'
    bl = oebl.to_neo(cascade = True)
rcg = bl.recordingchannelgroups[0]


sps = spikesorter = SpikeSorter(rcg)

if True:
    #~ spikesorter.ButterworthFilter( f_low = 200.)
    #~ spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
    #~ spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
    #~ spikesorter.PcaFeature(n_components = 4)
    spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
    spikesorter.SklearnKMeans(n_cluster = 5)

    
    
spikesorter.check_display_attributes()
print spikesorter

