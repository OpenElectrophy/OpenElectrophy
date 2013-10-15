# -*- coding: utf-8 -*-
"""
Theses widget display individual waveforms and average waveforms.
"""





from .base import *

from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

class AverageWaveforms(SpikeSortingWidgetBase):
    name = 'Average waveforms'
    refresh_on = [  'spike_waveforms', 'spike_clusters', 'cluster_names']
    icon_name = 'plot-waveform.png'
    
    plot_dataset = type('Parameters', (DataSet,), { 'estimation' : ChoiceItem('max_waveform_by_cluster',  ['Median + MAD', 'Mean + STD']),
                                                                                                'deviation_coeff' : FloatItem('deviation coeff',  default = 2.5),
                                                                                                })
    
    def __init__(self,**kargs):
        super(AverageWaveforms, self).__init__(**kargs)
        self.canvas = SimpleCanvasAndTool( )
        self.canvas.toolbar.hide()
        self.canvas.toolbar.pan()
        #~ self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        #~ self.refresh()
        
        sps = self.spikesorter
        
        # create axes
        self.axs = [ ]
        self.ax2s = [ ]
        ax = None
        ax2 = None
        grid = GridSpec(3,sps.trodness, wspace=0, hspace=0)
        for i in range(sps.trodness):
            ax = self.fig.add_subplot( grid[0:2,i] ,  sharex = ax, sharey = ax)
            self.axs.append( ax )
            #~ ax.axvline(0, color = 'r', ls = '--', alpha = .7)
            ax2 = self.fig.add_subplot( grid[2,i] ,  sharex = ax, sharey = ax2)
            self.ax2s.append(ax2)
            #~ ax2.axvline(0, color = 'r', ls = '--', alpha = .7)
            ax.get_xaxis().set_visible(False)
            if i !=0:
                ax.get_yaxis().set_visible(False)
                ax2.get_yaxis().set_visible(False)
            ax2.set_xticks(np.arange(-10,10))
            ax2.set_xticklabels(['']*20)
        

    def refresh(self):
        sps = self.spikesorter
        for i in range(sps.trodness):
            self.axs[i].clear()
            self.ax2s[i].clear()

        if sps.spike_waveforms is None : 
            self.canvas.draw()
            return
        
        # recreate axes
        
                
        times = (np.arange(-sps.left_sweep, sps.right_sweep+1)/sps.wf_sampling_rate).rescale('ms').magnitude
        
        for i in range(sps.trodness):
            #~ self.axs[i].clear()
            #~ self.ax2s[i].clear()
            if i==0:
                self.axs[i].set_ylabel(self.plot_parameters['estimation'])
                self.ax2s[i].set_ylabel(self.plot_parameters['estimation'].split('+')[-1])
        
        # plots
        coeff = self.plot_parameters['deviation_coeff']
        #~ print sps.cluster_names.keys()
        #~ print sps.median_centers.keys()
        _max  = 0.
        for c in sps.cluster_names:
            #~ print c
            if not sps.active_cluster[c]: continue
            for i in range(sps.trodness):
                if self.plot_parameters['estimation'] == 'Median + MAD':
                    m = sps.median_centers[c][i,:]
                    sd = sps.mad_deviation[c][i,:]
                elif self.plot_parameters['estimation']== 'Mean + STD':
                    m = sps.mean_centers[c][i,:]
                    sd = sps.std_deviation[c][i,:]
                
                color = sps.cluster_colors[c]
                self.axs[i].plot(times, m, linewidth=2,color = color,)
                self.axs[i].fill_between(times, m-sd*coeff, m+sd*coeff ,
                                    color = color, alpha = .3)
                self.ax2s[i].plot(times, sd, linewidth=2,color = color,)
                
                self.axs[i].axvline(0, color = 'r', ls = '--', alpha = .7)
                self.ax2s[i].axvline(0, color = 'r', ls = '--', alpha = .7)
                
                _max = max(_max, max(sd))
                
        self.axs[0].set_xlim(times[0], times[-1])
        
        for i in range(sps.trodness):
            self.ax2s[i].set_xticks(np.arange(-10,10))
            self.ax2s[i].set_xticklabels(['']*20)

        self.axs[0].set_xlim(times[0], times[-1])
        #~ self.ax2s[0].set_xlim(times[0], times[-1])
        self.ax2s[0].set_ylim(0, _max*1.1)
        
        #~ for i in range(sps.trodness):
            #~ ax = self.axs[i]
            #~ if len(sps.cluster_names) == 0:
                #~ slices = [ slice(None,None,None) ]
                #~ colors = [ 'b' ]
            #~ else:
                #~ slices = [c==sps.spike_clusters for c in sps.cluster_names if sps.active_cluster[c]]
                #~ colors = [ sps.cluster_colors[c] for c in sps.cluster_names if sps.active_cluster[c]]
            #~ for sl,color in zip(slices, colors):
                #~ if self.plot_parameters['estimation'] == 'Median + MAD':
                    #~ m  = np.median(sps.spike_waveforms[sl,i,:], axis = 0)
                    #~ sd = np.median(np.abs(sps.spike_waveforms[sl,i,:]-m), axis = 0)/  .6745
                #~ elif self.plot_parameters['estimation']== 'Mean + STD':
                    #~ m  = np.mean(sps.spike_waveforms[sl,i,:], axis = 0)
                    #~ sd = np.std(sps.spike_waveforms[sl,i,:], axis = 0)

                #~ coeff = self.plot_parameters['deviation_coeff']
                #~ ax.plot(times, m, linewidth=2,color = color,)
                #~ ax.fill_between(times, m-sd*coeff, m+sd*coeff ,
                                    #~ color = color, alpha = .3)
                #~ self.axs[0].set_xlim(times[0], times[-1])
                #~ self.ax2s[i].plot(times, sd, linewidth=2,color = color,)

        self.canvas.draw()

class AllWaveforms(SpikeSortingWidgetBase):
    name = 'All waveforms'
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
        #self.actualSelection = np.array([ ] , dtype='i')
        self.epsilon = .5
        self.selected_lines = None
        self.already_in_pick = False # to avoid multiple pick
        
        #~ self.refresh()
    
    def refresh(self):
        
        sps = self.spikesorter
        self.axs = [ ]
        self.fig.clear()
        self.selected_lines = None
        
        if sps.spike_waveforms is None : 
            self.canvas.draw()
            return
            
        # recreate axes
        ax = None
        grid = GridSpec(1,sps.trodness, wspace=0, hspace=0)
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
            ax.set_xticks(np.arange(-10,10))
            ax.set_xticklabels(['']*20)
        
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
        sps = self.spikesorter
        if sps.spike_waveforms is None : 
            return
        
        if self.selected_lines is not None:
            for i, ax in enumerate(self.axs):
                ax.lines.remove(self.selected_lines[i])
        
        times = (np.arange(-sps.left_sweep, sps.right_sweep+1)/sps.wf_sampling_rate).rescale('ms').magnitude
        
        #~ if self.actualSelection.size>=1:
        if np.any(sps.selected_spikes):
            self.selected_lines = [ ]
            for i, ax in enumerate(self.axs):
                sel,  = np.where(sps.selected_spikes)
                lines  = self.axs[i].plot(times, self.spikesorter.spike_waveforms[sel[0],i,:],
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
        sps = self.spikesorter
        if self.already_in_pick: return
        self.canvas.mpl_disconnect(self.mpl_event_id)
        if isinstance(event.artist, Line2D):
            i =  self.axs.index(event.artist.get_axes())
            if event.artist not in self.lines[i]:
                #~ self.actualSelection = np.array([ ] , dtype='i')
                sps.selected_spikes[:] = False
            else:
                num_line = self.lines[i].index(event.artist)
                sps.selected_spikes[:] = False
                sps.selected_spikes[self.ploted_indices[num_line]] = True
                #~ self.actualSelection = self.ploted_indices[[num_line]]
        else:
            #~ self.actualSelection = np.array([ ] , dtype='i')
            sps.selected_spikes[:] = False
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
    
    
    def on_spike_selection_changed(self):
        # TO avoid larsen
        #~ self.canvas.mpl_disconnect(self.mpl_event_id)
        #~ self.actualSelection =  ind
        self.refresh_selection()
        #~ self.mpl_event_id = self.canvas.mpl_connect('pick_event', self.onPick)



