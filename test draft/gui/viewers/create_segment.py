
import numpy as np
import quantities as pq
import neo

nb_sig = 8

#~ sig_size = 3.6e8
#~ sig_size = 1e7
sig_size = 1e6
nb_spike =  10e3
#~ nb_spike =  0
fs = 10.e3
t = np.arange(sig_size)/fs
t_start = -5.

analogsignals = [ ]
spiketrains_on_signals = [ ]
for i in range(nb_sig):
    sig = 7*np.sin(t*np.pi*2*25.) + np.random.randn(sig_size)*6
    spikepos = np.random.randint(sig.size, size =nb_spike)
    sig[spikepos] += 15
    analogsignals.append(neo.AnalogSignal(sig, units = 'uV', t_start=t_start*pq.s, sampling_rate = fs*pq.Hz, channel_index = i, color = 'w'))
    spiketrains_on_signals.append([ ])
    for i in range(2):
        color = ['magenta', 'green', 'blue', 'red'][i%4]
        spiketrains_on_signals[-1].append(neo.SpikeTrain(spikepos[i*nb_spike/2:(i+1)*nb_spike/2]/fs+t_start,
                    t_start = t_start, t_stop = t_start+sig_size/fs, units = 's', color = color))



seg = neo.Segment(name = 'test')

seg.analogsignals = analogsignals
#~ seg.spiketrains = 