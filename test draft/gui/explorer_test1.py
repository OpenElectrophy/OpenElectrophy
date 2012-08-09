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



url = 'sqlite:///test_db_1.sqlite'

def test1():
    """
    simple test
    """
    mapperInfo = open_db(url, mylocals = locals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                relationship_lazy = 'dynamic', 
                                                                )
    
    session = mapperInfo.Session()

    app = QApplication([ ])
    settings = PickleSettings(applicationname = 'testOE3')
    #~ settings = None
    
    w = MainExplorer(mapperInfo = mapperInfo, settings = settings)
    ok = w.show()
    app.exec_()




if __name__ == '__main__' :
    test1()

