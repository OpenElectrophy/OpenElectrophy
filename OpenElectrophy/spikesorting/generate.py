 


import numpy as np
import quantities as pq
import os

import neo



def generate_block_for_sorting(
                nb_segment = 5,
                nb_recordingchannel = 4,
                sampling_rate = 10.e3 * pq.Hz,
                duration = 6.*pq.s,
                
                nb_unit = 6,
                spikerate_range = [.5*pq.Hz, 12*pq.Hz],
                
                t_start = 0.*pq.s,
                noise_ratio = 0.2,
                use_memmap_path = None,
                ):



    bl = neo.Block()
    
    for s in range(nb_segment):
        bl.segments.append(neo.Segment(name = 'Segment {}'.format(s)))
    
    rcg = neo.RecordingChannelGroup(name = 'polytrode',)
    rcg.block = bl
    bl.recordingchannelgroups.append( rcg )
    for r in range(nb_recordingchannel):
        rc = neo.RecordingChannel(name = 'RC {}'.format(r), index = r)
        rcg.recordingchannels.append(rc)
        rc.recordingchannelgroups.append(rcg)
    
    # generate spiketrain 
    for u in range(nb_unit):
        unit = neo.Unit(name = 'Unit #{}'.format(u))
        rcg.units.append(unit)
        spikerate = np.random.rand()*np.diff(spikerate_range)+spikerate_range[0].magnitude
        spike_times = [ ]
        for seg in bl.segments:
            spike_times.append(np.random.rand(int((spikerate*(duration)).simplified))*duration+t_start)
        n_total = np.sum( times.size for times in spike_times )
        all_waveforms = stupid_waveform_generator(n_total, nb_recordingchannel, sampling_rate) * pq.mV
        
        n = 0
        for s,seg in enumerate(bl.segments):
            #~ print u, 's', s, spike_times[s].size
            sptr = neo.SpikeTrain(  spike_times[s], t_start = t_start, t_stop = t_start+duration)
            sptr.waveforms = all_waveforms[n:n+spike_times[s].size, :,:] 
            sptr.sampling_rate = sampling_rate
            sptr.left_sweep = (sptr.waveforms.shape[2]/sampling_rate).rescale('ms')/2.
            seg.spiketrains.append(sptr)
            unit.spiketrains.append(sptr)
            n += spike_times[s].size

    # generate signal = noise + spike waveform
    for i, seg in enumerate(bl.segments):
        for j,rc in enumerate(rcg.recordingchannels):
            sig_size = int((duration*sampling_rate).simplified)
            
            if use_memmap_path:
                filename = os.path.join(use_memmap_path, 'signal {} {}'.format(i ,j))
                signal = np.memmap(filename, dtype = float, mode = 'w+', offset = 0,
                                        shape = sig_size, )
                signal[:] = noise_ratio*np.random.randn(sig_size)
            else:
                signal = noise_ratio*np.random.randn(sig_size)
            
            #~ anasig = neo.AnalogSignal(signal = signal, units = 'mV', sampling_rate = sampling_rate, t_start = t_start, channel_index = j)
            
            for sptr in seg.spiketrains:
                for k,time in enumerate(sptr):
                    wf = sptr.waveforms[k,j,:]
                    pos = int(((time-t_start)*sampling_rate).simplified)
                    if pos+wf.size<signal.size:
                        signal[pos:pos+wf.size] += wf
            anasig = neo.AnalogSignal(signal = signal, units = 'mV', sampling_rate = sampling_rate, t_start = t_start, channel_index = j)
            seg.analogsignals.append(anasig)
            rc.analogsignals.append(anasig)
    
    try:
        neo.io.tools.create_many_to_one_relationship(bl)
    except:
        bl.create_many_to_one_relationship()
        
    return bl
    
    
    


def stupid_waveform_generator(n, trodness, sampling_rate):
    parameter_range = dict(
                                amp1 = [1.5, 3.5],
                                mu1 = [ 0.9e-3, 1.1e-3],
                                sigma1 = [3e-4, 4e-4],
                                
                                mu2 = [ 1.3e-3, 1.9e-3],
                                sigma2 = [5.5e-4, 6e-4],
                                amp2 = [-6., -1.],
                                )
    
    t = np.arange(0,4.e-3,(1./sampling_rate).rescale(pq.s).magnitude )
    
    def random_param_in_range():
        np.random.seed()
        centers = { }
        for p, r in parameter_range.items():
            val = np.random.rand()*np.diff(r)+r[0]
            centers[p] = val
        return centers
    
    waveforms = np.empty((n,trodness, t.size))
    for i in range(trodness):
        initial_params = random_param_in_range()
        for j in range(n):
            params = { }
            for p, r in parameter_range.items():
                params[p] = initial_params[p] + np.diff(r)*.02 * np.random.randn()
            waveforms[j,i,:] = params['amp1']*np.exp(-(t-params['mu1'])**2/params['sigma1']**2) + params['amp2']* np.exp(-(t-params['mu2'])**2/params['sigma2']**2)
    
    return waveforms #* pq.V



def test1():
    
    from matplotlib import pyplot


    trodness = 4

    fig = pyplot.figure()
    axs = [ ]
    for i in range(trodness):
        ax = fig.add_subplot(trodness,1,1+i)
        axs.append(ax)
    

    n = 100
    colors = 'rybkcm'
    sampling_rate = 10*pq.kHz
    
    t = np.arange(0,4.e-3,(1./sampling_rate).rescale(pq.s).magnitude )
    
    for c in range(5):
        wavefoms = stupid_waveform_generator(n, trodness, sampling_rate)
    
        for i in range(trodness):
            for j in range(n):
                axs[i].plot(t, wavefoms[j,i,:], color = colors[c%len(colors)])


    pyplot.show()


def test2():
    bl = generate_block_for_sorting()
    print bl.recordingchannelgroups
    

if __name__ == '__main__':
    #~ test1()
    test2()



    