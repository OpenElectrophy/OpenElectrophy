# -*- coding: utf-8 -*-
"""

Basic save and load of a variable to a database
----------------------------------------------------------------------------

The only thing to remind in OpenElectrophy is that everything is stored in a database.
So each analog signal, spike, spike train or oscillation can be accessed with a standard SQL query.
In some cases SQL is very easy and efficient: for finding a data, for ordering, for filtering...
But for other operations, writing SQL queries is repetitive and time consuming. 
Thus OpenElectrophy provides a mapper class to access mySQL values directly in Python without writing any SQL query. 
This mapper is directly constructed on top on SQLalchemy.

In practice, to each SQL table corresponds a Python class.
So OpenElectrophy provides all these classes: Block, Segment, AnalogSignal, Epoch, Event, SpikeTrain, Neuron, ...
Each instance of one of these classes will map a row of a table and all fields of the SQL table will be held by an instance member.


All these classes have 2 basic methods: save() and load() to save or load all fields to/from the database.

By consequence, to manipulate fields of a SQL row, you just need to read/write a Python variable (class member). 


"""

import sys
sys.path.append('..')

if __name__== '__main__':
    
    from OpenElectrophy import open_db

    # connection to a DB
    url = 'sqlite:///test.sqlite'
    open_db( url = url, myglobals= globals(), use_global_session = True)

    # create an empty segment variable
    seg1 = Segment()

    # fill attributes (=columns in SQL)
    seg1.name = 'My first segment'
    seg1.description = 'This is just a test'
    seg1.index = 3

    # TEXT field in SQL = str in python
    print seg1.name
    print type(seg1.name)

    print seg1.id
    # give None

    # SAVE seg1 to the db (return the id)
    seg1.save()
    # now the id of seg1 is not anymore None
    my_id =  seg1.id
    
    # LOAD from the db
    # create an empty segment
    open_db( url = url, myglobals= globals(), use_global_session = True)
    seg2 = Segment.load( id  = my_id)
    # equvalent to
    seg2 = Segment(id = my_id)
    print seg2.id
    print seg2.name
