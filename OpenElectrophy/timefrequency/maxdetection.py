# -*- coding: utf-8 -*-
"""

"""


from numpy import vstack,diff,nonzero,c_,array,repeat,where,array,r_,sort,unique,zeros

def max_detection(map,
            threshold,
            min_dx = None,
            min_dy = None,
            ):
    """
    Find local maxima from a 2D real map 
    and clean contiguous maxima to keep only one

    ``min_dx and min_dy``
        If given, from 2 maxima with indices strictly closer than min_dx, min_dy, only the higher one is kept.
        Be careful, it works in chain and thus from 3 maxima in range from each other only the highest one is kept.
        Using min_dx = 2, min_dy = 2 simply avoid consecutive maxima.
        
    Output:
        tuple of maxima index array
    """

    if (map.shape[0]<2)or(map.shape[1]<2):
        return (array([]),array([]))
    else:
        # Center points
        time_max=(map[1:-1,:]-map[2:,:]>=0)&(map[1:-1,:]-map[:-2,:]>=0)
        freq_max=(map[:,1:-1]-map[:,2:]>=0)&(map[:,1:-1]-map[:,:-2]>=0)

        # Add edges -> current method assume no max can be detected on edge !
        #~ time_max=vstack((map[0,:]-map[1,:]>=0,time_max,map[-1,:]-map[-2,:]>=0))
        #~ freq_max=c_[map[:,0]-map[:,1]>=0,freq_max,map[:,-1]-map[:,-2]>=0]
        time_max=vstack((zeros(time_max.shape[1],dtype='bool'),time_max,zeros(time_max.shape[1],dtype='bool')))
        freq_max=c_[zeros(freq_max.shape[0],dtype='bool'),freq_max,zeros(freq_max.shape[0],dtype='bool')]

        # combine results to get local maxima
        maxima = time_max & freq_max & (map>=threshold)

        #~ # clean contiguous maxima (in time only) -> useless with min_dx=2,min_dy=1
        #~ maxima[1:,:]=maxima[1:,:].astype('int')*diff(maxima,axis=0)

        ind = list(nonzero(maxima))
        if min_dx is not None and min_dy is not None :
            INDX = abs(repeat([ind[0]],ind[0].size,0)-repeat([ind[0]],ind[0].size,0).transpose())
            INDY = abs(repeat([ind[1]],ind[1].size,0)-repeat([ind[1]],ind[1].size,0).transpose())
            to_eliminate = array([])
            N1,N2 = where( (INDX<min_dx) & (INDY<min_dy) )
            for i in range(N1.size) :
                n1,n2 = N1[i],N2[i]
                if n1==n2 : continue
                if map[ind[0][n1],ind[1][n1]] > map[ind[0][n2],ind[1][n2]] :
                    to_eliminate = r_[to_eliminate , n2]
                else :
                    to_eliminate = r_[to_eliminate , n1]
            to_eliminate = sort(unique(to_eliminate))
            for n in to_eliminate :
                ind[0] = r_[ind[0][:n] , ind[0][n+1:]]
                ind[1] = r_[ind[1][:n] , ind[1][n+1:]]
                to_eliminate -=1

        return tuple(ind)
