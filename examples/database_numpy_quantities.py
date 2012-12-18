# -*- coding: utf-8 -*-
"""
Numpy in SQL 
----------------------

Numpy is a python module for manipulating ndarray (vector, matrices, volume ...)

Quantities = numpy + units handling.

There are no official way to store an array in SQL contrary to str, datetime, int, float, ...

OpenElectrophy provides a simple 2 ways to save a numpy (or quantities) attributes in SQL:
    1 Everything in database (standard attrs + numpy):
       * There a big table *NumpyArrayTable* containing numpy
       * Each table that have numpy are link with the specific row
       * The main idea is to compress the buffer (memory) part of the array and store it in a big BLOB
       * You can activate compression (faster in some case)
       * This table have this columns:
           * id  =Int
           * dtype = String
           * shape = String
           * compres = String
           * units = String (only for quantities)
           * blob = LargeBinary (LONGBLOB)
    
    2 Standard attributes in database + hdf5 pytables for numpy array:
        * *NumpyArrayTable* is empty
        * a hdf5 file come with the database
        * each numpy attributes are saved in a tables.EArray at path discribe by tablename+attribute name+id

    
For instance the following classes have a numpy or qiuantities attributes:
 * AnalogSignal.signal
 * SpikeTrains.waveforms and SpikeTrains.times
 * Oscillation.time_line, Oscillation.freq_line, Oscillation.value_line
 * EpochArray.times, EpochArray.durations, EpochArray.labels, 

With the SQL mapper you can directly and transparently use them in your scripts.

"""

import sys
sys.path.append('..')

if __name__== '__main__':

    import numpy as np
    import quantities as pq
    
    from OpenElectrophy import open_db
    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)
    
    # create a random AnalogSignal with 5. s at 1kHz
    ana = AnalogSignal()
    ana.signal = np.random.rand(5000) * pq.mV
    ana.sampling_rate = 1000. *pq.Hz
    ana.t_start = 0. * pq.s

    # ana.signal is a <quantities.quantity.Quantity>
    print type(ana.signal)
    
    # so you can play with it
    ana.signal[30:400] = .04 * pq.V
    ana.signal[ ana.signal>.8 * pq.mV ] *= 2.

    # and save in db
    ana.save()

