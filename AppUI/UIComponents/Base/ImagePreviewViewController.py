from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from typing import Optional
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QAction, QMenu

from AppCore.Config import ConfigurationProvider
from AppCore.Observation import ObservationTower, TransmissionReceiver
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceEvent)
from AppCore.Models import LocalCardResource
from .LoadingSpinner import LoadingSpinner
from AppCore.Observation.Events import TransmissionProtocol
import subprocess
import os
import webbrowser

class ImagePreviewViewController(QWidget, TransmissionReceiver):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProvider):
        super().__init__()
        self.observation_tower = observation_tower
        layout = QVBoxLayout(self)
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        self._image_view = label
        # self._image_view.mousePressEvent = self._tapped_image # causes memory leak in child
        self.loading_spinner = LoadingSpinner(self)

        self._local_resource: Optional[LocalCardResource] = None
        self._configuration_provider = configuration_provider

        observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent, 
                                                 LocalResourceEvent])
        
        self._image_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._image_view.customContextMenuRequested.connect(self.showContextMenu)
        
    def showContextMenu(self, pos):
        if self._local_resource is not None and self._local_resource.is_ready:
            menu = QMenu(self)
            action1 = QAction(f"Reveal {self._local_resource.file_name_with_ext} in finder", self) # full image
            action1.triggered.connect(self.open_file_path)
            menu.addAction(action1)
            if self._local_resource.remote_image_url is not None:
                action3 = QAction(f'Open image url')
                action3.triggered.connect(self.open_image_url)
                menu.addAction(action3)
                
                action4 = QAction(f'Copy image url')
                action4.triggered.connect(self.copy_image_url)
                menu.addAction(action4)
            
            menu.exec_(self.mapToGlobal(pos))

    def open_file_path(self):
        # https://stackoverflow.com/a/55975564
        subprocess.Popen(rf'explorer /select,"{os.path.abspath(self._local_resource.image_path)}"')
        
    def copy_file_path(self):
        cb = QGuiApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self._local_resource.image_path, mode=cb.Clipboard)
        
    def open_image_url(self):
        webbrowser.open(self._local_resource.remote_image_url)
        
        
    def copy_image_url(self):
        cb = QGuiApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self._local_resource.remote_image_url, mode=cb.Clipboard)

    def clear_image(self):
        self._local_resource = None
        self._image_view.clear()
    
    def set_image(self, local_resource: LocalCardResource):
        self._local_resource = local_resource
        self._load_image()
    
    def _load_image(self):
        if self._local_resource is None:
            self.loading_spinner.stop()
            return
        self._image_view.clear()
        if self._local_resource.is_loading:
            self.loading_spinner.start()
        elif self._local_resource.is_ready:
            self.loading_spinner.stop()
            if self._configuration_provider.configuration.is_performance_mode:
                self._image_view.setText(self._local_resource.display_name)
            else:
                image = QPixmap()
                success = image.load(self._local_resource.image_preview_path)
                if success:
                    self._image_view.setPixmap(image)
        else: # failed to load
            self.loading_spinner.stop()

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            self._load_image()
        elif type(event) == LocalResourceEvent:
            if self._local_resource is not None:
                if self._local_resource.image_preview_path == event.local_resource.image_preview_path:
                    self._load_image()
                    if event.event_type == LocalResourceEvent.EventType.FAILED:
                        print(f"Failed resource: {self._local_resource.image_preview_path}")
                    elif event.event_type == LocalResourceEvent.EventType.FINISHED:
                        print(f"Reloading resource: {self._local_resource.image_preview_path}")
                
    def _tapped_image(self, ev: Optional[QMouseEvent]) -> None:
        if self._img_path is not None:
            # print(self._img_path)
            pass