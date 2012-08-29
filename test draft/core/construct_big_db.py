# -*- coding: utf-8 -*-

import sys
import os

#~ sys.path.append('../..')

import time

from OpenElectrophy import *
import quantities as pq

import neo

sig_size = 1e7
nb_sig = 8
nb_block = 15
nb_seg = 4



#~ url_mysql = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'
url_mysql = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_2'


url_sqlite =  'sqlite:///big_sqlite.sqlite'
if os.path.exists('big_sqlite.sqlite'):
    os.remove('big_sqlite.sqlite')


url_hybrid =  'sqlite:///big_hybrid.sqlite'
if os.path.exists('big_hybrid.sqlite'):
    os.remove('big_hybrid.sqlite')
hdf5_filename = 'big_hybrid.h5'
if os.path.exists('big_hybrid.h5'):
    os.remove('big_hybrid.h5')



def erase_all_table_mysql(url):
    engine = create_engine(url, echo=False)
    metadata = MetaData(bind = engine)
    metadata.reflect()
    metadata.drop_all()


def create_big_block(name, session):
    t1 = time.time()
    
    print name
    bl = Block(name = name)
    session.add(bl)
    
    rcg = RecordingChannelGroup(name = 'big group')
    bl.recordingchannelgroups.append(rcg)
    for a in range(nb_sig):
        rc = RecordingChannel(name = 'rec channel {}'.format(a), index = a)
        rcg.recordingchannels.append(rc)
    
    for s in range(nb_seg):
        print ' s', s
        seg = Segment(name = u'seg {} éèê'.format(s), index = s)
        bl.segments.append(seg)
        for a in range(nb_sig):
            #~ print '  a', a
            ana = AnalogSignal(signal =  np.random.rand(sig_size)*pq.mV, sampling_rate = 10*pq.kHz, t_start = -2.*pq.s,
                                name = 'signal {}'.format(a), description = 'this is a big signal', channel_index = a)
            #~ ana = AnalogSignal(signal =  np.empty(sig_size)*pq.mV, sampling_rate = 10*pq.kHz, t_start = -2.*pq.s,
                                #~ name = 'signal {}'.format(a), description = 'this is a big signal', channel_index = a)

            seg.analogsignals.append(ana)
            rcg.recordingchannels[a].analogsignals.append(ana)
            session.commit()
        
    t2 = time.time()
    print 'time for creating block', t2 - t1
    
    return bl

    
    


def construct_big_mysql():    
    #~ erase_all_table_mysql(url_mysql)

    
    mapperInfo = open_db(url_mysql, myglobals = globals(), compress = 'blosc', use_global_session = False)
    session = mapperInfo.Session()
    
    # writing
    for b in range(nb_block):
        
        mega_point_per_block =  nb_seg * nb_sig * sig_size / (1024**2)
        print 'nb point per block', mega_point_per_block, 'M'
        
        t1 = time.time()
        bl = create_big_block('block num {}'.format(b), session)
        t2 = time.time()
        print 'time for writing mysql block',(t2-t1),mega_point_per_block/(t2-t1), 'Mpts/s'
        



def construct_big_sqlite():    
    
    mapperInfo = open_db(url_sqlite, myglobals = globals(), compress = 'blosc', use_global_session = False)
    session = mapperInfo.Session()
    
    # writing
    for b in range(nb_block):
        
        mega_point_per_block =  nb_seg * nb_sig * sig_size / (1024**2)
        print 'nb point per block', mega_point_per_block, 'M'
        
        t1 = time.time()
        bl = create_big_block('block num {}'.format(b), session)
        t2 = time.time()
        print 'time for writing sqlite block',(t2-t1),mega_point_per_block/(t2-t1), 'Mpts/s'
        

def construct_big_hybrid():    
    
    mapperInfo = open_db(url_hybrid, myglobals = globals(), numpy_storage_engine = 'hdf5', hdf5_filename = hdf5_filename, compress = 'blosc')
    session = mapperInfo.Session()
    
    # writing
    for b in range(nb_block):
        
        mega_point_per_block =  nb_seg * nb_sig * sig_size / (1024**2)
        print 'nb point per block', mega_point_per_block, 'M'
        
        t1 = time.time()
        bl = create_big_block('block num {}'.format(b), session)
        t2 = time.time()
        print 'time for writing sqlite/hdf5 block',(t2-t1),mega_point_per_block/(t2-t1), 'Mpts/s'
        
    


if __name__ == '__main__':
    
    #~ construct_big_mysql()
    
    #~ construct_big_sqlite()
    
    construct_big_hybrid()
    


