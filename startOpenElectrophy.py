#!python
# -*- coding: utf-8 -*-

import guidata #this force sip api 2

import sys
import os.path


from  OpenElectrophy.gui.qt import QApplication
from OpenElectrophy.gui.mainwindow import MainWindow

applicationname = 'OpenElectrophy_0_3'
app = QApplication(sys.argv)
w = MainWindow(applicationname =applicationname)
w.show()
sys.exit(app.exec_())

