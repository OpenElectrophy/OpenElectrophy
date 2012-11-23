#encoding : utf-8 

"""
This modules provide context menu classes for qtsqltreview.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .editdb import EditFieldsDialog, ChangeParentDialog, EditRecordingChannelGroupsDialog


#TODO : fix delete on close for QWidget.show() here.


class MenuItem(object):
    name = ''
    table = None # None  for alltable
    mode = 'all' # or all unique homogeneous empty
    icon = ''
    def execute(self, **kargs):
        print 'Not implemented', self.name
        print kargs


class Delete(MenuItem):
    name = 'Delete'
    table = None
    mode = 'homogeneous'
    icon = ':/user-trash.png'
    def execute(self, session, treeview, explorer,ids, tablename,  treedescription, **kargs):
        for warn in  [  'Do you want to delete this and all of its descendants?',
                                'Are you sure?',
                                'Are you really sure?',
                                ]:
            mb = QMessageBox.warning(treeview, u'delete',warn, 
                    QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)
            if mb == QMessageBox.Cancel : return
        
        for id  in ids :
            class_ = treedescription.tablename_to_class[tablename]
            # this do not work in cascade because it is directly SQL
            #~ session.query(OEclass).filter_by(id=id).delete()
            # this works but slow
            instance = session.query(class_).get(id)
            session.delete(instance)
        session.commit()
        explorer.refresh()
    
class Edit(MenuItem):
    name = 'Edit'
    table = None
    mode = 'unique'
    icon = ':/view-form.png'
    def execute(self, session,treeview, id, tablename,treedescription, explorer,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        instance = session.query(class_).get(id)
        w= EditFieldsDialog(parent = treeview, session = session, instance = instance)
        if w.exec_():
            explorer.refresh()


class ChangeParent(MenuItem):
    name = 'Change parent'
    table = None
    mode = 'homogeneous'
    icon = ':/view-process-all-tree.png'
    def execute(self, session,explorer, ids, treeview, treedescription,tablename, **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        w= ChangeParentDialog(parent = treeview, session = session, ids = ids, 
                            class_ = class_, mapped_classes = treedescription.dbinfo.mapped_classes )
        if w.exec_():
            explorer.refresh()


class CreateTop(MenuItem):
    name = 'Create top hierachical element'
    table = None
    mode = 'empty'
    icon = ':/list-add.png'
    def execute(self, session, explorer, treedescription, **kargs):
        instance = treedescription.topClass()
        session.add(instance)
        session.commit()
        explorer.refresh()
    



class SaveToFile(MenuItem):
    name = 'Save Block(s) to file'
    table = 'Block'
    mode = 'homogeneous'
    icon = ':/document-save.png'

# Open Viewers
from .viewers import SegmentViewer, SignalViewer, TimeFreqViewer

class DrawSegment(MenuItem):
    name = 'View Segment'
    table = 'Segment'
    mode = 'unique'
    icon = ':/draw-segment.png'
    def execute(self, session,treeview, id, tablename,treedescription, explorer,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        neo_seg = session.query(class_).get(id).to_neo(cascade = True)
        print len(neo_seg.analogsignals)
        w= SegmentViewer(segment = neo_seg, parent = treeview)
        w.setWindowFlags(Qt.Window)
        w.show()

class DrawAnalogSignal(MenuItem):
    name = 'View AnalogSignals'
    table = 'AnalogSignal'
    mode = 'homogeneous'
    icon = ':/draw-analogsignals.png'
    def execute(self, session,treeview, ids, treedescription,tablename,    **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        analogsignals = [ ]
        for id in ids:
            neo_anasig = session.query(class_).get(id).to_neo(cascade = True)
            analogsignals.append(neo_anasig)
        w= SignalViewer(analogsignals = analogsignals, parent = treeview, with_time_seeker = True)
        w.setWindowFlags(Qt.Window)
        w.show()

class DrawTimeFreqViewer(MenuItem):
    name = 'View Time Frequency'
    table = 'AnalogSignal'
    mode = 'homogeneous'
    icon = ':/draw-timefreq.png'
    def execute(self, session,treeview, ids, treedescription,tablename,    **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        analogsignals = [ ]
        for id in ids:
            neo_anasig = session.query(class_).get(id).to_neo(cascade = True)
            analogsignals.append(neo_anasig)
        w= TimeFreqViewer(analogsignals = analogsignals, parent = treeview, with_time_seeker = True)
        w.setWindowFlags(Qt.Window)
        w.show()







class EditRecordingChannelGroups(MenuItem):
    name = 'Edit RecordingChannelGroups'
    table = 'Block'
    mode = 'unique'
    icon = ':/recordingchannelgroup.png'
    def execute(self, session,treeview, id, tablename,treedescription, explorer,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        instance = session.query(class_).get(id)
        w= EditRecordingChannelGroupsDialog(parent = treeview, Session = treedescription.dbinfo.Session,
                block = instance, mapped_classes = treedescription.dbinfo.mapped_classes)
        if w.exec_():
            explorer.refresh()



from .oscillationdetection import OscillationDetection


class EditOscillation(MenuItem):
    name = 'Edit Oscillations'
    table = 'AnalogSignal'
    mode = 'unique'
    icon = ':/oscillation.png'
    def execute(self, session,explorer,tablename,  id, treedescription,settings,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        ana = session.query(class_).get(id)
        
        w = OscillationDetection(analogsignal = ana, settings =settings, session = session, mapped_classes = treedescription.dbinfo.mapped_classes)
        w.db_changed.connect(explorer.refresh)
        w.setParent(explorer)
        w.setWindowFlags(Qt.Window)
        w.show()


from .spikesorting import SpikeSortingWindow
from ..spikesorting import SpikeSorter

class SpikeSorting(MenuItem):
    name = 'Spike sorting'
    table = 'RecordingChannelGroup'
    mode = 'unique'
    icon = ':/spike.png'
    def execute(self, session,explorer,tablename,  id, treedescription,settings,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        rcg = session.query(class_).get(id)
        
        # FIXME: this load every in a block because of cascade = True
        # do a hack for loading only the rcg
        neo_rcg = rcg.to_neo(cascade = True)
        
        spikesorter = SpikeSorter(neo_rcg)
        w= SpikeSortingWindow(spikesorter = spikesorter, session = session, dbinfo = treedescription.dbinfo, settings =settings)
        w.db_changed.connect(explorer.refresh)
        w.setParent(explorer)
        w.setWindowFlags(Qt.Window)
        w.show()

class DetectRespiratoryCycle(MenuItem):
    name = 'Detect respiratory cycles'
    table = 'RespirationSignal'
    mode = 'unique'
    icon = ':/repiration.png'
    
    
    



context_menu = [ Delete, Edit, ChangeParent,CreateTop, 
                DrawSegment, DrawAnalogSignal, DrawTimeFreqViewer, 
                EditRecordingChannelGroups, SaveToFile,
                EditOscillation, 
                SpikeSorting,
                DetectRespiratoryCycle,
                ]
