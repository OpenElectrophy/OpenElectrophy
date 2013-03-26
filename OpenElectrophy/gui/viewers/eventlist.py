# -*- coding: utf-8 -*-
"""
Event list change time on click.
"""


from tools import *





class EventList(ViewerBase):
    """
    """
    time_changed = pyqtSignal(float)
    def __init__(self, parent = None,
                eventarrays = [ ],xsize=5.):
        super(EventList,self).__init__(parent)
        
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        self.eventarrays = eventarrays
        
        self.combo = QComboBox()
        self.mainlayout.addWidget(self.combo)
        self.list = QListWidget()
        self.mainlayout.addWidget(self.list)
        self.combo.currentIndexChanged.connect(self.refresh_list)
        self.combo.addItems([ev.name for ev in self.eventarrays ])
        
        self.list.currentRowChanged.connect(self.select_event)
        
    def refresh(self):
        pass
        
    def refresh_list(self, ind):
        self.ind = ind
        self.list.clear()
        ev = self.eventarrays[ind]
        for i in range(len(self.eventarrays[ind].times)):
            if i>=len(ev.labels):
                self.list.addItem('{} : {:.3f}'.format(i, float(ev.times[i].rescale('s').magnitude)) )
            else:
                self.list.addItem('{} : {:.3f} {}'.format(i, float(ev.times[i].rescale('s').magnitude), ev.labels[i]) )

        
    def select_event(self, i):
        ev = self.eventarrays[self.ind]
        t = ev.times[i].rescale('s').magnitude
        self.time_changed.emit(t)
        