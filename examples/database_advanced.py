# -*- coding: utf-8 -*-
"""
Advanced
-----------------


OpenElectrophy.core is an tiny layer on top of sqlalchemy. (http://www.sqlalchemy.org/)

User with experience with sqlalchemy must known this:
    * when open_db if the database is empty the schema is constructed the first time
    * if the schema exist, the metadata is reflected from the db.
    * the mapped **objects** are also reflected from the db  : attributes and relationship
      are guessed from teh schema

Rules of reflexion:
   * primary key is **id**
   * only simple types
   * one many to one relationship : **parentname_id**
   * many to many relationship : a table **table1XREFtable2** exists
   
Consequences:
    * It mean that you can add any table or column you want for each database you have.
    * When you add a columns in your db, you can open it again and new attributes will be reflected
    * You can play with 2 databases at the same time with 2 sets of mapped object.
    

When you play with multi processing or GUI:
    * **use_global_session = False** and **myglobals=None**

You can modify relationship *lazy* parameters from sqlalchemy with **relationship_lazy**.
See http://docs.sqlalchemy.org/en/rel_0_8/orm/relationships.html#sqlalchemy.orm.relationship


"""

import sys
sys.path.append('..')


if __name__== '__main__':

    from OpenElectrophy import open_db, OEBase
    from OpenElectrophy.io import TryItIO # come from neo
    import numpy as np
    import quantities as pq
    

    # connection to a DB 1
    dbinfo1 = open_db( url = 'sqlite:///test1.sqlite', myglobals=None, use_global_session = False)
    session1 = dbinfo1.Session() # create a sqlalchemy session
    classes1 = { }
    for c in dbinfo1.mapped_classes:
        classes1[c.__name__] = c
    # You can do this
    Block = classes1['Block']
    bl = Block(name = 'yep')
    # or this
    bl = classes1['Block'](name = 'yep')
    
    # This allow you to play with 2 databases
    # connection to a DB 2
    dbinfo2 = open_db( url = 'sqlite:///test2.sqlite', myglobals=None, use_global_session = False)
    classes2 = { }
    for c in dbinfo2.mapped_classes:
        print c
        classes2[c.__name__] = c
    
    # This are not the same (because could different schema)
    print classes1['Block'] is classes2['Block']
    

    # You can use sqlalchemy way 
    dbinfo1 = open_db( url = 'sqlite:///test1.sqlite', myglobals=None, use_global_session = False,)
    classes1 = dict( [(c.__name__,c) for c in  dbinfo1.mapped_classes])
    Segment = classes1['Segment']
    AnalogSignal = classes1['AnalogSignal']
    session1 = dbinfo1.Session()
    seg = Segment(name = 'yep', index = 3)
    for i in range(4):
        ana = AnalogSignal(signal = np.random.rand(10)*pq.mV, t_start = 0*pq.s, sampling_rate = 3*pq.Hz,
                                        description = None, name = 'sig  {}'.format(i) )
        seg.analogsignals.append(ana)
    session1.add(seg)
    session1.commit()
    print seg
    

    # When you open you can change the lazy way of relationship
    dbinfo1 = open_db( url = 'sqlite:///test1.sqlite', myglobals=None, use_global_session = False,
                                    relationship_lazy = 'dynamic')
    classes1 = dict( [(c.__name__,c) for c in  dbinfo1.mapped_classes])
    Segment = classes1['Segment']
    session1 = dbinfo1.Session()
    seg = session1.query(Segment).first()
    # here the ralationhip is dynamic (=one query)
    for ana in seg.analogsignals.filter_by(description = None).order_by('name'):
        print ana
    

    
    
    
    
    

