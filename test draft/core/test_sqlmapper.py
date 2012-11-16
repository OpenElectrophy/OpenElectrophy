import sys
import os

sys.path.append('../..')

from OpenElectrophy import *
import quantities as pq

url = 'sqlite://'

#~ url = 'sqlite:///test_db_1.sqlite'
#~ if os.path.exists('test_db_1.sqlite'):
    #~ os.remove('test_db_1.sqlite')


#~ url = 'mysql://test_dev:test_dev@localhost/test_dev_1'
#~ url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'


#~ url = 'sqlite:///test_db_with_hdf5.sqlite'
#~ hdf5_filename = 'test_db_with_hdf5.h5'
#~ if os.path.exists('test_db_with_hdf5.sqlite'):
    #~ os.remove('test_db_with_hdf5.sqlite')
#~ if os.path.exists('test_db_with_hdf5.h5'):
    #~ os.remove('test_db_with_hdf5.h5')




#~ if True:
    #~ engine = create_engine(url, echo=False)
    #~ metadata = MetaData(bind = engine)
    #~ metadata.reflect()
    #~ metadata.drop_all()



mapperInfo = open_db(url, myglobals = globals(), )

#~ mapperInfo = open_db(url, myglobals = globals(), numpy_storage_engine = 'hdf5', hdf5_filename = hdf5_filename)





seg = Segment(name = 'first seg')

for i in range(3):
    ana = AnalogSignal( )
    ana.name = 'from attr {}'.format(i)
    ana.signal = pq.Quantity( [1.,2.,3.], units = 'mV')
    ana.t_start = 50.23 * pq.s
    seg.analogsignals.append(ana)
    print ana.segment


for i in range(1):
    ana = AnalogSignal(   signal = pq.Quantity( [1.,2.,3.], units = 'mV'),
                                        t_start = 15.654654 * pq.s,
                                        sampling_rate = 10*pq.Hz,
                                        name = 'ini init {}'.format(i),
                                        
                                        )
    ana.signal[1] = 4*pq.mV
    seg.analogsignals.append(ana)
    
for i in range(2):
    ev = EventArray(times = [1., 2.5, 5.5]*pq.s)
    ev.labels = np.array(['aa', 'bbb', 'cccc' ])
    seg.eventarrays.append(ev)

seg.save()
id_seg = seg.id


rcg1 = RecordingChannelGroup(name = 'RCG1')
rcg2 = RecordingChannelGroup(name = 'RCG2')
for i in range(4):
    rc = RecordingChannel(name = 'RC {}'.format(i), index = i)
    rcg1.recordingchannels.append(rc)
    if i<2:
        rcg2.recordingchannels.append(rc)


rcg1.save()
rcg2.save()
id_rcg = rcg1.id

# loading
seg = Segment.load(id_seg)
print seg
#or
seg = Segment(id = id_seg)


print seg
for ana in seg.analogsignals:
    print ana
for ev in seg.eventarrays:
    print ev


print id_rcg
rcg = RecordingChannelGroup.load(id_rcg)


print rcg

for rc in rcg.recordingchannels:
    print rc
    print rc.recordingchannelgroups


ids, = sql("SELECT Segment.id from Segment")
print ids
print type(ids)


ids, = sql("SELECT EpochArray.id from EpochArray")
print ids
print type(ids)


