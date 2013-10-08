# -*- coding: utf-8 -*-
"""
Theses widget display individual waveforms and average waveforms.
"""





from .base import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec

from .ndviewer import NDViewer


class FeaturesParallelPlot(SpikeSortingWidgetBase):
    name = 'Features Parallel Plot'
    refresh_on = [  'waveform_features', 'feature_names', ]
    icon_name = 'TODO.png'
    
    plot_dataset = type('Parameters', (DataSet,), { 'max_lines' : IntItem('max_lines', 60) })

    def __init__(self,**kargs):
        super(FeaturesParallelPlot, self).__init__(**kargs)
        
        self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        #~ self.refresh()

    def refresh(self):
        sps = self.spikesorter
        self.ax.clear()
        if sps.waveform_features is None : return
        
        
        for c in sps.cluster_names:
            ind = sps.cluster_displayed_subset[c]
            if ind.size ==0: continue
            if ind.size>self.plot_parameters['max_lines']:
                ind = ind[:self.plot_parameters['max_lines']]
            self.ax.plot( sps.waveform_features[ind,:].transpose() , 
                                                color = sps.cluster_colors[c] )
            if len(sps.feature_names) == sps.waveform_features.shape[1]:
                self.ax.set_xticks(np.arange(sps.waveform_features.shape[1]))
                self.ax.set_xticklabels( sps.feature_names)
            
        self.canvas.draw()



class FeaturesWilsonPlot(SpikeSortingWidgetBase):
    name = 'Features Wilson Plot'
    refresh_on = [  'waveform_features', 'feature_names', ]
    icon_name = 'TODO.png'

    def __init__(self,**kargs):
        super(FeaturesWilsonPlot, self).__init__(**kargs)
        
        self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        #~ self.refresh()

    def refresh(self):
        sps = self.spikesorter
        self.canvas.fig.clear()
        if sps.waveform_features is None : return
        
        ndim = sps.waveform_features.shape[1]
        ndim2 = min(ndim, 16)
        
        if sps.waveform_features.shape[1]>1:
            for c in sps.cluster_names:
                ind = sps.cluster_displayed_subset[c]
                for i in range(ndim2):
                    for j in range(i+1, ndim2):
                        p = (j-1)*(ndim2-1)+i+1
                        ax = self.canvas.fig.add_subplot(ndim2-1, ndim2-1, p)
                        ax.plot(sps.waveform_features[ind,i], sps.waveform_features[ind,j], 
                                                        marker = '.',linestyle = 'None',
                                                        color = sps.cluster_colors[c]) 
                        if i==0:
                            ax.set_ylabel( sps.feature_names[j] )
                        if j==ndim-1:
                            ax.set_xlabel( sps.feature_names[i]) 
                        ax.set_xticks([ ])
                        ax.set_yticks([ ])
        self.canvas.draw()



class Features3D(SpikeSortingWidgetBase):
    name = 'Features 3D'
    refresh_on = [  'waveform_features', 'feature_names', ]
    icon_name = 'TODO.png'
    
    plot_dataset = type('Parameters', (DataSet,), { 'max_points_by_cluster' : IntItem('max_points_by_cluster', 500) })
    
    def __init__(self,**kargs):
        super(Features3D, self).__init__(**kargs)
        
        h = QHBoxLayout()
        self.mainLayout.addLayout(h)
        
        h.addWidget(QLabel('Choose dim'))
        self.combos = [ ]
        for i in range(3):
            cb = QComboBox()
            self.combos.append(cb)
            cb.activated.connect(self.change_dim)
            h.addWidget(cb)
        
        self.canvas = SimpleCanvas()
        self.ax = Axes3D(self.canvas.fig)
        self.mainLayout.addWidget( self.canvas )
        
        #~ self.refresh()


    def change_dim(self, index = None):
        sps = self.spikesorter
        if sps.waveform_features is None : return
        self.ax.clear()
        vects = [ ]
        for i in range(3):
            
            ind = self.combos[i].currentIndex()
            vects.append( sps.waveform_features[:,ind] )
        
        for c in sps.cluster_names:
            ind = sps.cluster_displayed_subset[c]
            if ind.size>self.plot_parameters['max_points_by_cluster']:
                ind = ind[:self.plot_parameters['max_points_by_cluster']]
            if ind.size>0:
                self.ax.scatter(vects[0][ind], vects[1][ind], vects[2][ind], 
                                                color = sps.cluster_colors[c],
                                                )
        self.canvas.draw()

    def refresh(self):
        sps = self.spikesorter
        for i in range(3):
            self.combos[i].clear()
        if sps.waveform_features is None : return
        
        ndim = sps.waveform_features.shape[1]
        for i in range(3):
            #~ self.combos[i].clear()
            self.combos[i].addItems( [ sps.feature_names[n] for n in range(ndim) ] )
            if i<ndim:
                self.combos[i].setCurrentIndex(i)
        
        self.change_dim()




class FeaturesEvolutionInTime(SpikeSortingWidgetBase):
    name = 'Evolution of features over time'
    refresh_on = [  'waveform_features', 'feature_names', ]
    icon_name = 'office-chart-line.png'
    
    #~ plot_dataset = type('Parameters', (DataSet,), { 'max_points_by_cluster' : IntItem('max_points_by_cluster', 500) })
    
    def __init__(self,**kargs):
        super(FeaturesEvolutionInTime, self).__init__(**kargs)
    
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.comboChanged)
        self.mainLayout.addWidget(self.combo)
        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.mainLayout.addWidget(self.canvas)
        
        #~ self.refresh()
    
    def comboChanged(self, i):
        if i<0:return
        sps = self.spikesorter
        self.fig.clear()
        grid = GridSpec(1,len(sps.segs))
        for s in range(len(sps.segs)):
            slice = sps.seg_spike_slices[s]
            features_of_seg = sps.waveform_features[slice, i]
            ax = self.fig.add_subplot(grid[s])
            ax.set_title('Segment {}'.format(s))
            ax.set_xlabel('times')
            if s==0:
                ax.set_ylabel(sps.feature_names[i])
            for c in sps.cluster_names:
                if not sps.active_cluster[c]: continue
                select = c==sps.spike_clusters[slice]
                feature = features_of_seg[select]
                times = sps.spike_index_array[s][select]/sps.sig_sampling_rate
                ax.plot(times, feature, color = sps.cluster_colors[c], ls = '--', marker = '.')
        self.canvas.draw()

    
    def refresh(self):
        sps = self.spikesorter
        self.combo.clear()
        self.fig.clear()
        if sps.waveform_features is None : return
        
        
        ndim = sps.waveform_features.shape[1]
        self.combo.addItems( [ sps.feature_names[n] for n in range(ndim) ] )



class FeaturesNDViewer(SpikeSortingWidgetBase):
    name = 'Features ND Viewer'
    refresh_on = [  'waveform_features', 'feature_names', ]
    icon_name = 'Clustering.png'

    def __init__(self,settings = None, **kargs):
        super(FeaturesNDViewer, self).__init__(settings = settings, **kargs)

        self.ndviewer = NDViewer(settings = settings,
                                                            show_tour = True,
                                                            show_select_tools = True,)
        self.mainLayout.addWidget(self.ndviewer)
        
        self.ndviewer.selection_changed.connect(self.newSelectionInViewer )
        self.ndviewer.canvas.mpl_connect('button_press_event', self.rigthClickOnNDViewer)

    def refresh(self):
        sps = self.spikesorter
        if sps.waveform_features is None :
            self.ndviewer.change_point(np.empty((0,2)) )
            return
        self.ndviewer.change_point(sps.waveform_features, data_labels = sps.spike_clusters, 
                                                        colors = sps.cluster_colors,
                                                        subset = sps.cluster_displayed_subset,
                                                        )
    
    def newSelectionInViewer(self):
        sps = self.spikesorter
        
        sps.selected_spikes = self.ndviewer.actualSelection
        for c, active  in sps.active_cluster.items():
            if not active:
                ind = sps.spike_clusters ==c
                sps.selected_spikes[ind] = False
        self.spike_selection_changed.emit()
    
    def on_spike_selection_changed(self):
        sps = self.spikesorter
        if sps.waveform_features is None : return
        #~ self.ndviewer.selection_changed.disconnect(self.newSelectionInViewer )
        self.ndviewer.changeSelection(sps.selected_spikes, emit_signal = False)
        #~ self.ndviewer.selection_changed.connect(self.newSelectionInViewer )

    def rigthClickOnNDViewer(self,event):
        if hasattr(self.ndviewer, 'lasso'): return
        if self.ndviewer.canvas.widgetlock.locked(): return
        if event.button == 3: 
            menu = QMenu()
            act = menu.addAction(QIcon(':/user-trash.png'), u'Move selection to trash')
            act.triggered.connect(self.moveSpikeToTrash)
            act = menu.addAction(QIcon(':/merge.png'), u'Group selection in one unit')
            act.triggered.connect(self.createNewClusterWithSpikes)
            menu.exec_(self.cursor().pos())
    
    def moveSpikeToTrash(self):
        ind = self.ndviewer.actualSelection
        self.spikesorter.spike_clusters[ ind ]= -1
        
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()

    def createNewClusterWithSpikes(self):
        ind = self.ndviewer.actualSelection
        self.spikesorter.spike_clusters[ ind ]= max(self.spikesorter.cluster_names.keys())+1
        
        self.spikesorter.check_display_attributes()
        self.spike_clusters_changed.emit()
        self.refresh()



