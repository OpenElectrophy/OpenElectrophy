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
    mapperInfo = open_db(url, mylocals = locals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'dynamic', 
                                                                )
    session = mapperInfo.Session()
    
    app = QApplication([ ])
    td = TreeDescription( mapped_classes = mapperInfo.mapped_classes,)

    w = ViewDesigner(mapperInfo= mapperInfo, treedescription = td)
    ok = w.show()
    app.exec_()
    


def test2():
    # modify
    mapperInfo = open_db(url, mylocals = locals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'dynamic', 
                                                                )
    
    session = mapperInfo.Session()
    
    td = None

    app = QApplication([ ])
    w = ViewDesigner(mapperInfo= mapperInfo, treedescription = td)
    ok = w.show()
    app.exec_()



if __name__ == '__main__' :
    test1()
    #~ test2()


