import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui import *
from OpenElectrophy.gui.explorer import *
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings



import quantities as pq
import numpy as np

import neo
from OpenElectrophy.core.base import OEBase


from sqlalchemy.sql.expression import asc, desc



#~ url = 'sqlite:///test_db_1.sqlite'
url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_2'

def test1():
    """
    simple test
    """
    dbinfo = open_db(url, myglobals = globals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'dynamic', 
                                                                )
    
    session = dbinfo.Session()

    app = QApplication([ ])
    settings = PickleSettings(applicationname = 'testOE3')
    #~ settings = None
    
    w = MainExplorer(dbinfo = dbinfo, settings = settings, name = url)
    ok = w.show()
    app.exec_()




if __name__ == '__main__' :
    test1()

