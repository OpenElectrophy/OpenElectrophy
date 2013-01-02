# -*- coding: utf-8 -*-
"""
Literal SQL in python Loop
-----------------------------------------------

It is interesting to mix SQL queries + load + python loop.

This is an example to compute the rms of an AnalogSignal.


"""

import sys
sys.path.append('..')


if __name__== '__main__':

    from OpenElectrophy import open_db, sql, neo_to_oe, TryItIO
    import datetime
    import numpy


    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)


    # create 5 Blocks with different dates
    for i in range(5):
        neo_bl = TryItIO().read(nb_segment = 2, duration = 2)
        bl = neo_to_oe(neo_bl, cascade = True)
        bl.rec_datetime = datetime.datetime(2012, 06, 1+i, 12,30,40)
        bl.name = 'test sql %d' %i
        bl.save()
        print bl


    # select all Block.id after 3 june 2012 and Segment name is 1
    query = """
                SELECT Block.id, Segment.id, AnalogSignal.id
                FROM Block, Segment, AnalogSignal
                WHERE
                Block.id = Segment.block_id
                AND Segment.id = AnalogSignal.segment_id
                AND Block.rec_datetime > '2012-06-03'
                
                LIMIT 10
                """
    block_ids, segment_ids, analogsignal_ids= sql(query)
    print block_ids

    for i in range(block_ids.size):
        print i
        print ' block_id', block_ids[i]
        print ' segment_id', segment_ids[i]
        print ' analogsignal_id', analogsignal_ids[i]
        
        # load the Block
        bl = Block.load(block_ids[i])
        print ' ',bl.name
        
        # load the Segment
        seg = Segment.load( segment_ids[i] )
        print ' ',seg.name
        
        
        # load the AnalogSignal
        ana = AnalogSignal.load( analogsignal_ids[i] )
        
        print ' ', ana.signal.size
        rms = numpy.sqrt( numpy.mean( (ana.signal**2.) ) )
        print '     rms', rms

