import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui import *
from OpenElectrophy.gui.qtsqltreeview import *


import quantities as pq
import numpy as np

import neo
from OpenElectrophy.core.base import OEBase



from sqlalchemy.sql.expression import asc, desc


def create_and_open():
    #~ url = 'sqlite://'

    #~ url = 'sqlite:///test_db_1.sqlite'
    #~ if os.path.exists('test_db_1.sqlite'):
        #~ os.remove('test_db_1.sqlite')
    
    
    #~ url =  'sqlite:///big_sqlite.sqlite'

    #~ url = 'mysql://OE3_dev:OE3_dev@localhost/test_dev_1'
    #~ url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_2'


    #~ if True:
    #~ if False:
        #~ engine = create_engine(url, echo=False)
        #~ metadata = MetaData(bind = engine)
        #~ Session = orm.sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
        #~ session = Session()
        #~ for table, in session.execute("Show tables"  ).fetchall():
            #~ session.execute(" DROP TABLE %s" % ( table )   )
    
    return open_db(url, myglobals = globals(),
                                                                use_global_session = False, 
                                                                object_number_in_cache = 3000,
                                                                memmap_path = './memmap1',
                                                                #~ memmap_path = None,
                                                                relationship_lazy = 'select', 
                                                                #~ relationship_lazy = 'dynamic', 
                                                                )



def fill_a_db(session, generic_classes):
    sig_size = 1e4
    
    nb_sig = 16
    nb_block = 2
    for b in range(nb_block):
        print 'b', b
        bl = Block(name = 'toto {}'.format(nb_block-b))
        session.add(bl)
        rcg = RecordingChannelGroup(name = 'big group')
        bl.recordingchannelgroups.append(rcg)
        for a in range(nb_sig):
            rc = RecordingChannel(name = 'rec channel {}'.format(a), index = a)
            rcg.recordingchannels.append(rc)
        
        for s in range(10):
            print ' s', s
            seg = Segment(name = 'seg {}'.format(s))
            bl.segments.append(seg)
            for a in range(nb_sig):
                #~ print '  a', a
                ana = AnalogSignal(signal = np.empty(sig_size)*pq.mV, sampling_rate = 10*pq.kHz, t_start = -2.*pq.s)
                seg.analogsignals.append(ana)
                rcg.recordingchannels[a].analogsignals.append(ana)
            session.commit()




def test1():
    """
    simple test
    """
    dbinfo = create_and_open()
    session = dbinfo.Session()
    #~ fill_a_db(session,dbinfo.mapped_classes)
    
    
    
    
    treedescription = TreeDescription(
                            dbinfo = dbinfo,
                            table_children = { 
                                                    'Block' : ['Segment' ],
                                                    'Segment' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = {'Block' : desc('name'),
                                                    'Segment' : 'name',
                                                    } ,
                            )
    app = QApplication([ ])
    w = QtSqlTreeView(session = session, treedescription = treedescription)
    w.show()
    sys.exit(app.exec_())
    

def test2():
    """
    simple doucle view
    """
    dbinfo = create_and_open()
    session = dbinfo.Session()
    #~ fill_a_db(session,dbinfo.mapped_classes)

    treedescription1 = TreeDescription(
                            dbinfo = dbinfo,
                            table_children = { 
                                                    'Block' : ['Segment' ],
                                                    'Segment' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = { },
                            )
    treedescription2 = TreeDescription(
                            dbinfo = dbinfo,
                            table_children = { 
                                                    'Block' : ['RecordingChannelGroup' ],
                                                    'RecordingChannelGroup' : [ 'RecordingChannel', ],
                                                    'RecordingChannel' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = { },
                            )
    
    app = QApplication([ ])
    
    w1 = QtSqlTreeView(session = session, treedescription = treedescription1)
    w2 = QtSqlTreeView(session = session, treedescription = treedescription2)
    w1.show()
    w2.show()
    sys.exit(app.exec_())



def test3():
    """
    With no db : just a file
    """
    
    url = 'sqlite://'
    
    
    dbinfo = open_db(url, 
                        object_number_in_cache = 3000,
                        #~ memmap_path = './memmap1',
                        #~ memmap_path = None,
                        )
    session = dbinfo.Session()
    
    #~ bl = neo.AxonIO(filename = 'File_axon_1.abf').read()
    #~ print bl.segments
    #~ bl2 = OEBase.from_neo(bl, generic_classes, cascade = True)
    
    from neo.test.io.generate_datasets import generate_one_simple_block
    from neo.io.tools import create_many_to_one_relationship, populate_RecordingChannel
    bl = generate_one_simple_block(supported_objects = [neo.Segment, neo.AnalogSignal, ])
    create_many_to_one_relationship(bl)
    populate_RecordingChannel(bl)
    bl2 = OEBase.from_neo(bl, dbinfo.mapped_classes, cascade = True)
    
    session.add(bl2)
    
    treedescription1 = TreeDescription(
                            mapped_classes =  dbinfo.mapped_classes,
                            table_children = { 
                                                    'Block' : ['Segment' ],
                                                    'Segment' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = None,
                            )
    treedescription2 = TreeDescription(
                            mapped_classes =  dbinfo.mapped_classes,
                            table_children = { 
                                                    'Block' : ['RecordingChannelGroup' ],
                                                    'RecordingChannelGroup' : [ 'RecordingChannel', ],
                                                    'RecordingChannel' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = None,
                            context_menu = None,
                            )
    
    app = QApplication([ ])
    
    w1 = QtSqlTreeView(session = session, treedescription = treedescription1)
    w2 = QtSqlTreeView(session = session, treedescription = treedescription2)
    w1.show()
    w2.show()
    sys.exit(app.exec_())

    

def test4():
    url = 'sqlite://'
    dbinfo = open_db(url, 
                        object_number_in_cache = 3000,
                        #~ memmap_path = './memmap1',
                        #~ memmap_path = None,
                        )
    
    import pickle
    treedescription = TreeDescription(
                            dbinfo = dbinfo,
                            table_children = { 
                                                    'Block' : ['Segment' ],
                                                    'Segment' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = { 'Block' : desc('name'),
                                                    'Segment' : asc('name'),
                                                    #~ 'Segment' : desc('name'),
                                                    } ,
                            )
    session = dbinfo.Session()
    session.query('Block')
    for k,v in treedescription.__dict__.items():
        print k, v
    treedescription2 = pickle.loads(pickle.dumps(treedescription))
    print treedescription2.name
    print treedescription2.table_order
    for k,v in treedescription2.table_order.items():
        print k, str(v)

def test5():
    """
    Context menu
    """
    dbinfo = create_and_open()
    session = dbinfo.Session()
    #fill_a_db(session,dbinfo.mapped_classes)
    
    
    from OpenElectrophy.gui.contextmenu import context_menu
    
    treedescription = TreeDescription(
                            dbinfo = dbinfo,
                            table_children = { 
                                                    'Block' : ['Segment' ],
                                                    'Segment' : [ 'AnalogSignal'],
                                                    },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = {'Block' : desc('name'),
                                                    'Segment' : asc('name'),
                                                    #~ 'segment' : desc('name'),
                                                    } ,
                            )
    app = QApplication([ ])
    w = QtSqlTreeView(session = session, treedescription = treedescription, context_menu = context_menu)
    w.show()
    sys.exit(app.exec_())



if __name__ == '__main__' :
    #~ test1()
    test2()
    #~ test3()
    #~ test4()
    #~ test5()