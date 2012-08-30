# -*- coding: utf-8 -*-
"""
Theses widget display individual waveforms and average waveforms.
"""





from .base import *

from matplotlib.gridspec import GridSpec

class AverageWaveforms(SpikeSortingWidgetBase):
    name = 'Average waveforms'
    refresh_on = [  'spike_waveforms', 'spike_clusters', 'cluster_names']
    icon_name = 'plot-waveform.png'
    
    
    def __init__(self,**kargs):
        super(AverageWaveforms, self).__init__(**kargs)
        self.canvas = SimpleCanvasAndTool( )
        #~ self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        self.refresh()

    def refresh(self, step = None):
        sps = self.spikesorter
        if sps.spike_waveforms is None : return
            
        # recreate axes
        self.fig.clear()
        self.axs = [ ]
        self.ax2s = [ ]
        ax = None
        ax2 = None
        grid = GridSpec(4,sps.trodness)
        for i in range(sps.trodness):
            ax = self.fig.add_subplot( grid[0:3,i] ,  sharex = ax, sharey = ax)
            self.axs.append( ax )
            ax.axvline(0, color = 'r', ls = '--', alpha = .7)
            ax2 = self.fig.add_subplot( grid[3,i] ,  sharex = ax, sharey = ax2)
            self.ax2s.append(ax2)
            ax2.axvline(0, color = 'r', ls = '--', alpha = .7)
            ax.get_xaxis().set_visible(False)
            if i !=0:
                ax.get_yaxis().set_visible(False)
                ax2.get_yaxis().set_visible(False)
            else:
                ax.set_ylabel('mean +- sd')
                ax2.set_ylabel('sd')
                
        times = (np.arange(-sps.left_sweep, sps.right_sweep+1)/sps.wf_sampling_rate).rescale('ms').magnitude
        
        # plots
        for i in range(sps.trodness):
            ax = self.axs[i]
            if len(sps.cluster_names) == 0:
                slices = [ slice(None,None,None) ]
                colors = [ 'b' ]
            else:
                slices = [c==sps.spike_clusters for c in sps.cluster_names]
                colors = [ sps.cluster_colors[c] for c in sps.cluster_names]
            
            for sl,color in zip(slices, colors):
                m  = np.mean(sps.spike_waveforms[sl,i,:], axis = 0)
                sd = np.std(sps.spike_waveforms[sl,i,:], axis = 0)
                ax.plot(times, m, linewidth=2,color = color,)
                ax.fill_between(times, m-sd, m+sd ,
                                    color = color, alpha = .3)
                self.axs[0].set_xlim(times[0], times[-1])
                self.ax2s[i].plot(times, sd, linewidth=2,color = color,)
        
        self.canvas.draw()


class AllWaveforms(SpikeSortingWidgetBase):
    name = 'All aveforms'
    refresh_on = [  'spike_waveforms', 'spike_clusters', 'cluster_names']
    icon_name = 'plot-waveform.png'
    
    #magic button fom SpikeSortingWidgetBase
    plot_dataset = type('Parameters', (DataSet,), { 'max_waveform_by_cluster' : IntItem('max_waveform_by_cluster', 25) })
    
    
    def __init__(self,**kargs):
        super(AllWaveforms, self).__init__(**kargs)
        
        #~ self.canvas = SimpleCanvasAndTool( )
        self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
       
        # for selection
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)
        self.actualSelection = np.array([ ] , dtype='i')
        self.epsilon = .5
        self.selected_lines = None
        self.already_in_pick = False # to avoid multiple pick
        
        self.refresh()
    
    def refresh(self, step = None):
        
        sps = self.spikesorter
        self.axs = [ ]
        self.fig.clear()
        self.selected_lines = None
        
        if sps.spike_waveforms is None : return
            
        # recreate axes
        ax = None
        grid = GridSpec(1,sps.trodness)
        for i in range(sps.trodness):
            ax = self.fig.add_subplot( grid[i] , sharex = ax, sharey = ax)
            self.axs.append( ax )
            if i !=0:
                ax.get_yaxis().set_visible(False)
        
        times = (np.arange(-sps.left_sweep, sps.right_sweep+1)/sps.wf_sampling_rate).rescale('ms').magnitude
        
        # plots
        self.lines = [ ]
        for i in range(sps.trodness):
            ax = self.axs[i]
            ax.clear()
            ax.axvline(0, color = 'r', ls = '--', alpha = .7)
            self.lines.append([ ])
        
        self.ploted_indices =[ ]
        for c in sps.cluster_names.keys():
            ind = sps.cluster_displayed_subset[c]
            if ind.size> self.plot_parameters['max_waveform_by_cluster']:
                ind = ind[:self.plot_parameters['max_waveform_by_cluster']]
            self.ploted_indices.extend( ind )
            for i in range(sps.trodness):
                if ind.size>0: 
                    lines  = self.axs[i].plot( times, sps.spike_waveforms[ind, i,  :].transpose(),
                                                color = sps.cluster_colors[c],
                                                picker=self.epsilon,
                                                )
                    self.lines[i] += lines
                else:
                    self.lines[i].append(None)
        self.ploted_indices = np.array(self.ploted_indices)
        self.canvas.draw()
    
    
    #cid = self.canvas.mpl_connect('pick_event', self.onPick)
    # self.canvas.mpl_disconnect(e)
    
    def refresh_selection(self):
        if self.selected_lines is not None:
            for i, ax in enumerate(self.axs):
                ax.lines.remove(self.selected_lines[i])
        
        times = (np.arange(-sps.left_sweep, sps.right_sweep+1)/sps.wf_sampling_rate).rescale('ms').magnitude
        
        if self.actualSelection.size>=1:
            self.selected_lines = [ ]
            for i, ax in enumerate(self.axs):
                lines  = self.axs[i].plot(times, self.spikesorter.spike_waveforms[self.actualSelection[0],i,:],
                                                    color = 'm',
                                                    linewidth = 4,
                                                    alpha = .6,
                                                    )
                self.selected_lines += lines
        else:
            self.selected_lines = None
        self.canvas.draw()
        
        
    
    def onPick(self , event):
        #~ print 'on pick'
        if self.already_in_pick: return
        self.canvas.mpl_disconnect(self.mpl_event_id)
        if isinstance(event.artist, Line2D):
            i =  self.axs.index(event.artist.get_axes())
            if event.artist not in self.lines[i]:
                self.actualSelection = np.array([ ] , dtype='i')
            else:
                num_line = self.lines[i].index(event.artist)
                self.actualSelection = self.ploted_indices[[num_line]]
        else:
            self.actualSelection = np.array([ ] , dtype='i')
        self.refresh_selection()
        self.spike_selection_changed.emit()
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)
        
        # this is a ugly patch to avoid multiple onPick at the same time
        self.already_in_pick = True
        self.timer = QTimer(interval = 1000., singleShot = True)
        #~ self.timer = QTimer( )
        #~ self.timer.setInterval( 1000.)
        #~ self.timer.setSingleShot( True )
        
        self.timer.timeout.connect(self.do_pick_again)
        self.timer.start()
    
    def do_pick_again(self):
        self.already_in_pick = False
    
    
    def setSpikeSelection(self, ind):
        # TO avoid larsen
        self.canvas.mpl_disconnect(self.mpl_event_id)
        self.actualSelection =  ind
        self.refresh_selection()
        self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)



