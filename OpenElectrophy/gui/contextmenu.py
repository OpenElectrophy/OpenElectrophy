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
    def execute(self, session, treeview, explorer,ids, tablenames,  treedescription, **kargs):
        for warn in  [  'Do you want to delete this and all of its descendants?',
                                'Are you sure?',
                                'Are you really sure?',
                                ]:
            mb = QMessageBox.warning(treeview,treeview.tr('delete'),treeview.tr(warn), 
                    QMessageBox.Ok ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)
            if mb == QMessageBox.Cancel : return
        
        for id, tablename in zip(ids, tablenames) :
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
    def execute(self, session,treeview, id, tablename,treedescription,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        instance = session.query(class_).get(id)
        w= EditFieldsDialog(parent = treeview, session = session, instance = instance)
        w.exec_()


class ChangeParent(MenuItem):
    name = 'Change parent'
    table = None
    mode = 'homogeneous'
    icon = ':/view-process-all-tree.png'
    def execute(self, session,explorer, ids, treeview, treedescription,tablename, **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        w= ChangeParentDialog(parent = treeview, session = session, ids = ids, 
                            class_ = class_, mapped_classes = treedescription.mapped_classes )
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
    

class EditRecordingChannelGroups(MenuItem):
    name = 'Edit RecordingChannelGroups'
    table = 'block'
    mode = 'unique'
    icon = ':/recordingchannelgroup.png'
    def execute(self, session,treeview, id, tablename,treedescription, explorer,  **kargs):
        class_ = treedescription.tablename_to_class[tablename]
        instance = session.query(class_).get(id)
        w= EditRecordingChannelGroupsDialog(parent = treeview, session = session,
                block = instance, mapped_classes = treedescription.mapped_classes)
        if w.exec_():
            explorer.refresh()


class SaveToFile(MenuItem):
    name = 'Save Block(s) to file'
    table = 'block'
    mode = 'homogeneous'
    icon = ':/document-save.png'

class EditOscillation(MenuItem):
    name = 'Edit Oscillations'
    table = 'analogsignal'
    mode = 'unique'
    icon = ':/oscillation.png'

class BaseSpikeSorting(MenuItem):
    table = 'recordingchannelgroup'
    mode = 'unique'
    icon = ':/spike.png'


class SpikeSortingFullBand(BaseSpikeSorting):
    name = 'Spike Sorting (mode = from_full_band_signal)'
    spike_sorting_mode = 'from_full_band_signal'
class SpikeSortingFiltered(BaseSpikeSorting):
    name = 'Spike Sorting (mode = from_filtered_signal)'
    spike_sorting_mode = 'from_filtered_signal'
class SpikeSortingSpike(BaseSpikeSorting):
    name = 'Spike Sorting (mode = from_detected_spike)'
    spike_sorting_mode = 'from_detected_spike'
class SpikeSortingWaveformFeatures(BaseSpikeSorting):
    name = 'Spike Sorting (mode = from_waveform_features)'
    spike_sorting_mode = 'from_waveform_features'


class DetecRespiratoryCycle(MenuItem):
    name = 'Detect respiratory cycles'
    table = 'respirationsignal'
    mode = 'unique'
    icon = ':/repiration.png'



context_menu = [ Delete, Edit, ChangeParent,CreateTop, 
                EditRecordingChannelGroups, SaveToFile,
                EditOscillation, 
                SpikeSortingFullBand, SpikeSortingFiltered, SpikeSortingSpike, SpikeSortingWaveformFeatures,
                DetecRespiratoryCycle,
                ]
