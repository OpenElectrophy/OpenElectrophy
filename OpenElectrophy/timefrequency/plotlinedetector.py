# -*- coding: utf-8 -*-
"""

High level object for the display of a :class:`.LineDetector` object, i.e. 
the scalogram, the filtered signal and detected oscillations.

"""


import matplotlib 
from matplotlib import pyplot
import numpy

from ..tools import fft_passband_filter

class PlotLineDetector():
    def __init__(self, figure = None,
                            lineDetector = None):
        """ 
        Construct a :class:`.PlotLineDetector` object.
        
        Parameters
        ----------
        
        figure : Figure instance, optional
            Figure instance to display the LineDetector object.
        lineDetector : LineDetector instance, optional
            LineDetector instance to be displayed.
            
            
        Example
        -------
        
        >>> ana = AnalogSignal.load(id)    
        >>> ld = LineDetector(ana)
        >>> ld.computeAllStep()  
        >>> pld = PlotLineDetector(lineDetector=ld)
        >>> pld.reDrawAll()
        
        """
        self.fig = figure
        self.lineDetector = lineDetector
        
        #~ self.axMap = self.fig.add_subplot(2,1,1 )
        #~ self.axSig = self.fig.add_subplot(2,1,2 , sharex = self.axMap)
        self.axMap = self.fig.add_axes([0.05 , 0.45 , .9 , 0.45 ] )
        self.axSig = self.fig.add_axes([0.05 , 0.05 , .9 , 0.35 ] , sharex = self.axMap)       
        self.ax_colorbar = self.fig.add_axes([0.05 , 0.95 , .9 , 0.03 ] )
        
        
        
        self.clear()

    def clear(self):
        """ Clear all axes.  """
        self.axMap.clear()
        self.axSig.clear()
        self.ax_colorbar.clear()
        
        
        self.im = None
        self.lineSig = None
        self.rect_detect = None
        self.rect_ref = None
        self.line_threshold =  None
        self.threshline1 = None
        self.threshline2 = None
        self.lineMaximas = None
        self.lineOscillations1 = [ ]
        self.lineOscillations2 = [ ]
        self.span = None        
    
    def reDrawAll(self):
        """ 
        Redraw everything, i.e. the scalogram, the filtered signal, the 
        reference and detection zones, maxima, oscillations and the threshold.
        """
        self.clear()
        self.plotMap()
        self.plotFilteredSig()
        self.plotReferenceZone()
        self.plotDetectionZone()
        self.plotOscillations()
        self.plotMax()
        self.plotThreshold()
        
        self.axMap.set_xlim( self.lineDetector.t_start, self.lineDetector.t_stop)
        self.axMap.set_ylim( self.lineDetector.f_start, self.lineDetector.f_stop)

    def plotMap(self):
        """ Plot the scalogram. """
        if len(self.axMap.get_images())==1:
            self.axMap.get_images()[0].remove()
            
        self.im = self.lineDetector.timeFreq.plot(self.axMap,  cax = self.ax_colorbar, colorbar = True)
        #~ self.fig.colorbar(im,ax = self.axMap, cax = self.ax_colorbar ,orientation='horizontal')
        

    def plotMax(self):
        """ Plot the maxima and set axis limits. """
        xl = self.axMap.get_xlim()
        yl = self.axMap.get_ylim()
        if self.lineMaximas  is not  None:
            self.axMap.lines.remove(self.lineMaximas)
        self.lineMaximas, = self.axMap.plot( self.lineDetector.list_max.time, self.lineDetector.list_max.freq, 'o', markersize=6, color = 'w')
        self.axMap.set_xlim(xl)
        self.axMap.set_ylim(yl)
        
    def plotFilteredSig(self):
        """ Plot filtered signal. """
        _ ,_ , f1, f2 = self.lineDetector.detection_zone
        if self.lineSig  is not  None:
            self.axSig.lines.remove(self.lineSig)
        
        #TODO
        ana = self.lineDetector.anaSig
        nq = ana.sampling_rate.magnitude/2.
        sig_f = fft_passband_filter(ana.magnitude, f_low =f1.magnitude/nq,f_high=f2.magnitude/nq)
        self.lineSig, = self.axSig.plot(ana.times, sig_f , color = 'g')
        
        #~ self.lineSig, = self.lineDetector.anaSig.plot_filtered(ax = self.axSig , 
                                                                #~ f1 = f1,
                                                                #~ f2 = f2,
                                                                #~ color = 'g',
                                                                #~ )
        self.axSig.set_xlim( self.lineDetector.t_start, self.lineDetector.t_stop)
        self.axSig.set_ylim()
        #~ self.lineDetector.anaSig.plot_natural(ax = self.axSig , 
                                                                #~ color='k',
                                                                #~ )
    
    def plotThreshold(self):
        """ Plot the threshold in the colorbar of the scalogram. """
        if self.threshline1  is not  None:
            self.ax_colorbar.lines.remove(self.threshline1)
        
        if self.im is not None:
            cl = self.im.get_clim()
            if self.lineDetector.threshold<max(cl):
                t = (self.lineDetector.threshold-cl[0]) / (cl[1]-cl[0])
                self.threshline1 = self.ax_colorbar.axvline(t, color = 'w', linewidth = 2.5)
            else:
                self.threshline1 = None
        
        if self.threshline2  is not None:
            self.axSig.lines.remove(self.threshline2)        
        self.threshline2 = self.axSig.axhline(self.lineDetector.threshold, color = 'k', linewidth = 1., alpha = .8)
        
        
    
    def plotOscillations(self):
        """ Plot the detected oscillations as lines in the scalogram and the on
        top of the filtered signal. """
        xl = self.axMap.get_xlim()
        yl = self.axMap.get_ylim()
        
        for l in self.lineOscillations1:
            self.axMap.lines.remove(l)
        for l in self.lineOscillations2:
            self.axSig.lines.remove(l)        
        
        self.lineOscillations1 = [ ]
        self.lineOscillations2 = [ ]
        for osci in self.lineDetector.list_oscillation:
            l = self.axMap.plot( osci.time_line, osci.freq_line , linewidth = 3, color='m')
            self.lineOscillations1 += l
            l = osci.plot_line_on_signal(ax = self.axSig,
                                                color = 'm',
                                                sampling_rate =self.lineDetector.anaSig.sampling_rate,
                                                )
            self.lineOscillations2 += l

        self.axMap.set_xlim(xl)
        self.axMap.set_ylim(yl)

    def plotDetectionZone(self):
        """ Plot a magenta box around the detection zone. """
        if self.rect_detect is not None:
            self.axMap.patches.remove(self.rect_detect)
        x1, x2, y1, y2 = self.lineDetector.detection_zone
        self.rect_detect = pyplot.Rectangle((x1,y1) ,x2-x1 , y2-y1 , edgecolor = 'm' , fill = False , linewidth = 3)
        self.axMap.add_patch(self.rect_detect)
        
        if self.span is not None:
            self.axSig.patches.remove( self.span ) 
        self.span = self.axSig.axvspan(x1,x2, color = 'm', alpha = .15)
        
        

    def plotReferenceZone(self):
        """ Plot a white box around the reference zone. """
        if self.rect_ref is not None:
            self.axMap.patches.remove(self.rect_ref)
        
        if self.lineDetector.manual_threshold:
            self.rect_ref = None
        else :
            x1, x2, y1, y2 = self.lineDetector.reference_zone
            self.rect_ref = pyplot.Rectangle((x1,y1) ,x2-x1 , y2-y1 , edgecolor = 'w' , fill = False , linewidth = 3)
            self.axMap.add_patch(self.rect_ref)
