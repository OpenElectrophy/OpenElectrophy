# -*- coding: utf-8 -*-
"""
Literal SQL in python Basic
-----------------------------------------------

OpenElectrophy provide a very simple way to execute SQL queries in python : the execute_sql (alias sql)

Contrary to python DB API and sqlalchemy OpenElectrophy:
    * return results in columns style oposed as raw style.
    * columns are numpy.array (by default)

"""

import sys
sys.path.append('..')


if __name__== '__main__':
    

    from OpenElectrophy import open_db, sql
    import datetime
    
    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)

    # create 5 Block with different dates
    for i in range(5):
        bl = Block(name = 'Block {}'.format(i),
                        rec_datetime = datetime.datetime(2012, 06, 1+i, 12,30,40)
                        )
        bl.save()
        print bl.id

    # select all Block.id after 3 june 2010
    query = """
                SELECT Block.id, Block.name
                FROM Block
                WHERE
                Block.rec_datetime > '2012-06-03'
                """
    ids, names = sql(query)
    print ids
    print names
    print type(names)



    # be CAREFUL if you select only one column
    # you need a coma even for one column

    # GOOD
    query = """
                SELECT Block.name
                FROM Block
                WHERE
                Block.rec_datetime > '2012-06-03'
                """
    names, = sql(query)
    print names #[test sql 2 test sql 3 test sql 4]
    print type(names) #<type 'numpy.ndarray'>
    print len(names) # 3
    # names is a ndarray


    # BAD
    query = """
                SELECT Block.name
                FROM Block
                WHERE
                Block.rec_datetime > '2012-06-03'
                """
    names = sql(query)
    print names #array([test sql 2, test sql 3, test sql 4], dtype=object)]
    print type(names) #<type 'list'>
    print len(names) # 1
