import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy import *
from OpenElectrophy.gui.schemadesign import SchemaDesign


url = 'sqlite:///test_db_1.sqlite'

kargs_reopen = dict(url = url,
                                    myglobals = globals(),
                                    use_global_session = False, 
                                    object_number_in_cache = 3000,
                                    relationship_lazy = 'dynamic', 
                                    )
dbinfo = open_db(**kargs_reopen)
dbinfo.kargs_reopen = kargs_reopen

def test1():
    app = QApplication([ ])
    w = SchemaDesign(dbinfo = dbinfo)
    w.show()
    app.exec_()

if __name__ == '__main__' :
    test1()
