
import numpy as np
import quantities as pq
import neo

nb_sig = 3
nb_epocharrays = 4
nb_eventarrays = 4
nb_spiketrains = 25
#~ sig_size = 3.6e8
#~ sig_size = 1e7
sig_size = 1e5
nb_spike =  10e3
#~ nb_spike =  0
#~ fs = 10.e3
fs = 5000
t = np.arange(sig_size)/fs
t_start = -5.
epoch_size = 100
event_size = 2000
dur = sig_size/fs

analogsignals = [ ]
spiketrains_on_signals = [ ]
spiketrains = [ ]
for i in range(nb_sig):
    sig = 7*np.sin(t*np.pi*2*25.) + np.random.randn(sig_size)*6
    spikepos = np.random.randint(sig.size, size =nb_spike)
    
    sig[spikepos] += 45
    sig *= 1+i/10.
    color = 'w' if i<2 else None
    analogsignals.append(neo.AnalogSignal(sig, units = 'uV', t_start=t_start*pq.s, sampling_rate = fs*pq.Hz, channel_index = i, color = color))
    spiketrains_on_signals.append([ ])
    for i in range(2):
        color = ['m', 'g', 'b', 'r'][i%4]
        sptr = neo.SpikeTrain(spikepos[i*nb_spike/2:(i+1)*nb_spike/2]/float(fs)+t_start,
                    t_start = t_start, t_stop = t_start+sig_size/fs, units = 's', color = color)
        spiketrains_on_signals[-1].append(sptr)
        spiketrains.append(sptr)

epocharrays = [ ]
for i in range(nb_epocharrays):
    durations = np.random.rand(epoch_size)*(dur/epoch_size/2)
    interv = np.random.rand(epoch_size)*(dur/epoch_size/2)+dur/epoch_size/4
    times = np.cumsum(durations)+np.cumsum(interv)
    color = 'r' if i<2 else 'w'
    ea = neo.EpochArray(times = times*pq.s,
                                        durations = durations*pq.s,
                                        name = 'epoch {}'.format(i),
                                        color = color)
    epocharrays.append(ea)
ea = neo.EpochArray(times = [1., 2., 3.]*pq.s,
                                        durations = [.5,.3,.6]*pq.s,
                                        name = 'yep')
epocharrays.append(ea)

eventarrays = [ ]

for i in range(nb_eventarrays):
    times = np.random.rand(event_size)*dur
    times = np.sort(times)
    color = ['r', 'g', 'b', 'm'][i%4]
    ev = neo.EventArray(times = times*pq.s,
                                        name = 'event {}'.format(i),
                                        color = color)
    eventarrays.append(ev)


    


seg = neo.Segment(name = 'test')

seg.analogsignals = analogsignals
seg.epocharrays = epocharrays
seg.spiketrains = spiketrains
seg.eventarrays = eventarrays

