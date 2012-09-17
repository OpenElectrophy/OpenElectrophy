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
    
    def __init__(self, parent = None, show_play = True, show_step = True,
                                    show_slider = True, show_spinbox = True, show_label = False) :
        QWidget.__init__(self, parent)
        
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.toolbar = QToolBar()
        self.mainlayout.addWidget(self.toolbar)
        t = self.toolbar
        
        self.show_play = show_play
        self.show_step = show_step
        self.show_slider = show_slider
        self.show_spinbox = show_spinbox
        self.show_label = show_label
        
        if show_play:
            but = QPushButton(QIcon(':/media-playback-start.png'), '')
            but.clicked.connect(self.play)
            t.addWidget(but)
            
            but = QPushButton(QIcon(':/media-playback-stop.png'), '')
            but.clicked.connect(self.stop_pause)
            t.addWidget(but)
            
            t.addWidget(QLabel('Speed:'))
            self.speedSpin = QDoubleSpinBox()
            t.addWidget(self.speedSpin)
            self.speedSpin.setMinimum(0.01)
            self.speedSpin.setMaximum(100.)
            self.speedSpin.setSingleStep(0.1)
            self.speedSpin.setValue(1.)
            self.speedSpin.valueChanged.connect(self.change_speed)
            t.addSeparator()
        
        if show_step:
            but = QPushButton('<')
            but.clicked.connect(self.prev_step)
            t.addWidget(but)
            
            self.popupStep = QToolButton( popupMode = QToolButton.MenuButtonPopup,
                                                                        toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                                                        text = u'Step 50ms'
                                                                        )
            t.addWidget(self.popupStep)
            ag = QActionGroup(self.popupStep )
            ag.setExclusive( True)
            for s in ['60s','10s', '1s', '100ms', '50ms', '5ms' ]:
                act = QAction(s, self.popupStep, checkable = True)
                ag.addAction(act)
                self.popupStep.addAction(act)
            ag.triggered.connect(self.change_step)
            
            but = QPushButton('>')
            but.clicked.connect(self.next_step)
            t.addWidget(but)
            
            t.addSeparator()
        
        if show_slider:
            self.slider = QSlider()
            t.addWidget(self.slider)
            self.slider.setOrientation( Qt.Horizontal )
            self.slider.setMaximum(1000)
            self.slider.setMinimum(0)
            self.slider.setMinimumWidth(400)
            self.slider.valueChanged.connect(self.sliderChanged)
        
        if show_spinbox:
            self.spinbox = QDoubleSpinBox(decimals = 3., minimum = -np.inf, maximum = np.inf, 
                                                                singleStep = 0.05, minimumWidth = 60)
            t.addWidget(self.spinbox)
            t.addSeparator()
            self.spinbox.valueChanged.connect(self.spinBoxChanged)
        
        if show_label:
            self.labelTime = QLabel('0')
            t.addWidget(self.labelTime)
            t.addSeparator()
        
        # all in s
        self.refresh_interval = .1 #s
        self.step_size = 0.05 #s
        self.speed = 1.
        self.t = 0 #  s
        self.set_start_stop(0., 10.)
        
        self.timerPlay = QTimer(self)
        self.timerPlay.timeout.connect(self.timerPlayTimeout)
        self.timerDelay = None
        
        self.seek(self.t_start)
        

    def play(self):
        # timer is in ms
        self.timerPlay.start( int(self.refresh_interval*1000.) )

    def stop_pause(self):
        self.timerPlay.stop()
        self.seek(self.t)
    
    def timerPlayTimeout(self):
        t = self.t +  self.refresh_interval*self.speed
        self.seek(t)
    
    def set_start_stop(self, t_start, t_stop):
        self.t_start = t_start
        self.t_stop =  t_stop
        if self.show_spinbox:
            self.spinbox.setMinimum(t_start)
            self.spinbox.setMaximum(t_stop)
        
    def change_step(self, act):
        t = str(act.text())
        self.popupStep.setText(u'Step '+t)
        if t.endswith('ms'):
            self.step_size = float(t[:-2])*1e-3
        else:
            self.step_size = float(t[:-1])
        if self.show_spinbox:
            self.spinbox.setSingleStep(self.step_size)

    def prev_step(self):
        t = self.t -  self.step_size
        self.seek(t)
    
    def next_step(self):
        t = self.t +  self.step_size
        self.seek(t)
    
    def sliderChanged(self, pos):
        t = pos/1000.*(self.t_stop - self.t_start)+self.t_start
        self.seek(t, refresh_slider = False)
    
    def spinBoxChanged(self, val):
        self.seek(val, refresh_spinbox = False)
    
    def seek(self , t, refresh_slider = True, refresh_spinbox = True):
        if self.timerDelay is not None and self.timerDelay.isActive():
            self.timerDelay.stop()
            self.timerDelay = None
        
        self.t = t
        if (self.t<self.t_start):
            self.t = self.t_start
        if (self.t>self.t_stop):
            self.t = self.t_stop
            if self.timerPlay.isActive():
                self.stop_pause()

        if refresh_slider and self.show_slider:
            self.slider.valueChanged.disconnect(self.sliderChanged)
            pos = int((self.t - self.t_start)/(self.t_stop - self.t_start)*1000.)
            self.slider.setValue(pos)
            self.slider.valueChanged.connect(self.sliderChanged)
        
        if refresh_spinbox and self.show_spinbox:
            self.spinbox.valueChanged.disconnect(self.spinBoxChanged)
            self.spinbox.setValue(t)
            self.spinbox.valueChanged.connect(self.spinBoxChanged)
        
        if self.show_label:
            self.labelTime.setText('{:5.3} s'.format(self.t))
        
        self.fast_time_changed.emit(self.t)
        if not self.timerPlay.isActive():
            self.delay_emit()
        
    def change_speed(self , speed):
        self.speed = speed
    
    def change_start_stop(self, t_start, t_stop):
        assert t_stop>t_start
        self.t_start = t_start
        self.t_stop = t_stop
        self.seek(self.t_start)
    
    def delay_emit(self):
        if self.timerDelay is not None: return
        self.timerDelay = QTimer(interval = 700, singleShot = True)
        self.timerDelay.timeout.connect(self.timerDelayTimeout)
        self.timerDelay.start()
        
    def timerDelayTimeout(self):
        self.time_changed.emit(self.t)
        self.timerDelay = None


class XSizeChanger(QWidget):
    xsize_changed = pyqtSignal(float)
    def __init__(self, parent = None,
                            xsize = 10.,
                            xzoom_limits = [0.001, 1000],
                            orientation  = Qt.Vertical,
                            ):
        super(XSizeChanger, self).__init__(parent)

        self.xsize = xsize
        self.xzoom_limits = xzoom_limits
        
        
        if orientation == Qt.Horizontal:
            self.mainlayout = QHBoxLayout()
        else:
            self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.targets = None

        self.xsize_spinbox = QDoubleSpinBox(decimals = 4, singleStep = .1,
                                                        minimum = self.xzoom_limits[0], maximum = self.xzoom_limits[1])
        self.mainlayout.addWidget(self.xsize_spinbox)
        self.xsize_slider = QSlider(Qt.Horizontal, minimum =0, maximum = 100)
        self.mainlayout.addWidget(self.xsize_slider)
        
        self.xsize_spinbox.valueChanged.connect(self.xsize_spinbox_changed)
        self.xsize_slider.valueChanged.connect(self.xsize_slider_changed)
        self.xsize_spinbox.setValue(self.xsize)
    
        
    
    def set_targets(self, targets):
        self.targets = targets
        for target in self.targets:
            target.xsize = self.xsize
    
    def _set_xsize(self, xsize):
        self.xsize =xsize
        self.xsize_changed.emit(self.xsize)
        if self.targets is not None:
            for target in self.targets:
                target.xsize = self.xsize

    def xsize_slider_changed(self, val):
        min, max = self.xzoom_limits
        v = 10**((val/100.)*(np.log10(max) - np.log10(min) )+np.log10(min))
        self.xsize_spinbox.valueChanged.disconnect(self.xsize_spinbox_changed)
        self.xsize_spinbox.setValue(v)
        self._set_xsize(v)
        self.xsize_spinbox.valueChanged.connect(self.xsize_spinbox_changed)
    
    def xsize_spinbox_changed(self, val):
        self._set_xsize(val)
        min, max = self.xzoom_limits
        v = int( (np.log10(val)-np.log10(min))/(np.log10(max) - np.log10(min) )*100 )
        self.xsize_slider.valueChanged.disconnect(self.xsize_slider_changed)
        self.xsize_slider.setValue(v)
        self.xsize_slider.valueChanged.connect(self.xsize_slider_changed)



class YLimsChanger(QWidget):
    ylims_changed = pyqtSignal(list)
    def __init__(self, parent = None,
                            ylims = [0,1.],
                            orientation  = Qt.Vertical
                            ):
        super(YLimsChanger, self).__init__(parent)

        self.ylims = ylims
        
        self.targets = None
        
        if orientation == Qt.Horizontal:
            self.mainlayout = QHBoxLayout()
        else:
            self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.ylim_spinboxes = [ ]
        for i in range(2):
            spin = QDoubleSpinBox( decimals = 3, singleStep = 0.1, value =self. ylims[i], 
                            minimum = -np.inf, maximum = np.inf)
            self.ylim_spinboxes.append(spin)
            spin.valueChanged.connect(self.ylim_spinboxes_changed)
        for spin in self.ylim_spinboxes[::-1]:
            self.mainlayout.addWidget(spin)
    
    def set_targets(self, targets):
        self.targets = targets
        for target in self.targets:
            target.ylims = self.ylims
        
    
    def set_ylims(self, ylims):
        self._set_ylims(ylims)
        for i, spin in enumerate(self.ylim_spinboxes):
            spin.valueChanged.disconnect(self.ylim_spinboxes_changed)
            spin.setValue(self.ylims[i])
            spin.valueChanged.connect(self.ylim_spinboxes_changed)

    def _set_ylims(self, ylims):
        self.ylims =ylims
        self.ylims_changed.emit(self.ylims)
        if self.targets is not None:
            for target in self.targets:
                target.ylims = self.ylims

    def ylim_spinboxes_changed(self):
        #~ for i, spin in enumerate(self.ylim_spinboxes):
            #~ self.ylims[i] = spin.value()
        self._set_ylims([ spin.value() for spin in self.ylim_spinboxes ])



class ViewerBase(QWidget):
    """
    Base for SignalViewer, TimeFreqViewer, EpochViewer
    
    This handle seek and fast_seek with TimeSeeker time_changed and fast_time_changed signals
    """
    need_refresh = pyqtSignal(bool)
    def __init__(self, parent = None):
        super(ViewerBase, self).__init__(parent)

        #~ self.mainlayout = QHBoxLayout()
        #~ self.setLayout(self.mainlayout)
        
        self.t = 0.
        self.is_refreshing = False
        self.need_refresh.connect(self.refresh, type = Qt.QueuedConnection)

    def fast_seek(self, t):
        if self.is_refreshing: 
            return
        self.t = t
        self.is_refreshing = True
        self.need_refresh.emit(True)

    def seek(self, t):
        if self.is_refreshing:
            return
        self.t = t
        self.is_refreshing = True
        self.need_refresh.emit(False)
    
    def refresh(self, fast = False):
        # Implement in subclass
        if fast:
            print 'fast refresh'
        else:
            time.sleep(.5)
            print 'slow refresh'
        self.is_refreshing = False
    


class ViewerWithXSizeAndYlim(ViewerBase):
    def __init__(self, parent = None,
                                                            xsize = 10., 
                                                            xzoom_limits = (0.001, 1000),
                                                            ylims = [0.,1.],
                                                            show_toolbar = True,
                                                            **kargs):
        
        super(ViewerWithXSizeAndYlim, self).__init__(parent, **kargs)
                                                            


        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.plot_layout = QVBoxLayout()
        self.mainlayout.addLayout(self.plot_layout, 8)
        
        self.ylims_changer = YLimsChanger()
        self.ylims_changer.set_targets([self ])
        self.xsize_changer = XSizeChanger(xsize = xsize, xzoom_limits = xzoom_limits)
        self.xsize_changer.set_targets([self ])
        
        if show_toolbar:
            self.toolBar = QToolBar(orientation = Qt.Vertical)
            tb = self.toolBar
            self.mainlayout.addWidget(self.toolBar, 2)
            
            # configure
            self.actionOpenConfigure = QAction(u'Full configure', self,
                                                                    shortcut = "Ctrl+O",
                                                                    icon =QIcon(':/configure.png'))
            tb.addAction(self.actionOpenConfigure)
            self.actionOpenConfigure.triggered.connect(self.open_configure_dialog)
            tb.addSeparator()
            # y limits
            tb.addWidget(QLabel('Y limits:'))
            
            tb.addWidget(self.ylims_changer)
            
            self.ylims_changer.ylims_changed.connect(self.refresh, type = Qt.QueuedConnection)
            
            #x size
            tb.addWidget(QLabel('X size (s):'))
            
            tb.addWidget(self.xsize_changer)
            
            self.xsize_changer.xsize_changed.connect(self.refresh, type = Qt.QueuedConnection)
        

    def open_configure_dialog(self):
        # Implement in subclass
        pass


def get_analogsignal_slice(ana, t_start, t_stop, return_t_vect = True, decimate = None):
    if t_start>=ana.t_stop or t_stop<ana.t_start:
        if return_t_vect:
            return np.array([ ], dtype = 'f'), slice(0,0)
        else:
            return slice(0,0)
    else:
        ind_start = int(((t_start-ana.t_start)*ana.sampling_rate).simplified)
        ind_stop = int(((t_stop-ana.t_start)*ana.sampling_rate).simplified)
        step = 1
        if decimate is not None:
            length = (ind_stop-ind_start)
            step = int(length/decimate)
            if step==0: step=1
            #~ # align on step ???
            #~ ind_start -= ind_start%step
            #~ ind_stop -= ind_stop%step + step
        else:
            step = 1
        if ind_start<0:
            ind_start=0
            t_start = ana.t_start
        if ind_stop>ana.size:
            ind_stop=ana.size
        
        if return_t_vect:
            t_vect = (np.arange(0,ind_stop-ind_start, step, dtype='f')/ana.sampling_rate+t_start).rescale('s').magnitude
            return t_vect, slice(ind_start, ind_stop, step)
        else:
            return slice(ind_start, ind_stop, step)






