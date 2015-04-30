# -*- coding: utf-8 -*-
"""
This is a multiple video viewers.
"""


from tools import *


import os

#~ import cv2

mode = None
try :
    import imageio
    mode = 'imageio'
except:
    print 'no imageio'
    import skimage.io
    if 'Video' in dir(skimage.io):
        mode = 'skimage'
        




param_global = [
            {'name': 'nb_column', 'type': 'int', 'value': 4},
    ]

param_by_channel = [ 
                {'name': 'visible', 'type': 'bool', 'value': True},
            ] 





class VideoViewer(ViewerBase):
    """
    """
    def __init__(self, parent = None,
                            videofiles = [ ],
                            videotimes = None):
        super(VideoViewer,self).__init__(parent)
        
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.grid = QGridLayout()
        self.mainlayout.addLayout(self.grid)
        
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = param_global)
        
        # inialize
        self.set_videos(videofiles, videotimes = videotimes)
        
        self.paramGlobal.sigTreeStateChanged.connect(self.refresh)
    
    def set_videos(self, videofiles, videotimes = None):
        
        self.cv_image_widgets = [ ]
        self.grid_changing =False
        
        self.videofiles = videofiles
        self.videotimes = videotimes
        if self.videotimes is None:
            self.videotimes = [None]*len(videofiles)

        all = [ ]
        for i, vid in enumerate(self.videofiles):
            name = '{} {}'.format(i, os.path.basename(vid))
            all.append({ 'name': name, 'type' : 'group', 'children' : param_by_channel})
        self.paramVideos = pg.parametertree.Parameter.create(name='Videos', type='group', children=all)
        
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', children = [self.paramGlobal,self.paramVideos  ])
        
        self.paramControler = VideoViewerControler(viewer = self)
        
        
        #~ self.captures = [ ]
        self.videos = [ ]
        self.video_length = [ ]
        self.video_fps = [ ]
        for i, vid in enumerate(self.videofiles):
            #~ cap = cv2.VideoCapture(vid)
            #~ self.captures.append(cap)
            #~ self.video_length.append(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
            #~ self.video_fps.append(cap.get(cv2.cv.CV_CAP_PROP_FPS))
            
            if mode =='imageio':
                v  = imageio.get_reader(vid, format = 'avi', mode = 'I')
                self.videos.append(v)
                self.video_length.append(v.get_meta_data()['nframes'])
                self.video_fps.append(v.get_meta_data()['fps'])
            elif mode =='skimage':
                #~ v  = skimage.io.Video(source = vid, backend = 'gstreamer')
                v  = skimage.io.Video(source = vid, backend = 'opencv')
                self.videos.append(v)
                self.video_length.append(v.frame_count())
                #~ self.video_fps.append(25.)
                self.video_fps.append(float(v.duration())/v.frame_count())
            
            
            
            
        #~ print self.video_fps, self.video_length
        self.create_grid()
        
        self.paramVideos.sigTreeStateChanged.connect(self.create_grid)
        self.paramGlobal.param('nb_column').sigValueChanged.connect(self.create_grid)
        
        self.proxy = pg.SignalProxy(self.allParams.sigTreeStateChanged, rateLimit=5, delay=0.1, slot=self.refresh)
        

    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()

    def create_grid(self):

        n = len(self.videofiles)
        for cv_image_widget in self.cv_image_widgets:
            if cv_image_widget is not None:
                cv_image_widget.hide()
                self.grid.removeWidget(cv_image_widget)
        
        self.cv_image_widgets = [None for i in range(n)]
        self.frames = [-1000 for i in range(n)]
        
        r,c = 0,0
        for i, vid in enumerate(self.videofiles):
            if not self.paramVideos.children()[i].param('visible').value(): continue
            self.cv_image_widgets[i] = cw  = QtCVImageWIdget()
            self.cv_image_widgets[i].clicked.connect(self.open_configure_dialog)
            self.grid.addWidget(cw, r,c)
            
            c+=1
            if c==self.paramGlobal.param('nb_column').value():
                c=0
                r+=1
    
    def refresh(self, fast = False):
        
        for i, vid in enumerate(self.videofiles):
            if not self.paramVideos.children()[i].param('visible').value(): continue
            #~ print i
            if self.videotimes[i] is None:
                frame = int(self.t*self.video_fps[i])
            else :
                #~ allsup,  = np.where(self.t<self.videotimes[i])
                #~ if allsup.size>0:
                    #~ frame = allsup[0]
                #~ else:
                    #~ frame = self.videotimes[i].size-1
                allinf,  = np.where(self.t>=self.videotimes[i])
                if allinf.size>0:
                    frame = allinf[-1]
                else:
                    #~ frame = self.videotimes[i].size-1
                    frame = 0
            
            if mode =='imageio':
                if 0<=frame<self.video_length[i]:
                    im = self.videos[i].get_data(frame)
                else:
                    im = None
                self.frames[i] = frame
                if im is not None:
                    self.cv_image_widgets[i].set_image(im)
            
            elif mode =='skimage':
                if 0<frame<self.video_length[i] and frame !=self.frames[i]:
                    # opencv is bad for seek in a video stream so we cache the last image
                    if 0<(frame-self.frames[i])<self.video_fps[i]+2:
                        # until one seconde we read in loop
                        for f in range(frame-self.frames[i]):
                            #~ ret, im = self.captures[i].read()
                            im = self.videos[i].get()
                    else:
                        # otherwise a long seek but this flash
                        #~ print 'long seek',i,  self.frames[i], frame
                        #~ self.captures[i].set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame)
                        #~ ret, im = self.captures[i].read()
                        im = self.videos[i].get_index_frame(frame)
                    self.frames[i] = frame
                    #~ print i, im.shape
                    if im is not None:
                        self.cv_image_widgets[i].set_image(im)
        
        
        self.is_refreshing = False
        
        

class QtCVImageWIdget(QWidget):
    """
    Similar to pyqtgraph.RawImageWidget but play directly with OpenCV format.
    """
    clicked = pyqtSignal()
    def __init__(self, parent = None, with_ratio = True):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        self.qimage = None
        self.image = None
        self.with_ratio = with_ratio
        #~ self.setBackGroundColor(QColor('black'))

    def mousePressEvent (self, ev):
        self.clicked.emit()
        ev.accept()
        
    def set_image(self, cv_im):
        if self.image is None:
            self.image = np.empty(cv_im.shape[:2] + (4,), dtype=cv_im.dtype)
            self.image[:,:,3] = 255
        
        self.image[:,:,:3] = cv_im
        self.qimage = QImage(buffer(self.image), cv_im.shape[1], cv_im.shape[0], QImage.Format_RGB32)
        self.update()
        

    def paintEvent(self, ev):
        if self.qimage is None:
            return
        p = QPainter(self)

        rect = self.rect()
        if self.with_ratio:
            ar = rect.width() / float(rect.height())
            imar = self.qimage.width() / float(self.qimage.height())
            if ar > imar:
                rect.setWidth(int(rect.width() * imar/ar))
            else:
                rect.setHeight(int(rect.height() * ar/imar))
                
        p.drawImage(rect, self.qimage)
        p.end()





class VideoViewerControler(QWidget):
    def __init__(self, parent = None, viewer = None):
        super(VideoViewerControler, self).__init__(parent)


        self.viewer = viewer

        #layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        t = u'Options for EpochArrays'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.treeParamEpoch = pg.parametertree.ParameterTree()
        self.treeParamEpoch.header().hide()
        h.addWidget(self.treeParamEpoch)
        self.treeParamEpoch.setParameters(self.viewer.paramVideos, showTop=True)
        
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.treeParamGlobal = pg.parametertree.ParameterTree()
        self.treeParamGlobal.header().hide()
        v.addWidget(self.treeParamGlobal)
        self.treeParamGlobal.setParameters(self.viewer.paramGlobal, showTop=True)
        
        v.addWidget(QLabel(self.tr('<b>Automatic color:<\b>'),self))
        but = QPushButton('Progressive')
        but.clicked.connect(self.automatic_color)
        v.addWidget(but)


    
    def automatic_color(self):
        n = len(self.viewer.epocharrays)
        cmap = get_cmap('jet' , n)
        for i, pEpoch in enumerate(self.viewer.paramEpochs.children()):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            pEpoch.param('color').setValue(color)
       
            

