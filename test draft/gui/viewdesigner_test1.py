import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui import *
from OpenElectrophy.gui.viewdesigner import *
from OpenElectrophy.gui.qtsqltreeview import *



import quantities as pq
import numpy as np

import neo


from sqlalchemy.sql.expression import asc, desc


url = 'sqlite:///test_db_1.sqlite'

def test1():
    # new one
    dbinfo = open_db(url, myglobals = globals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'select', 
                                                                )
    session = dbinfo.Session()
    
    app = QApplication([ ])
    td = TreeDescription( dbinfo = dbinfo,)

    w = ViewDesigner(dbinfo= dbinfo, treedescription = td)
    ok = w.show()
    app.exec_()
    


def test2():
    # modify
    dbinfo = open_db(url,  myglobals = globals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'select', 
                                                                )
    
    session = dbinfo.Session()
    
    td = None

    app = QApplication([ ])
    w = ViewDesigner(dbinfo= dbinfo, treedescription = td)
    ok = w.show()
    app.exec_()



if __name__ == '__main__' :
    test1()
    #~ test2()


