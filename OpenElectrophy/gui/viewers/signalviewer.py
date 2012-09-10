# -*- coding: utf-8 -*-
"""
Signal viewers
"""

from tools import *





class SignalViewer(ViewerBase):
    """
    A multi signal viewer trying to be efficient for very big data.
    
    Trick:
       * fast refresh with pure decimation (= bad for aliasing)
       * slow refresh with all point when not moving.
       * if AnaloSignal share same t_start and sampling_rate =>  same time vector
    
    
    
    """
    def __init__(self, parent = None,
                            analogsignals = [ ],
                            xsize = 10.,  xzoom_limits = (0.001, 1000),
                            ylims ='auto',
                            max_point_if_decimate = 2000,
                            ):
                            
        super(SignalViewer,self).__init__(parent,xsize = xsize, 
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
        

        self.plot = CurvePlot()
        self.plot_layout.addWidget(self.plot)
        
        

        self.set_analosignals(analogsignals)
        # TODO fix colors
        #~ colors = ['r', 'g', 'b', 'k'] * 1024
        # AnalogSIgnals

    def set_analosignals(self, analogsignals):
        self.plot.del_all_items()
        self.range_line = make.range(0.,0.)
        self.plot.add_item(self.range_line)
        
        self.analogsignals = analogsignals
        self.analogsignal_curves = [ ]
        for i,anasig in enumerate(analogsignals):
            #~ print i, colors[i]
            curve = make.curve([ ], [ ])#, color =  colors[i])
            self.plot.add_item(curve)
            self.analogsignal_curves.append(curve)
        
    
    def refresh(self, fast = False):
        """
        When fast it do decimate.
        
        """
        #~ import time
        
        xaxis, yaxis = self.plot.get_active_axes()
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        self.plot.setAxisScale(xaxis, t_start, t_stop )
        self.range_line.set_range(self.t,self.t)
        #self.plot.setAxisScale(yaxis, self.y_min , self.y_max )
        #~ print 'self.t', self.t
        #~ print 't_start, t_stop', t_start, t_stop
        

        #~ t1 = time.time()
        #~ t2 = time.time()
        #~ print t2-t1
        
        # AnalogSignals
        for c, curve in enumerate(self.analogsignal_curves):
            ana = self.analogsignals[c]
            t_vect, chunk = get_analogsignal_chunk(ana, t_start*pq.s, t_stop*pq.s)


            # 4 ms
            
            
            #~ print chunk.size
            
            
            # .01ms
            if fast and chunk.size>self.max_point_if_decimate:
                sl = slice(0, None, int(chunk.size/self.max_point_if_decimate))
                curve.set_data(t_vect[sl], chunk[sl])
            else:
                curve.set_data(t_vect, chunk)
            
        self.plot.setAxisScale(yaxis, self.ylims[0], self.ylims[1])
            
            #~ if t_start>=ana.t_start+ana.signal.size/ana.sampling_rate:
                #~ curve.set_data([ ], [ ])
            #~ elif t_stop<ana.t_start: 
                #~ curve.set_data([ ], [ ])
            #~ else:
                #~ ind_start = (t_start-ana.t_start)*ana.sampling_rate
                #~ ind_stop = (t_stop-ana.t_start)*ana.sampling_rate
                #~ t_vect = arange(ind_stop-ind_start)/ana.sampling_rate+t_start
                #~ if ind_start<0:
                    #~ t_vect = t_vect[-ind_start:]
                    #~ ind_start=0
                #~ if ind_stop>ana.signal.size:
                    #~ t_vect = t_vect[:-(ind_stop-ana.signal.size)]
                    #~ ind_stop=ana.signal.size
                #~ curve.set_data(t_vect, ana.signal[ind_start:ind_stop])
                #~ self.plot.setAxisScale(yaxis, self.ylims[0], self.ylims[1])
                
        #~ print 
        
        #Epochs
        # TODO
        #~ colors = ['red', 'green', 'cyan', 'k'] * 1024
            
            #~ print e, epocharray.name

            
        
        

        
        # 700ms
        t1 = time.time()
        self.plot.replot()
        t2 = time.time()
        print fast, t2-t1
        print



