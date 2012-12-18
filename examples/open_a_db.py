# -*- coding: utf-8 -*-
"""
Open a db 
------------------

OpenElectrophy provides a simple function open_db.

You have to give an url to open a db.

url is in format of sqlalchemy

OpenElectrophy support 4 database engines:
    - sqlite: a db in one file for everything (include arrays)
    - mysql: a db on a server
    - postgres: a db on a server
    - sqlite+pytables: a db in two files : one for everything one for arrays.

For sqlite, the url is::
    sqllite://myfile

For mysql, the url is::
    mysql://login:password@host/dbname

For postgres, the url is::
    postgresql://login:password@host/dbname


open_db have some parameters.
When scripting the main (and dealing with one db at once) use that:
    * **myglobals= globals()**  : this inject in your namespace all classe mapped from 
       the database by reflexion (included columns added by hand)
    * **use_global_session = True** : this keep somewhere an object called *session*
       in sqlalchemy world that is the entry point with your db.

For more detail see open_db.


"""

import sys
sys.path.append('..')

if __name__== '__main__':

    from OpenElectrophy import open_db
    # connection to a DB
    #url = 'sqlite:////home/sgarcia/test.db'
    #url = 'sqlite:///C:/Users/sgarcia/Desktop/test.db'
    #url = 'sqlite:///test.db'
    #open_db( url = url)
    
    # this open mysql
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'
    open_db( url = url, myglobals= globals(), use_global_session = True)

    # this open sqlite
    open_db( url = 'sqlite:///test.db', myglobals= globals(), use_global_session = True)

    # this open sqlite + pytables (hdf5)
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'
    open_db( url = url, myglobals= globals(), use_global_session = True, hdf5_filename = 'test1.h5')



