import sys
import os

sys.path.append('../..')

from OpenElectrophy.core.tools import *
from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting
from OpenElectrophy.core import OEBase, open_db

import quantities as pq


url = 'sqlite:///'
dbinfo = open_db(url = url, use_global_session = True)
#~ session = dbinfo.Session()


def test1():
    bl1 = generate_block_for_sorting(nb_unit = 2,
                                                        duration = 3.*pq.s,
                                                        nb_segment = 2,
                                                        )
    oebl1 = OEBase.from_neo(bl1, dbinfo.mapped_classes, cascade =True)
    oebl1.save()

    bl2 = generate_block_for_sorting(nb_unit = 3,
                                                        duration = 2.5*pq.s,
                                                        nb_segment = 1,
                                                        )    
    oebl2 = OEBase.from_neo(bl2, dbinfo.mapped_classes, cascade =True)
    oebl2.save()
    
    oebl3 = merge_blocks([oebl1, oebl2], )
    
    print 'name', oebl3.name
    #~ print oebl3.recordingchannelgroups
    for rcg in oebl3.recordingchannelgroups:
        print '#'*3
        print rcg
        for rc in rcg.recordingchannels:
            print rc
    
    


if __name__ == '__main__':
    test1()

