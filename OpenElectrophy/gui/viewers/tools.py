# -*- coding: utf-8 -*-
"""
Common tools for viewers.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ..guiutil import *

import quantities as pq
import numpy as np


from guiqwt.curve import CurvePlot, CurveItem#
from guiqwt.image import ImagePlot
from guiqwt.styles import CurveParam
from guiqwt.builder import make
from guiqwt.shapes import RectangleShape
from guiqwt.styles import ShapeParam, LineStyleParam

import time


class TimeSeeker(QWidget) :
    """
    This is a remote for all Vierwers.
    """
    time_changed = pyqtSignal(float)
    fast_time_changed = pyqtSignal(float)
    
    def __init__(self, parent = None,) :
        QWidget.__init__(self, parent)
        
        #~ self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        but = QPushButton('play')
        but.clicked.connect(self.play)
        h.addWidget(but)
        
        but = QPushButton('stop/pause')
        but.clicked.connect(self.stop_pause)
        h.addWidget(but)
        
        h.addWidget(QLabel('Speed X:'))
        self.speedSpin = QDoubleSpinBox()
        h.addWidget(self.speedSpin)
        self.speedSpin.setMinimum(0.01)
        self.speedSpin.setMaximum(100.)
        self.speedSpin.setSingleStep(0.1)
        self.speedSpin.setValue(1.)
        self.speedSpin.valueChanged.connect(self.changeSpeed)
        
        but = QPushButton('<')
        but.clicked.connect(self.prev_step)
        h.addWidget(but)
        
        but = QPushButton('>')
        but.clicked.connect(self.next_step)
        h.addWidget(but)
        
        self.slider = QSlider()
        h.addWidget(self.slider, 10)
        self.slider.setOrientation( Qt.Horizontal )
        self.slider.setMaximum(1000)
        self.slider.setMinimum(0)
        self.slider.setMinimumWidth(400)
        self.slider.valueChanged.connect(self.sliderChanged)
        
        
        self.labelTime = QLabel('0')
        h.addWidget(self.labelTime)
        
        # all in s
        self.step_size = 0.05 #s
        self.speed = 1.
        self.t = 0 #  s
        self.t_start =  0.#  s
        self.t_stop =  10.#  s
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_step)
        
        self.timerDelay = None
        
        self.seek(self.t_start)
        

    def play(self):
        # timer is in ms
        self.timer.start( int(self.step_size*1000.) )

    def stop_pause(self):
        self.timer.stop()
        self.time_changed.emit(self.t)

    def prev_step(self):
        t = self.t -  self.step_size*self.speed
        self.seek(t)
    
    def next_step(self):
        t = self.t +  self.step_size*self.speed
        self.seek(t)
    
    def sliderChanged(self, pos):
        t = pos/1000.*(self.t_stop - self.t_start)+self.t_start
        self.seek(t, refresh_slider = False)
    
    def seek(self , t, refresh_slider = True):
        self.t = t
        if (self.t<self.t_start):
            self.t = self.t_start
        if (self.t>self.t_stop):
            self.t = self.t_stop
            if self.timer.isActive():
                self.stop_pause()

        if refresh_slider:
            self.slider.valueChanged.disconnect(self.sliderChanged)
            pos = int((self.t - self.t_start)/(self.t_stop - self.t_start)*1000.)
            self.slider.setValue(pos)
            self.slider.valueChanged.connect(self.sliderChanged)
        
        self.labelTime.setText('%10.3f s' % (self.t))
        
        self.fast_time_changed.emit(self.t)
        if not self.timer.isActive():
            #~ self.time_changed.emit(self.t)
            self.delay_emit()
        
    def changeSpeed(self , speed):
        self.speed = speed
    
    def changeStartStop(self, t_start, t_stop):
        assert t_stop>t_start
        self.t_start = t_start
        self.t_stop = t_stop
        self.seek(self.t_start)
    
    def delay_emit(self):
        if self.timerDelay is not None: return
        self.timerDelay = QTimer(interval = 600, singleShot = True)
        self.timerDelay.timeout.connect(self.timerDelayTimeout)
        self.timerDelay.start()
        
    def timerDelayTimeout(self):
        self.time_changed.emit(self.t)
        self.timerDelay = None
        
        
        





class ViewerBase(QWidget):
    """
    Base for SignalViewer, TimeFreqViewer, EpochViewer
    
    All are seekable remote by a TimeSeeker (or a timer or something else)
    All have a xisze: the size of window for x axis.
    
    
    """
    def __init__(self, parent = None,
                            xsize = 10.,
                            xzoom_limits = [0.001, 1000],
                            ylims = [0.,1.],
                            ):
        super(ViewerBase, self).__init__(parent)
        
        self.xsize = xsize
        self.xzoom_limits = xzoom_limits
        self.ylims = ylims
        
        
    
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        
        
        self.plot_layout = QVBoxLayout()
        self.mainlayout.addLayout(self.plot_layout, 8)
        #~ self.widget_plot = QWidget()
        #~ self.mainlayout.addWidget(self.widget_plot, 8)
        
        
        
        self.createToolBar()
        self.mainlayout.addWidget(self.toolBar, 2)
        
        self.t = 0.
    
    def createToolBar(self):
        self.toolBar = QToolBar(orientation = Qt.Vertical)
        
        # configure
        self.actionOpenConfigure = QAction(u'Full configure', self,
                                                                shortcut = "Ctrl+O",
                                                                icon =QIcon(':/configure.png'))
        self.toolBar.addAction(self.actionOpenConfigure)
        self.actionOpenConfigure.triggered.connect(self.open_configure_dialog)
        self.toolBar.addSeparator()
        
        # y limits
        self.toolBar.addWidget(QLabel('Y limits:'))
        self.ylim_spinboxes = [ ]
        for i in range(2):
            spin = QDoubleSpinBox( decimals = 3, singleStep = 0.1, value =self. ylims[i], 
                            minimum = -np.inf, maximum = np.inf)
            self.ylim_spinboxes.append(spin)
            spin.valueChanged.connect(self.ylim_spinboxes_changed)
        for spin in self.ylim_spinboxes[::-1]:
            self.toolBar.addWidget(spin)
        self.toolBar.addSeparator()
        
        # x size
        self.toolBar.addWidget(QLabel(u'X size (s)'))
        self.xsize_spinbox = QDoubleSpinBox(decimals = 4, singleStep = .1,
                                                        minimum = self.xzoom_limits[0], maximum = self.xzoom_limits[1])
        self.toolBar.addWidget(self.xsize_spinbox)
        self.xsize_slider = QSlider(Qt.Horizontal, minimum =0, maximum = 100)
        self.toolBar.addWidget(self.xsize_slider)
        self.xsize_spinbox.valueChanged.connect(self.xsize_spinbox_changed)
        
        #~ self.xsize_spinbox.valueChanged.connect(self.refresh)
        
        self.xsize_slider.valueChanged.connect(self.xsize_slider_changed)
        self.toolBar.addSeparator()
    
        self.is_refreshing = False

    def fast_seek(self, t):
        self.t = t
        self.refresh(fast = True)

    def seek(self, t):
        self.t = t
        self.refresh()
        
    
    def refresh(self, fast = False):
        # Implement in subclass
        if fast:
            print 'fast refresh'
        else:
            #~ import time
            time.sleep(.5)
            print 'slow refresh'
            #~ pass
        
    

        
    def open_configure_dialog(self):
        # Implement in subclass
        pass
    
    def set_xsize(self, xsize):
        self.xsize =xsize
        # FIXME
        #~ self.refresh()
        self.refresh(fast = True)
        
    
    
    #~ def show_param_panel(self):
        #~ pass
    
    #~ def hide_param_panel(self):
        #~ pass

    def ylim_spinboxes_changed(self):
        for i, spin in enumerate(self.ylim_spinboxes):
            self.ylims[i] = spin.value()
        # FIXME
        #~ self.refresh()
        self.refresh(fast = True)
    
    def xsize_slider_changed(self, val):
        
        min, max = self.xzoom_limits
        v = 10**((val/100.)*(np.log10(max) - np.log10(min) )+np.log10(min))
        self.xsize_spinbox.valueChanged.disconnect(self.xsize_spinbox_changed)
        self.xsize_spinbox.setValue(v)
        self.xsize = v
        self.xsize_spinbox.valueChanged.connect(self.xsize_spinbox_changed)
    
    def xsize_spinbox_changed(self, val):
        self.xsize = val
        min, max = self.xzoom_limits
        v = int( (np.log10(val)-np.log10(min))/(np.log10(max) - np.log10(min) )*100 )
        self.xsize_slider.valueChanged.disconnect(self.xsize_slider_changed)
        self.xsize_slider.setValue(v)
        self.xsize_slider.valueChanged.connect(self.xsize_slider_changed)



def get_analogsignal_chunk(ana, t_start, t_stop, return_t_vect = True):
    #~ print t_start, t_stop
    #~ print ana.t_start, ana.t_stop
    #~ print 
    if t_start>=ana.t_stop or t_stop<ana.t_start:
        #~ print 'yep'
        if return_t_vect:
            return array([ ], dtype = ana.dtype), array([ ], dtype = 'f')
        else:
            return array([ ], dtype = ana.dtype)
    else:
        ind_start = int(((t_start-ana.t_start)*ana.sampling_rate).simplified)
        ind_stop = int(((t_stop-ana.t_start)*ana.sampling_rate).simplified)
        
        if return_t_vect:
            t_vect = (np.arange(ind_stop-ind_start)/ana.sampling_rate+t_start).rescale('s').magnitude
            if ind_start<0:
                t_vect = t_vect[-ind_start:]
                ind_start=0
            if ind_stop>ana.size:
                t_vect = t_vect[:-(ind_stop-ana.size)]
                ind_stop=ana.size
            return t_vect, ana.magnitude[ind_start:ind_stop]
        else:
            if ind_start<0:
                ind_start=0
            if ind_stop>ana.signal.size:
                ind_stop=ana.signal.size
            return ana.magnitude[ind_start:ind_stop]






