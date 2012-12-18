# -*- coding: utf-8 -*-
"""
SqlAlchemy magic relationship
---------------------------------------------------

OpenEletrophy uses sqlalchemy for mapping databases.

sqlalchemy allows you to explore a tree without writing any sql with
the *relationship* macanism.

In OpenElectrophy, the convention when an object want to acces
relationship are the same in neo (note the lower case):
    * its children is  object.childname+s. Ex: Segment.analogsignals
    * its parents is object.parentname Ex: AnalogSIgnal.segment
    * its many to many relationhsip Ex : RecordingChannelGroup.recordingchannels


Be aware that each call to this is a query on the database.
It mean that by default relationship are loaded on demand.

The behavior of that relationship can be change with relationship_lazy = 'select' in open_db.

"""

import sys
sys.path.append('..')


if __name__== '__main__':

    from OpenElectrophy import open_db, OEBase
    from OpenElectrophy.io import TryItIO # come from neo

    # connection to a DB
    url = 'sqlite:///test.sqlite'
    dbinfo = open_db( url = url, myglobals= globals(), use_global_session = True)
    
    
    # thsi create a block with neo
    neo_bl = TryItIO().read_block(nb_segment = 2, duration = 2)
    bl = OEBase.from_neo(neo_bl, cascade = True, mapped_classes = dbinfo.mapped_classes)    
    bl.save()
    
    # Explore the tree with relationship (like in neo)
    print bl
    for seg in bl.segments:
        print seg
        for ana in seg.analogsignals:
            print ana
        for sptr in seg.spiketrains:
            print sptr
    for rcg in bl.recordingchannelgroups:
        print rcg
        for rc in rcg.recordingchannels:
            print rc
        for ut in rcg.units:
            print ut


