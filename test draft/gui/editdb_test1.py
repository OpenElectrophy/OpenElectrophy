import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui import *
from OpenElectrophy.gui.editdb import *
from OpenElectrophy.gui.guiutil import *



import quantities as pq
import numpy as np


url = 'sqlite:///test_db_1.sqlite'






def test1():
    """
    EditFields
    """
    dbinfo = open_db(url, myglobals = globals(),
                                        use_global_session = False, 
                                        object_number_in_cache = 3000,
                                        relationship_lazy = 'dynamic', 
                                        )
    session = dbinfo.Session()
    bl = OEBase.from_neo(TryItIO().read(duration = 3, nb_segment = 2),
                                            mapped_classes = dbinfo.mapped_classes, cascade = True)
    bl.save(session= session)
    

    app = QApplication([ ])
    
    #~ settings = PickleSettings(applicationname = 'testOE3')
    
    bl = session.query(Block).first()
    print bl.name
    print bl
    
    w = EditFieldsDialog( session = session,
                            instance = bl,
                            )
    #~ ok = w.show()
    w.exec_()
    #~ app.exec_()
    print bl


def test2():
    """
    ChangeParent
    """
    dbinfo = open_db(url, myglobals = globals(),
                                use_global_session = False, 
                                object_number_in_cache = 3000,
                                relationship_lazy = 'dynamic', 
                                )
    
    session = dbinfo.Session()

    app = QApplication([ ])
    
    inst = session.query(AnalogSignal).first()
    w = ChangeParentDialog( session = session,
                            ids =[ ],
                            class_ = AnalogSignal,
                            mapped_classes = dbinfo.mapped_classes,
                            )
    w.exec_()

def test3():
    """
    EditRecordingChannelGroupsDialog
    """
    dbinfo = open_db(url, myglobals = globals(),
                            use_global_session = False, 
                            object_number_in_cache = 3000,
                            #~ relationship_lazy = 'dynamic', 
                            )
    
    session = dbinfo.Session()

    app = QApplication([ ])
    
    bl = session.query(Block).first()
    #~ bl.recordingchannelgroups.append(RecordingChannelGroup(name = 'new'))
    #~ session.commit()
    print 'before', bl.id
    for rcg in bl.recordingchannelgroups:
        print '-'*10
        print rcg
        for rc in rcg.recordingchannels:
            print '   ' , rc.index
        print
    w = EditRecordingChannelGroupsDialog( Session = dbinfo.Session, block = bl,
                            mapped_classes = dbinfo.mapped_classes)
    if w.exec_():
        pass
        
    
    session = dbinfo.Session()
    bl = session.query(Block).first()
    print 'after', bl.id
    for rcg in bl.recordingchannelgroups:
        print '-'*10
        print rcg
        for rc in rcg.recordingchannels:
            print '   ' , rc.index
        print
        


if __name__ == '__main__' :
    #~ test1()
    #~ test2()
    test3()



