#!python
# -*- coding: utf-8 -*-

import sys
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
app = QApplication(sys.argv)

applicationname = 'OpenElectrophy_0_3'

from OpenElectrophy.gui.mainwindow import MainWindow


class FakeOpenDB(object):
    """Class that mimics OpenDB for opening from command line.
    
    Currently this will only work for sqlite databases.
    """
    def __init__(self, filename):
        self.url = 'sqlite:///' + filename
        self.filename = filename    
    def get_url(self):
        return self.url    
    def get_dict_url(self):
        return dict([('name', os.path.basename(self.filename)), 
            ('type', 'sqlite')])    
    def exec_(self):
        return True

if len(sys.argv) > 1:
    # Grab second argument and use that as filename to open sqlite file
    print sys.argv
    d = FakeOpenDB(filename=sys.argv[-1])
    w = MainWindow(applicationname =applicationname)
    w.openDatabaseFromOpenDB(d)
else:
    w = MainWindow(applicationname =applicationname)

w.show()
sys.exit(app.exec_())

