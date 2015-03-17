# -*- coding: utf-8 -*-
"""

"""
from numpy import intersect1d, in1d, r_, where, angle, argsort
import numpy

DEBUG = False
#~ DEBUG = True

def clean_oscillations_list(list_oscillation,
                            minimum_cycle_number= 0.,
                            eliminate_simultaneous = True,
                            regroup_full_overlap = True , 
                            eliminate_partial_overlap = True,
                            ):
    i = 0
    while i<len(list_oscillation) :
        osci1 = list_oscillation[i]
        #checking for a minimum size in cycle
        if where((angle(osci1.value_line[:-1]) <=0)&(angle(osci1.value_line[1:]) >=0))[0].size <minimum_cycle_number :
            list_oscillation.pop(i)
            if DEBUG:
                print 'too short'
            continue
        
        
        j = i+1
        while j<len(list_oscillation) :
            osci2 = list_oscillation[j]
            if intersect1d(osci1.time_line,osci2.time_line).size != 0 :
                #overlap
                # the 2 lines have same absisse for some point
                if DEBUG:
                    print 'probable overlap'
                ind_i, = where(in1d(osci1.time_line,osci2.time_line))
                ind_j, = where(in1d(osci2.time_line,osci1.time_line))
                
                if (osci1.freq_line[ind_i] == osci2.freq_line[ind_j]).all() and regroup_full_overlap :
                    # the 2 lines have same absisse and same freq for some point : we regroup them
                    ind_keep_j = where( ~in1d(osci2.time_line,osci1.time_line) )
                    osci1.time_line = r_[osci1.time_line , osci2.time_line[ind_keep_j].rescale(osci1.time_line.units)]*osci1.time_line.units
                    osci1.freq_line = r_[osci1.freq_line , osci2.freq_line[ind_keep_j].rescale(osci1.freq_line.units)]*osci1.freq_line.units
                    osci1.value_line = r_[osci1.value_line , osci2.value_line[ind_keep_j]]
                    ind_sort = argsort(osci1.time_line )
                    osci1.time_line = osci1.time_line[ind_sort]
                    osci1.freq_line = osci1.freq_line[ind_sort]
                    osci1.value_line = osci1.value_line[ind_sort]
                    del list_oscillation[j]
                    j=i+1 # to be sure to check the modified and extended oscillation with all the others
                    if DEBUG:
                        print 'full_overlap'
                    continue
                    
                if (osci1.freq_line[ind_i] != osci2.freq_line[ind_j]).all() and eliminate_simultaneous :
                    # the 2 lines have some same absisse and but not same freq for some point : we keep the higher max
                    if abs(osci1.amplitude_max)<abs(osci2.amplitude_max) :
                        list_oscillation[i] = osci2
                        osci1=osci2
                        del list_oscillation[j]
                        j=i+1 # to be sure to check the moved oscillation with all the others
                    else:
                        del list_oscillation[j]
                    if DEBUG:
                        print 'simultaneous'                    
                    continue
                
                
                if   (osci1.freq_line[ind_i] == osci2.freq_line[ind_j]).any()  and \
                        (osci1.freq_line[ind_i] != osci2.freq_line[ind_j]).any()  and \
                        eliminate_partial_overlap  :
                    # the 2 lines have some same absisse and same freq for some point  
                    # and for other point same abscise  not same freq : we keep the higher max
                    if abs(osci1.amplitude_max)<abs(osci2.amplitude_max) :
                        list_oscillation[i] = osci2
                        osci1 = osci2
                        del list_oscillation[j]
                        j=i+1 # to be sure to check the moved oscillation with all the others
                    elif abs(osci1.amplitude_max)>abs(osci2.amplitude_max) :
                        del list_oscillation[j]
                    elif abs(osci1.amplitude_max)==abs(osci2.amplitude_max):
                        # if both osc have the same max, the most powerful on the non-overlapping part is taken
                        # this is check by looking at the half biggest powers of each branc
                        non_overlapping_ind_i,=where(~(in1d(osci1.freq_line[ind_i],osci2.freq_line[ind_j])))
                        non_overlapping_ind_j,=where(~(in1d(osci2.freq_line[ind_j],osci1.freq_line[ind_i])))
                        fraction = non_overlapping_ind_i.size/2
                        non_overlapping_power_i=abs((osci1.value_line[ind_i])[non_overlapping_ind_i])
                        non_overlapping_power_j=abs((osci2.value_line[ind_j])[non_overlapping_ind_j])
                        non_overlapping_power_i.sort()
                        non_overlapping_power_j.sort()
                        if non_overlapping_power_i[fraction:].mean()<=non_overlapping_power_j[fraction:].mean():
                            list_oscillation[i] = osci2
                            osci1=osci2
                            del list_oscillation[j]
                            j=i+1 # to be sure to check the moved oscillation with all the others                            
                        else:
                            del list_oscillation[j]
                    if DEBUG:
                        print 'partial_overlap'                            
                    continue
            j+=1
        i+=1
    return list_oscillation
