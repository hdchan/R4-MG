from AppCore.Observation import *
from PyQt5.QtCore import Qt
from .ImagePreviewViewController import ImagePreviewViewController
from AppCore.Models import LocalCardResource

class ImagePopoutViewController(ImagePreviewViewController, TransmissionReceiverProtocol):
    
    def setup(self, local_resource: LocalCardResource):
        self.set_image(local_resource)
        self._local_resource = local_resource
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(self._local_resource.file_name)
    # https://stackoverflow.com/questions/48191399/pyqt-fading-a-qlabel
    # def startFadeIn(self):
    #     self.animation.stop()
    #     self.animation.setStartValue(QColor(0, 0, 0, 0))
    #     self.animation.setEndValue(QColor(0, 0, 0, 255))
    #     self.animation.setDuration(2000)
    #     self.animation.setEasingCurve(QEasingCurve.InBack)
    #     self.animation.start()

    # def startFadeOut(self):
    #     self.animation.stop()
    #     self.animation.setStartValue(QColor(0, 0, 0, 255))
    #     self.animation.setEndValue(QColor(0, 0, 0, 0))
    #     self.animation.setDuration(2000)
    #     self.animation.setEasingCurve(QEasingCurve.OutBack)
    #     self.animation.start()

    # def startAnimation(self):
    #     self.startFadeIn()
    #     loop = QEventLoop()
    #     self.animation.finished.connect(loop.quit)
    #     loop.exec_()
    #     QTimer.singleShot(2000, self.startFadeOut)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        pass
        # if type(event) == LocalResourceEvent:
        #     if self._local_resource.file_name == event.local_resource.file_name:
        #         self._load_image_view()
        #         print(f"Reloading resource: {self._img_path}")
        
                
            