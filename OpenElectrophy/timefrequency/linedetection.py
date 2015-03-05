# -*- coding: utf-8 -*-
"""

"""
from numpy import ediff1d,array,r_,digitize,arange
from ..core.oscillation import Oscillation

import quantities as pq

def detect_one_line_from_max(powermap,
            max_t,
            max_f,
            threshold,
            step = 1
            ):
    """
    Detect one ridge of powermap  above threshold starting from index (max_t,max_f)
    
    output:
    one tuple (line_t array,line_f array) (all is index based)
    """
    for direction in [-step,step]:
        half_line_f=[]
        cur_t=max_t
        cur_f=max_f
        cont = True
        while cont:
            
            # current point above threshold
            if powermap[cur_t,cur_f]<=threshold:
                break
            else:
                half_line_f.append(cur_f)
            
            # current point on time limit
            if (cur_t>=powermap.shape[0]-abs(direction))or(cur_t<abs(direction)):
                break
            
            # find next point
            cur_t+=direction
            deriv=ediff1d(powermap[cur_t,cur_f-1:cur_f+2])
            if (deriv[0]>=0.)and(deriv[1]<=0.): # is it straight ahead
                continue
            elif deriv[0]<0.:
                dir_f=-1
            elif deriv[1]>0.:
                dir_f=1
            while 1:
                cur_f+=dir_f
                # freq limit
                if (cur_f <=0)or(cur_f>=(powermap.shape[1]-1)):
                    cont = False
                    break
                # top found
                elif (powermap[cur_t,cur_f]-powermap[cur_t,cur_f+dir_f])>=0.:
                    break

        if direction<0:
            if len(half_line_f)>=2:
                line_f=array(half_line_f)[::-1]
                #~ line_t=max_t-arange(len(half_line_f)-1,-1,-1)*step
            else:
                line_f=array([max_f])
                #~ line_t=array([max_t])
        else:
            if len(half_line_f)>=2:
                line_f=r_[line_f,array(half_line_f[1:])]
                #~ line_t=r_[line_t,max_t+(1+arange(len(half_line_f)-1))*step]
                line_t=max_t+(arange(-line_f.size,0)+len(half_line_f))*step
            else:
                line_t=max_t+(arange(-line_f.size,0)+1)*step
                       
    return line_t, line_f


def detect_oscillations(map,
            t_start,
            sampling_rate,
            f_start,
            deltafreq,
            threshold,
            list_max=array([]),
            ):
    """
    Construct a list of :class:Oscillation which are detected on the map
    
    Input:
    ``map``
        complex scalogram map (its attributes t_start, sampling_rate, f_start and deltafreq must be given too)
        
    ``threshold``
        minimum power amplitude of :class:Oscillation line_val
        
    ``detection_start and detection_end``
        time limits of the detection in second
    
    Output:
    list of :class:Oscillation
    """
    list_osc = []
    if list_max.size>0:
        list_max_t=digitize(list_max.time,t_start+1.*arange(map.shape[0])/sampling_rate)-1
        list_max_f=digitize(list_max.freq,f_start+1.*arange(map.shape[1])*deltafreq)-1
        for (max_t,max_f) in zip(list_max_t,list_max_f):
            known = False
            for osc in list_osc:
                # this is really dirty...
                if (t_start+1.*max_t/sampling_rate,f_start+1.*max_f*deltafreq) in zip(osc.time_line.rescale('s').magnitude,osc.freq_line.rescale('Hz').magnitude):
                    if osc.amplitude_max>map[max_t,max_f]:
                        known = True # Max already detected on one oscillation and lower => can be skipped
                        break

            if not(known):
                line_t,line_f=detect_one_line_from_max(abs(map),max_t,max_f,threshold)
                osc=Oscillation()
                osc.time_line=(t_start+1.*line_t/sampling_rate)*pq.s
                osc.freq_line=(f_start+1.*line_f*deltafreq)*pq.Hz
                osc.value_line=map[line_t,line_f]
                #~ osc.amplitude_max=abs(map[max_t,max_f])
                #~ osc.time_max=t_start+1.*max_t/sampling_rate
                #~ osc.freq_max=f_start+1.*max_f*deltafreq
                osc.amplitude_max=float(abs(osc.value_line).max())
                ind_max=abs(osc.value_line).argmax()
                osc.time_max=float(osc.time_line[ind_max])
                osc.freq_max= float(osc.freq_line[ind_max])
                osc.time_start=float(osc.time_line[0])
                osc.freq_start=float(osc.freq_line[0])
                osc.time_stop=float(osc.time_line[-1])
                osc.freq_stop=float(osc.freq_line[-1])
                list_osc.append(osc)
    
    return list_osc

