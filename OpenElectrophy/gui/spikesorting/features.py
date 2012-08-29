# -*- coding: utf-8 -*-
"""
Theses widget display individual waveforms and average waveforms.
"""





from .base import *

from mpl_toolkits.mplot3d import Axes3D


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
        self.refresh()

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.waveform_features is None : return
        
        self.ax.clear()
        for c in sps.cluster_names.keys():
            ind = sps.cluster_displayed_subset[c]
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
        self.refresh()

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.waveform_features is None : return
        
        ndim = sps.waveform_features.shape[1]
        ndim2 = min(ndim, 16)
        self.canvas.fig.clear()
        if sps.waveform_features.shape[1]>1:
            for c in sps.cluster_names.keys():
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

