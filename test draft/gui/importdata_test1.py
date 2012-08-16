import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.core.sqlmapper import *
from OpenElectrophy.gui.importdata import ImportData


def test1():
    url = 'sqlite:///test_db_import.sqlite'
    dbinfo = open_db(url, myglobals = None, use_global_session = False,  numpy_storage_engine = 'sqltable', compress = None,)
    
    app = QApplication([ ])
    w = ImportData(dbinfo = dbinfo, use_thread = True)
    w.show()
    app.exec_()

def test2():
    url = 'sqlite:///'
    dbinfo = open_db(url, myglobals = None, use_global_session = False,  numpy_storage_engine = 'sqltable', compress = None,)
    
    app = QApplication([ ])
    w = ImportData(dbinfo = dbinfo, use_thread = False)
    w.show()
    app.exec_()


if __name__ == '__main__' :
    #~ test1()
    test2()

