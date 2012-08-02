import sys
import os

#~ sys.path.append('../..')

import time

from OpenElectrophy import *
import quantities as pq

import neo

sig_size = 1e8
nb_sig = 4
nb_block = 1
nb_seg = 3

mega_point = nb_block * nb_seg * sig_size / (1024**2)


url_mysql = 'mysql://test_dev:test_dev@localhost/test_dev_1'
#~ url_mysql = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'

url_sqlite = 'sqlite:///test_db_1.sqlite'



def erase_all_table_mysql(url):
    engine = create_engine(url, echo=False)
    metadata = MetaData(bind = engine)
    metadata.reflect()
    metadata.drop_all()

def erase_all_hdf5():
    for b in range(nb_block):
        filename = 'test {}.h5'.format(b)
        if os.path.exists(filename):
            os.remove(filename)

def erase_sqlite():
    url = 'sqlite:///test_db_1.sqlite'
    filename = url_sqlite.replace('sqlite:///','')
    print filename
    if os.path.exists(filename):
        os.remove(filename)




def create_big_neo_block(name='a block'):
    t1 = time.time()
    
    print 'b', b
    bl = neo.Block(name = name)
    
    rcg = neo.RecordingChannelGroup(name = 'big group')
    bl.recordingchannelgroups.append(rcg)
    for a in range(nb_sig):
        rc = neo.RecordingChannel(name = 'rec channel {}'.format(a), index = a)
        rcg.recordingchannels.append(rc)
    
    for s in range(nb_seg):
        print ' s', s
        seg = neo.Segment(name = 'seg {}'.format(s))
        bl.segments.append(seg)
        for a in range(nb_sig):
            #~ print '  a', a
            ana = neo.AnalogSignal(signal = np.empty(sig_size)*pq.mV, sampling_rate = 10*pq.kHz, t_start = -2.*pq.s,
                                name = 'signal {}'.format(a), description = 'this is a big signal')
            #~ ana = AnalogSignal(signal = np.random.rand(sig_size)*pq.mV, sampling_rate = 10*pq.kHz, t_start = -2.*pq.s)
            seg.analogsignals.append(ana)
            rcg.recordingchannels[a].analogsignals.append(ana)
        
    t2 = time.time()
    print 'time for creating neo block', t2 - t1
    
    return bl

    
    


if __name__ == '__main__':
    
    erase_all_table_mysql(url_mysql)
    erase_all_hdf5()
    erase_sqlite()

    print 'nb point ', mega_point, 'M'
    
    # writing
    for b in range(nb_block):
        bl = create_big_neo_block(name='block num {}'.format(b))
        
        
        # neo Hdf5
        w = neo.io.NeoHdf5IO(filename = 'test {}.h5'.format(b))
        t1 = time.time()
        w.write_block(bl)
        w.close()
        t2 = time.time()
        print 'time  for writing hdf5 block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'
        
        
        # OE MySQL
        mapperInfo = open_db(url_mysql, myglobals = globals(), compress = True)
        t1 = time.time()
        oebl = Block.from_neo(bl,mapperInfo.mapped_classes, cascade =True)
        oebl.save()
        t2 = time.time()
        print 'time for writing mysql block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'
        
        #~ bl = create_big_neo_block(name='block num {}'.format(b))
        # OE sqlite
        mapperInfo = open_db(url_sqlite, myglobals = globals(), compress = True)
        t1 = time.time()
        oebl = Block.from_neo(bl,mapperInfo.mapped_classes, cascade =True)
        oebl.save()
        t2 = time.time()
        print 'time for writing sqlite block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'


    # reading
    for b in range(nb_block):
        # neo Hdf5
        r = neo.io.NeoHdf5IO(filename = 'test {}.h5'.format(b))
        t1 = time.time()
        bl = r.read_block()
        r.close()
        for seg in bl.segments:
            for anasig in seg.analogsignals:
                s = anasig.shape
                print anasig.name,s
        t2 = time.time()
        print 'time for reading hdf5 block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'
        
        
        # OE MySQL
        mapperInfo = open_db(url_mysql, myglobals = globals(), compress = True)
        session = mapperInfo.Session()
        t1 = time.time()
        bl = session.query(Block).filter_by(name = 'block num {}'.format(b)).one()
        for seg in bl.segments:
            for oeanasig in seg.analogsignals:
                print oeanasig.signal.shape
                anasig = oeanasig.to_neo()
                s = anasig.shape
                print anasig.name,s
        t2 = time.time()
        print 'time for reading mysql block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'


        # OE SQlite
        mapperInfo = open_db(url_sqlite, myglobals = globals(), compress = True)
        session = mapperInfo.Session()
        t1 = time.time()
        bl = session.query(Block).filter_by(name = 'block num {}'.format(b)).one()
        for seg in bl.segments:
            for oeanasig in seg.analogsignals:
                print oeanasig.signal.shape
                anasig = oeanasig.to_neo()
                s = anasig.shape
                print anasig.name,s
        t2 = time.time()
        print 'time for reading SQlite block',(t2-t1),mega_point/(t2-t1), 'Mpts/s'


    

