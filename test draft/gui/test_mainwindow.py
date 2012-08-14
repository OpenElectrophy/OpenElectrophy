import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy.gui.mainwindow import MainWindow


def test1():
    app = QApplication([ ])
    w = MainWindow(applicationname = 'test_OE3')
    w.show()
    app.exec_()

if __name__ == '__main__' :
    test1()
