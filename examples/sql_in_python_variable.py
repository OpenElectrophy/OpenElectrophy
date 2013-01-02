# -*- coding: utf-8 -*-
"""
SQL in python : dynamical query
-----------------------------------------------

Previous examples show how to execute a query in python.

These queries were static, meaning that there were fully determined while scripting.

Now, an example of how to write a query with a variable part (determined during script execution).
It is very convinient to dynamicaly explore the data.

To to do this you need to use the same function sql but you can add some external variables.
And you can use ':' inside the query for declaration of external (python) variables.


"""

import sys
sys.path.append('..')

if __name__== '__main__':
    #start

    from OpenElectrophy import open_db, sql, neo_to_oe, TryItIO
    import datetime
    import numpy


    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)


    descriptions = [ 'condition A', 'condition B', 'condition C']
    # create 5 block with 50 segment 
    # segment.description is the condition (randomly A B C)
    for i in range(5):
        bl = Block( name = 'test')
        bl.save()
        for j in range(50):
            c = int(numpy.random.rand()*3)
            seg = Segment( 
                                        name = 'seg test',
                                        description = descriptions[c],
                                    )
            seg.block_id = bl.id
            seg.save()
    
    # static query for block
    query1 = """
                    SELECT block.id
                    FROM block
                    LIMIT 50
                    """
    #globals.globalsession.execute(query1)
    block_ids, = sql(query1)

    for block_id in block_ids:
        print 'block', block_id
        
        # variable query
        for description in descriptions:
            query2 = """
                            SELECT segment.id
                            FROM segment
                            WHERE
                            segment.block_id = :block_id
                            AND segment.description = :description
                            """
            # variables are given in sql with dict
            id_segments, = sql( query2, 
                                                    block_id = block_id,
                                                    description = description,
                                                    )
            print ' has ', len(id_segments), description



