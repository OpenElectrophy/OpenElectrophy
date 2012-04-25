# -*- coding: utf-8 -*- 
from __future__ import division

import unittest

import numpy as np
import quantities as pq
import neo

from OpenElectrophy.spikesorting import (SpikeSorter, generate_block_for_sorting,\
             ButterworthFilter  )
  


class BasicTest(unittest.TestCase):
    def setUp(self):
        bl = generate_block_for_sorting(nb_unit = 3, duration = 1.*pq.s,
                                                    noise_ratio = 0.2, nb_segment = 2,)
        rcg = bl.recordingchannelgroups[0]
        self.sps = SpikeSorter(rcg, initial_state='full_band_signal')
        
    def tearDown(self):
        pass
    
        
    def test_getattr_aliases(self):
        self.assertIs(self.sps.segs, self.sps.segments)
        self.assertRaises(AttributeError, getattr, self.sps, 'i_love_my_mother')
    
    def test_getattr_runstep(self):
        self.sps.ButterworthFilter( f_low = 200.)
        self.assertIsInstance(self.sps.history[-1]['methodInstance'], ButterworthFilter)
    
    def test_one_standart_pipeline(self):
        self.sps.ButterworthFilter( f_low = 200.)
        self.assertIsNotNone(self.sps.filtered_sigs)

        self.sps.MedianThresholdDetection(sign= '-', median_thresh = 6,)
        self.assertIsNotNone(self.sps.spike_index_array)

        self.sps.AlignWaveformOnDetection(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms)
        self.assertIsNotNone(self.sps.seg_spike_slices)
        self.assertIsNotNone(self.sps.spike_waveforms)
        self.assertIsNotNone(self.sps.left_sweep)
        self.assertIsNotNone(self.sps.right_sweep)
        
        self.sps.PcaFeature(n_components = 3)
        self.assertIsNotNone(self.sps.waveform_features)

        self.sps.SklearnGaussianMixtureEm(n_cluster = 12, n_iter = 500 )
        self.assertIsNotNone(self.sps.spike_clusters)
        self.assertIsNotNone(self.sps.cluster_names)
    
    def test_apply_history_to_other(self):
        sps2 = SpikeSorter(self.sps.rcg, initial_state='full_band_signal')
        self.sps.apply_history_to_other(sps2)
        
    


class TestConstructor(unittest.TestCase):
    pass
    
    
    

if __name__ == '__main__':
    unittest.main()
