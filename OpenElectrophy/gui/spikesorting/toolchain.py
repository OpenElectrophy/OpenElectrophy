# -*- coding: utf-8 -*-
"""
A widget for apply spike sorting chain and related parameters.
"""

from collections import OrderedDict
#~ from .parameters import *
from ...spikesorting.methods import *
from ..guiutil import *
import pyqtgraph as pg
from OpenElectrophy.gui.guiutil.mypyqtgraph import get_dict_from_group_param

from ..guiutil.mymatplotlib import *

#~ from PyQt4.QtWebKit import QWebView
from ..qt import QWebView

class SpikeSortingToolChain(object):
    """
    a SpikeSortingToolChain is define by a suite of of methods available in OpenElectrophy.spikesortign.methods
    Example 1, from full band signal to clustered spike:
      * [ButterworthFilter] > [MedianThresholdDetection or StdThresholdDetection ] >
          [AlignWaveformOnPeak or AlignWaveformOnDetection] > [PcaFeature or IcaFeature] > [SklearnKMeans or SklearnGaussianMixtureEm]
    Example 2, only detection on onready filterred signal
      * MedianThresholdDetection or StdThresholdDetection
    
    """
    name = ''
    chain = [ ]


# famillies
filters = [ ButterworthFilter, DerivativeFilter, SlidingMedianFilter]
detections = [  RelativeThresholdDetection, ManualThresholdDetection, MTEODetection]
waveforms = [ AlignWaveformOnDetection, AlignWaveformOnPeak, AlignWaveformOnCentralWaveform ]
features = [ PcaFeature, IcaFeature,CombineFeature, AllPeak, PeakToValley, HaarWaveletFeature]
sorting = [SklearnGaussianMixtureEm, SklearnKMeans, SklearnMiniBatchKMeans, SklearnMeanShift ]
clean = [OutsideTemplateCleaning, ]



class FromFullBandSignalToClustered(SpikeSortingToolChain):
    name = 'from full band signal to clustered spike'
    chain = OrderedDict([
                                            [ 'filters', filters],
                                            [ 'detections', detections],
                                            [ 'waveforms', waveforms],
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])

class FromFullBandSignalToClusteredClean(SpikeSortingToolChain):
    name = 'from full band signal to clustered spike with clean'
    chain = OrderedDict([
                                            [ 'filters', filters],
                                            [ 'detections', detections],
                                            [ 'waveforms', waveforms],
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            [ 'clean', clean],
                                            ])


class FromFilteredBandSignalToClustered(SpikeSortingToolChain):
    name = 'from filtered band signal to clustered spike'
    chain = OrderedDict([
                                            [ 'detections', detections],
                                            [ 'waveforms', waveforms],
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])
    


class FromWaveformToClustered(SpikeSortingToolChain):
    name = 'from waveform to clustered spike'
    chain = OrderedDict([
                                            [ 'features', features],
                                            [ 'sorting', sorting],
                                            ])


#~ # This is for you Chris:
class FromFeatureToClustered(SpikeSortingToolChain):
    name = 'from feature to clustered spike'
    chain = OrderedDict([
                                            [ 'sorting', sorting],
                                            ])


class FromFullBandSignalToDetection(SpikeSortingToolChain):
    name = 'from full band signal to detected spike'
    chain = OrderedDict([
                                            [ 'filters', filters],
                                            [ 'detections', detections],
                                            ])

    

all_toolchain = [FromFullBandSignalToClustered, FromFullBandSignalToClusteredClean, FromFilteredBandSignalToClustered,
                            FromWaveformToClustered, FromFeatureToClustered, FromFullBandSignalToDetection,
                            ]


class MultiMethodsParamWidget(QWidget):
    run_clicked = pyqtSignal()
    
    def __init__(self, parent = None, settings = None, title = None,
                            methods = [ ], spikesorter = None):
        super(MultiMethodsParamWidget, self).__init__(parent =parent)
        
        self.settings = settings
        self.methods = methods
        self.spikesorter = spikesorter
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        if title is not None:
            self.mainLayout.addWidget(QLabel(title))
            
        self.widget = None
        
        self.combo = QComboBox()
        self.mainLayout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.display_params)
        self.combo.addItems([ method.name for method in self.methods])
    
    def display_params(self, pos):
        if self.widget is not None :
            self.widget.setVisible(False)
            self.mainLayout.removeWidget(self.widget)
        if pos<0: return
        self.widget = QWidget()
        self.mainLayout.addWidget(self.widget)
        v = QVBoxLayout()
        self.widget.setLayout(v)
        self.method = self.methods[pos]
        
        if self.method.params is not None:
            self.params = pg.parametertree.Parameter.create( name='Params',
                                                    type='group', children =self.method.params)
            self.treeparams = pg.parametertree.ParameterTree()
            self.treeparams.header().hide()
            self.treeparams.setParameters(self.params, showTop=True)
        else:
            self.treeparams = QWidget()
            
        #~ if self.method.dataset is not None:
            #~ self.param_widget  = ParamWidget( self.method.dataset, title = self.method.name,
                                                    #~ settings = self.settings, settingskey = 'spikesortings/methods/'+self.method.name)
        #~ else:
            #~ self.param_widget = QWidget()
            
        #~ v.addWidget(self.param_widget,1)
        v.addWidget(self.treeparams,1)

        but = QPushButton('Info on {}'.format(self.method.name))
        v.addWidget(but)
        but.clicked.connect(self.open_info)

        but = QPushButton('run {}'.format(self.method.name))
        v.addWidget(but)
        but.clicked.connect(self.run_clicked.emit)
        
        if hasattr(self.method, 'mpl_plots'):
            for plot_name in self.method.mpl_plots:
                but = QPushButton('{}'.format(plot_name))
                v.addWidget(but)
                but.clicked.connect(self.open_figure)
                
            
    
    def get_method(self) :
        return self.method
    
    #~ def get_name(self):
        #~ return self.method.name
    
    def get_dict(self) :
        if self.method.params is not None:
            return get_dict_from_group_param(self.params)
        else:
            return {}
        #~ if self.method.dataset is not None:
            #~ return self.param_widget.to_dict()
        #~ else:
            #~ return {}
    
    def open_info(self):
        if not hasattr(self, 'helpview'):
            self.helpview = QWebView()
            self.helpview.setWindowFlags(Qt.SubWindow)
        self.helpview.setHtml(rest_to_html(self.method.__doc__))
        self.helpview.setVisible(True)
        
    def open_figure(self):
        print 'open_figure'
        sps = self.spikesorter
        
        step = None
        for step in sps.history[::-1]:
            if self.method == type(step['methodInstance']):
                inst = step['methodInstance']
                break
        if step is None: return
        self.canvas = SimpleCanvasAndTool(parent = self)
        self.canvas.setWindowFlags(Qt.Window)
        getattr(inst, str(self.sender().text()))(self.canvas.fig, sps)
        self.canvas.show()


class ToolChainWidget(QWidget):
    need_refresh = pyqtSignal()
    
    def __init__(self, parent = None, spikesorter = None, settings = None):
        super(ToolChainWidget, self).__init__(parent =parent)
        self.spikesorter = spikesorter
        self.settings = settings
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        h = QHBoxLayout()
        self.mainLayout.addLayout(h)
        but = QPushButton('Run all chain')
        h.addWidget(but)
        but.clicked.connect(self.run_all_chain)
        
        self.toolbox = None
        
        but =  QToolButton( popupMode = QToolButton.InstantPopup,
                                            toolButtonStyle = Qt.ToolButtonTextBesideIcon,
                                            icon = QIcon(':/configure.png' ),
                                            #~ )
                                            text = u'Mode')
        h.addWidget(but)
        self.actions = [ ]
        for tc in all_toolchain:
            act = QAction(tc.name, but, checkable = True)
            #~ act.triggered.connect( self.on_changed)       
            act.changed.connect( self.on_changed)       
            act.setChecked(False)
            but.addAction(act)
            act.toolchain = tc
            self.actions.append(act)
            
        self.change_toolchain(FromFullBandSignalToClustered)
        
    
    def change_toolchain(self, toolchain):
        i = all_toolchain.index(toolchain)
        self.actions[i].setChecked(True)

    def on_changed(self):
        for a in self.actions: 
            a.changed.disconnect( self.on_changed)
            a.setChecked(False)
            a.changed.connect( self.on_changed)
        self.sender().changed.disconnect( self.on_changed)
        self.sender().setChecked(True)
        self.sender().changed.connect( self.on_changed)
        tc = self.sender().toolchain
        self._change_toolchain(tc)

    def _change_toolchain(self, toolchain):
        self.toolchain = toolchain
        if self.toolbox is not None:
            self.toolbox.setVisible(False)
            self.mainLayout.removeWidget(self.toolbox)
        
        self.toolbox = QToolBox()
        self.mainLayout.addWidget(self.toolbox)
        i = 0
        self.all_params = OrderedDict()
        for name, methods in toolchain.chain.items():
            i+=1
            w = QWidget()
            h= QHBoxLayout()
            w.setLayout(h)            
            self.toolbox.addItem(w,QIcon(':/'+name+'.png'), '{} - {}'.format(i,name))
            
            mparams = MultiMethodsParamWidget(methods = methods, spikesorter = self.spikesorter,  settings = self.settings)
            h.addWidget(mparams)
            self.all_params[name] = mparams
            mparams.run_clicked.connect(self.run_one_method)
    
    def run_one_method(self):
        #~ print 'run_one_method', self.sender()
        mparams = self.sender()
        kargs = mparams.get_dict()
        method =  mparams.get_method()
        print 'run method', method
        print self.spikesorter
        self.spikesorter.run_step(method, **kargs)
        print self.spikesorter
        print self.spikesorter.history[-1]
        
        if  method in sorting:
            self.spikesorter.cluster_colors = { }
        self.need_refresh.emit()
    
    def run_all_chain(self):
        for name, mparams in self.all_params.items():
            print name
            kargs = mparams.get_dict()
            method =  mparams.get_method()
            self.spikesorter.run_step(method, **kargs)
        self.need_refresh.emit()

