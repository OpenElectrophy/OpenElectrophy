# -*- coding: utf-8 -*-
"""
Signal viewers
"""

from tools import *
from guiqwt.styles import CurveParam




class SignalViewerQwt(ViewerWithXSizeAndYlim):
    """
    A multi signal viewer trying to be efficient for very big data.
    
    Trick:
       * fast refresh with pure decimation (= bad for aliasing)
       * slow refresh with all point when not moving.
       * if AnaloSignal share same t_start and sampling_rate =>  same time vector
    
    
    
    """
    def __init__(self, parent = None,
                            analogsignals = [ ],
                            spiketrains_on_signals = None,
                            xsize = 10.,  xzoom_limits = (0.001, 1000),
                            ylims ='auto',
                            max_point_if_decimate = 2000,
                            show_toolbar = True,
                            **kargs
                            ):
                            
        super(SignalViewerQwt,self).__init__(parent,xsize = xsize, 
                                xzoom_limits = xzoom_limits, show_toolbar = show_toolbar, **kargs)
        
        self.max_point_if_decimate = max_point_if_decimate
        
        
        if ylims =='auto' and len(analogsignals)>0:
            ylims = [0,0]
            for ana in analogsignals:
                ylims[1] = max([max(ana.magnitude) , ylims[1]])
                ylims[0] = min([min(ana.magnitude), ylims[0]])
        elif type(ylims) == list:
            ylims = list(ylims)
        else:
            ylims = [-10,10]
        self.ylims_changer.set_ylims(ylims)
        
        self.plot = CurvePlot()
        self.plot_layout.addWidget(self.plot)
        
        # inialize
        self.clear_all()
        self.set_analosignals(analogsignals)
        self.set_spiketrains_on_signals(spiketrains_on_signals)
    
    def clear_all(self):
        self.plot.del_all_items(except_grid=False)
        self.range_line = make.range(0.,0.)
        self.plot.add_item(self.range_line)
        self.analogsignal_curves = [ ]
        self.spikeonsignal_curves = [ ]

    def set_analosignals(self, analogsignals):
        self.analogsignals = analogsignals
        self.analogsignal_curves = [ ]
        self.times_familly = { }# signal sharing same size sampling and t_start are in the same familly
        for i,anasig in enumerate(analogsignals):
            key = (float(anasig.t_start.rescale('s').magnitude), float(anasig.sampling_rate.rescale('Hz').magnitude), anasig.size)
            if  key in self.times_familly:
                self.times_familly[key].append(i)
            else:
                self.times_familly[key] = [ i ]
            curve = make.curve([ ], [ ])#, color =  colors[i])
            self.plot.add_item(curve)
            self.analogsignal_curves.append(curve)
    
    def set_spiketrains_on_signals(self, spiketrains_on_signals):
        self.spiketrains_on_signals = spiketrains_on_signals
        if spiketrains_on_signals is None: return
        for c, curves in enumerate(self.spikeonsignal_curves):
            for s, curve in enumerate(curves):
                self.plot.del_item(curve)
        assert len(spiketrains_on_signals)==len(self.analogsignals), 'must have same size'
        self.spikeonsignal_curves = [ ]
        for c,spiketrains in enumerate(spiketrains_on_signals):
            self.spikeonsignal_curves.append([])
            for s,sptr in enumerate(spiketrains):
                color = ['red', 'green', 'blue', 'magenta'][s%4]
                curve = make.curve([ ], [ ], markerfacecolor=  color,marker = 'o' , linestyle = '', markersize = 7)
                self.plot.add_item(curve)
                self.spikeonsignal_curves[-1].append(curve)
                
                # compute index and signal value for times
                ana = self.analogsignals[c]
                spike_indexes = np.round(((sptr-ana.t_start)*ana.sampling_rate).simplified.magnitude).astype(int)
                spike_values = ana[spike_indexes].magnitude
                

                
                
    
        #~ self.change_curve_param()
    
    def open_configure_dialog(self):
        # This is a test
        curve = self.analogsignal_curves[0]
        #~ p = curve.curveparam.line # LineStyleParam
        p = curve.curveparam #CurveParam
        p.edit()
        curve.curveparam.update_curve(curve) 
        #~ p.update_curve(curve)
        self.refresh()
    
    #~ def change_curve_param(self):
        #~ for curve in self.analogsignal_curves:
            #~ param = curve.curveparam
            #~ param.line.color = QColor('red')
            #~ param.symbol.facecolor = QColor('green')
            #~ param.symbol.edgecolor = QColor('blue')
            #~ param.line.style = '--'
            #~ curve.update_params()
            #~ param.update_curve(curve)
    
    def refresh(self, fast = False):
        """
        When fast it do decimate.
        
        """
        #~ t1 = time.time()
        
        xaxis, yaxis = self.plot.get_active_axes()
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        for key, sig_nums in self.times_familly.items():
            if fast:
                decimate = self.max_point_if_decimate
            else:
                decimate = None
            t_vect, sl = get_analogsignal_slice(self.analogsignals[sig_nums[0]], t_start*pq.s, t_stop*pq.s,
                                                        return_t_vect = True,decimate = decimate,)
            for c in sig_nums:
                curve = self.analogsignal_curves[c]
                ana = self.analogsignals[c]
                chunk = ana.magnitude[sl]
                curve.set_data(t_vect, chunk)
                
        if self.spiketrains_on_signals is not None:
            for c, curves in enumerate(self.spikeonsignal_curves):
                for s, curve in enumerate(curves):
                    sptr = self.spiketrains_on_signals[c][s]
                    ana = self.analogsignals[c]
                    times = sptr[(sptr>=t_start*pq.s) & (sptr<t_stop*pq.s)]
                    pos = np.round(((times-ana.t_start)*ana.sampling_rate).simplified.magnitude).astype(int)
                    curve.set_data(times, ana.magnitude[pos])
                
        self.plot.setAxisScale(xaxis, t_start, t_stop )
        self.range_line.set_range(self.t,self.t)
        self.plot.setAxisScale(yaxis, self.ylims[0], self.ylims[1])

        
        # 700ms
        self.plot.replot()
        #~ t2 = time.time()
        #~ print fast, self.__class__, t2-t1
        #~ print
        
        self.is_refreshing = False


SignalViewer = SignalViewerQwt

# This is for testing
"""

class SignalViewerMpl(ViewerBase):
    def __init__(self, parent = None,
                            analogsignals = [ ],
                            xsize = 10.,  xzoom_limits = (0.001, 1000),
                            ylims ='auto',
                            max_point_if_decimate = 2000,
                            ):
                            
        super(SignalViewerMpl,self).__init__(parent,xsize = xsize, 
                                xzoom_limits = xzoom_limits)
        self.max_point_if_decimate = max_point_if_decimate
        if ylims =='auto' and len(analogsignals)>0:
            self.ylims = [0,0]
            for ana in analogsignals:
                self.ylims[1] = max([ana.max(), self.ylims[1]])
                self.ylims[0] = min([ana.min(), self.ylims[0]])
        elif type(ylims) == list:
            self.ylims = list(ylims)
        else:
            self.ylims = [-10,10]

        self.canvas = SimpleCanvas()
        self.plot_layout.addWidget(self.canvas)
        self.ax = self.canvas.fig.add_subplot(1,1,1)
        self.set_analosignals(analogsignals)

    def set_analosignals(self, analogsignals):
        self.ax.clear()
        self.vline = self.ax.axvline(self.t)
        
        self.analogsignals = analogsignals
        self.analogsignal_curves = [ ]
        self.times_familly = { }# signal sharing same size sampling and t_start are in the same familly
        for i,anasig in enumerate(analogsignals):
            key = (float(anasig.t_start.rescale('s').magnitude), float(anasig.sampling_rate.rescale('Hz').magnitude), anasig.size)
            if  key in self.times_familly:
                self.times_familly[key].append(i)
            else:
                self.times_familly[key] = [ i ]
            curve, = self.ax.plot([],[])
            self.analogsignal_curves.append(curve)
    
    def refresh(self, fast = False):
        t1 = time.time()
        
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        self.ax.set_xlim(t_start, t_stop )
        self.vline.set_xdata(self.t)
        
        for key, sig_nums in self.times_familly.items():
            if fast:
                decimate = self.max_point_if_decimate
            else:
                decimate = None
            t_vect, sl = get_analogsignal_slice(self.analogsignals[sig_nums[0]], t_start*pq.s, t_stop*pq.s,
                                                        return_t_vect = True,decimate = decimate,)
            
            for c in sig_nums:
                curve = self.analogsignal_curves[c]
                ana = self.analogsignals[c]
                chunk = ana.magnitude[sl]
                curve.set_data(t_vect, chunk)
            
        self.ax.set_ylim(self.ylims[0], self.ylims[1])

        
        # 700ms
        self.canvas.draw()
        t2 = time.time()
        print fast, self.__class__, t2-t1
        print
        
        self.is_refreshing = False
"""



