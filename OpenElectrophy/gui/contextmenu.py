#encoding : utf-8 

"""
This modules provide context menu classes for qtsqltreview.
"""

from .qt import *


from .editdb import EditFieldsDialog, ChangeParentDialog, EditRecordingChannelGroupsDialog

import numpy as np

import neo

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
    
    
from importdata import ImportData
class MenuImportData(MenuItem):
    name = 'Import data in this db'
    table = None
    mode = 'empty'
    icon = ':/svn-update.png'
    def execute(self, session, explorer, treedescription, **kargs):
        w = ImportData(dbinfo = treedescription.dbinfo)
        w.setWindowTitle('Import new data in database')
        if w.exec_():
            explorer.refresh()



class SaveToFile(MenuItem):
    name = 'Save Block(s) to file'
    table = 'Block'
    mode = 'unique'
    icon = ':/document-save.png'
    def execute(self, session,treeview, id, tablename,treedescription, explorer,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        bl = session.query(class_).get(id)
        
        filters = u''
        ext_to_io = { }
        for io in neo.io.iolist:
            if neo.Block in  io.writeable_objects and len(io.extensions)>0:
                filters += u'{} (*.{});;'.format(io.name, io.extensions[0])
                ext_to_io[io.extensions[0]] = io
        
        filename = QFileDialog.getSaveFileName(treeview,u'Save File',
                            bl.name or u'',filters)
        if filename != '':
            filename = unicode(filename)
            for ext, io in ext_to_io.items():
                if filename.endswith('.{}'.format(ext)):
                    io(filename = filename).write(bl.to_neo(cascade = True))
                    return


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


# some hack for python list when contain numpy.array
def list_contains(l, e):
    # should be
    # return s in l
    return np.any([ e is e2 for e2 in l ])


def create_neo_rcg_for_sorting(rcg):
    # FIXED: this use to load load every in a block because of cascade = True
    #~ neo_rcg = rcg.to_neo(cascade = True)#, propagate_many_to_many = True)
    #~ return neo_rcg
    
    neo_rcg = rcg.to_neo(cascade = True, with_many_to_many = True,
            with_one_to_many = True, with_many_to_one = False,
            propagate_many_to_many = False)
    neo_rcg.block = rcg.block.to_neo(cascade = False)
    for seg in rcg.block.segments:
        neo_seg = seg.to_neo(cascade=False)
        if neo_seg not in neo_rcg.block.segments:
            neo_rcg.block.segments.append(neo_seg)
            for anasig in seg.analogsignals:
                if anasig.recordingchannel in rcg.recordingchannels:
                    neo_sig = anasig.to_neo(cascade = False)
                    #~ if neo_sig not in neo_seg.analogsignals:
                    if not list_contains(neo_seg.analogsignals, neo_sig):
                        neo_seg.analogsignals.append(neo_sig)
                        neo_sig.segment = neo_seg
            for spiketrain in seg.spiketrains:
                neo_spiketrain = spiketrain.to_neo(cascade=False)
                neo_spiketrain.unit = spiketrain.unit.to_neo(cascade=False)
                neo_seg.spiketrains.append(neo_spiketrain)
    return neo_rcg
    
    
class SpikeSortingOnRCG(MenuItem):
    name = 'Spike sorting'
    table = 'RecordingChannelGroup'
    mode = 'unique'
    icon = ':/spike.png'
    def execute(self, session,explorer,tablename,  id, treedescription,settings,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        rcg = session.query(class_).get(id)
        neo_rcg = create_neo_rcg_for_sorting(rcg)
        
        spikesorter = SpikeSorter(neo_rcg)
        w= SpikeSortingWindow(spikesorter = spikesorter, session = session, dbinfo = treedescription.dbinfo, settings =settings)
        w.db_changed.connect(explorer.refresh)
        w.setParent(explorer)
        w.setWindowFlags(Qt.Window)
        w.show()

class SpikeSortingOnRCs(MenuItem):
    name = 'Create Group and do spike sorting'
    table = 'RecordingChannel'
    mode = 'homogeneous'
    icon = ':/spike.png'
    def execute(self, session,explorer,tablename,  ids, treedescription,settings,  **kargs):
        RC = treedescription.tablename_to_class['RecordingChannel']
        RCG = treedescription.tablename_to_class['RecordingChannelGroup']
        Block = treedescription.tablename_to_class['Block']
        rcs = [ session.query(RC).get(id) for id in ids ]
        block_ids = np.unique([ rc.recordingchannelgroups[0].block_id for rc in rcs])
        if len(block_ids) !=1:
            # Not in the same Block
            return
        name = ''
        for rc in rcs:
            name += ' {}'.format(rc.index)
        rcg = RCG(name = name)
        session.add(rcg)
        for rc in rcs:
            rcg.recordingchannels.append(rc)
        bl = session.query(Block).get(int(block_ids[0]))
        bl.recordingchannelgroups.append(rcg)
        session.commit()
        explorer.refresh()
        
        neo_rcg = create_neo_rcg_for_sorting(rcg)
        
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



    
from ..core.tools import merge_blocks
class MergeBlock(MenuItem):
    name = 'Merge Blocks (unify RecordingChannel and recordingChannelGroup)'
    table = 'Block'
    mode = 'homogeneous'
    icon = ':/merge.png'
    def execute(self, session,explorer,tablename,  ids, treedescription,settings,  **kargs):
        
        class_ = treedescription.tablename_to_class[tablename]
        block_list = [ ]
        for id in ids:
            block_list.append(session.query(class_).get(id))
        print block_list
        new_bl = merge_blocks(block_list, session = session, dbinfo = treedescription.dbinfo)
        explorer.refresh()



context_menu = [ Delete, Edit, ChangeParent,MenuImportData, CreateTop, 
                DrawSegment, DrawAnalogSignal, DrawTimeFreqViewer, 
                EditRecordingChannelGroups, SaveToFile,
                EditOscillation, 
                SpikeSortingOnRCG, SpikeSortingOnRCs, 
                DetectRespiratoryCycle,
                MergeBlock,
                ]
