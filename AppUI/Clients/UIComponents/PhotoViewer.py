from typing import Callable
from typing import List, Optional
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
SCALE_FACTOR = 1.25
from PyQt5.QtGui import QContextMenuEvent, QImage


class PhotoViewer(QtWidgets.QGraphicsView):
    coordinatesChanged = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._photo.setShapeMode(
            QtWidgets.QGraphicsPixmapItem.BoundingRectShape)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._clipboard_image: Optional[QImage] = None

    def hasPhoto(self):
        return not self._empty

    def resetView(self, scale=1):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height()) * scale
                self.scale(factor, factor)
                if not self.zoomPinned():
                    self.centerOn(self._photo)
                self.updateCoordinates()

    def setPhoto(self, pixmap: Optional[QPixmap] = None, qImage: Optional[QImage] = None):
        self._clipboard_image = qImage
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        if not (self.zoomPinned() and self.hasPhoto()):
            self._zoom = 0
        self.resetView(SCALE_FACTOR ** self._zoom)

    def zoomLevel(self):
        return self._zoom

    def zoomPinned(self):
        return self._pinned

    def setZoomPinned(self, enable):
        self._pinned = bool(enable)

    def zoom(self, step):
        zoom = max(0, self._zoom + (step := int(step)))
        if zoom != self._zoom:
            self._zoom = zoom
            if self._zoom > 0:
                if step > 0:
                    factor = SCALE_FACTOR ** step
                else:
                    factor = 1 / SCALE_FACTOR ** abs(step)
                self.scale(factor, factor)
            else:
                self.resetView()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom(delta and delta // abs(delta))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resetView()

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def updateCoordinates(self, pos=None):
        if self._photo.isUnderMouse():
            if pos is None:
                pos = self.mapFromGlobal(QtGui.QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QtCore.QPoint()
        self.coordinatesChanged.emit(point)

    def mouseMoveEvent(self, event):
        self.updateCoordinates(event.pos())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.coordinatesChanged.emit(QtCore.QPoint())
        super().leaveEvent(event)
        
    def contextMenuEvent(self, a0: Optional[QContextMenuEvent]):
        context_menu = QtWidgets.QMenu(self)
        
        delete_action = QtWidgets.QAction(f"Copy Image", self)
        delete_action.triggered.connect(self._copy_to_clipboard)
        context_menu.addAction(delete_action) # type: ignore

        if a0 is not None:
            context_menu.exec_(a0.globalPos())

    def _copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        # clipboard.setImage(self._clipboard_image)
        clipboard.setPixmap(self._photo.pixmap())
        
class PhotoViewerWindow(QtWidgets.QWidget):
    def __init__(self, initial_colum_size: int, text_changed_fn: Callable[[int], None]):
        super().__init__()
        # self.setGeometry(500, 300, 800, 600)
        self._text_changed_fn = text_changed_fn
        self.viewer = PhotoViewer(self)
        self.viewer.coordinatesChanged.connect(self.handleCoords)
        self.labelCoords = QtWidgets.QLabel(self)
        self.labelCoords.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        # self.buttonOpen = QtWidgets.QPushButton(self)
        # self.buttonOpen.setText('Open Image')
        # self.buttonOpen.clicked.connect(self.handleOpen)
        # self.buttonPin = QtWidgets.QPushButton(self)
        # self.buttonPin.setText('Pin Zoom')
        # self.buttonPin.setCheckable(True)
        # self.buttonPin.toggled.connect(self.viewer.setZoomPinned)
        self._column_edit = QtWidgets.QLineEdit()
        validator = QtGui.QIntValidator(self) 
        self._column_edit.setText(str(initial_colum_size))
        self._column_edit.setValidator(validator)
        # self._column_edit.textChanged.connect(self._text_changed)
        
        self._update_button = QtWidgets.QPushButton(self)
        self._update_button.setText("Update columns")
        self._update_button.clicked.connect(self._text_changed)
        
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.viewer, 0, 0, 1, 3)
        layout.addWidget(self._column_edit)
        layout.addWidget(self._update_button)
        # layout.addWidget(self.buttonOpen, 1, 0, 1, 1)
        # layout.addWidget(self.buttonPin, 1, 1, 1, 1)
        layout.addWidget(self.labelCoords, 1, 2, 1, 1)
        layout.setColumnStretch(2, 2)
        self._path = None

    def _text_changed(self):
        try:
            value = self._column_edit.text()
            int_value = int(value)
            self._text_changed_fn(int_value)
        except:
            pass

    def handleCoords(self, point):
        if not point.isNull():
            self.labelCoords.setText(f'{point.x()}, {point.y()}')
        else:
            self.labelCoords.clear()

    # def handleOpen(self):
    #     if (start := self._path) is None:
    #         start = QtCore.QStandardPaths.standardLocations(
    #             QtCore.QStandardPaths.PicturesLocation)[0]
    #     if path := QtWidgets.QFileDialog.getOpenFileName(
    #         self, 'Open Image', start)[0]:
    #         self.labelCoords.clear()
    #         if not (pixmap := QtGui.QPixmap(path)).isNull():
    #             self.viewer.setPhoto(pixmap)
    #             self._path = path
    #         else:
    #             QtWidgets.QMessageBox.warning(self, 'Error',
    #                 f'<br>Could not load image file:<br>'
    #                 f'<br><b>{path}</b><br>'
    #                 )