# -*- coding: utf-8 -*-
"""
This basic utilities ofr embeded matplotlib in QT4.
See
http://matplotlib.sourceforge.net/examples/user_interfaces/embedding_in_qt4.html

"""

from ..qt import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2


class SimpleCanvas(FigureCanvas):
    def __init__(self, parent=None, ):
        self.fig = Figure()
        super(SimpleCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.updateGeometry()
        
        #~ FigureCanvas.setSizePolicy(self,
                                   #~ QtGui.QSizePolicy.Expanding,
                                   #~ QtGui.QSizePolicy.Expanding)
        #~ FigureCanvas.updateGeometry(self)

        color = self.palette().color(QPalette.Background).getRgb()
        color = [ c/255. for c in color[:3] ]
        self.fig.set_facecolor(color)


class SimpleCanvasAndTool(QWidget):
    def __init__(self  , parent = None ):
        super(SimpleCanvasAndTool, self).__init__(parent = parent)
        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.toolbar = NavigationToolbar2(parent = self, canvas = self.canvas)
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.canvas)
    
    def draw(self):
        self.canvas.draw()



def test1():
    app = QApplication([ ])
    w1 = SimpleCanvas()
    w1.fig.add_subplot(111)
    w1.show()
    w2 = SimpleCanvasAndTool()
    w2.show()
    
    app.exec_()
    
    
if __name__ == '__main__':
    test1()
    