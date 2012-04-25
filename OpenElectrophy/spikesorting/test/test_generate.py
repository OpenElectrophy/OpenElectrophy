# -*- coding: utf-8 -*- 
from __future__ import division

import unittest

import numpy as np
import quantities as pq
import neo

from OpenElectrophy.spikesorting import generate_block_for_sorting


class BasicTest(unittest.TestCase):
    def test_runtest(self):
        bl = generate_block_for_sorting(
                nb_segment = 5,
                nb_recordingchannel = 4,
                sampling_rate = 10.e3 * pq.Hz,
                duration = 0.5*pq.s,
                
                nb_unit = 6,
                spikerate_range = [.5*pq.Hz, 12*pq.Hz],
                
                t_start = 0.*pq.s,
                noise_ratio = 0.2,
                use_memmap_path = None,
                )
        print bl
        self.assertIsInstance(bl, neo.Block)
        self.assertEqual(len(bl.segments), 5)
        self.assertEqual(len(bl.recordingchannelgroups), 1)
        self.assertEqual(len(bl.recordingchannelgroups[0].recordingchannels), 4)
        


if __name__ == '__main__':
    unittest.main(verbosity=2)


