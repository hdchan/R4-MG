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
        self._configuration_provider = configuration_provider
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self._image_view = label
        self._image_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._image_view.customContextMenuRequested.connect(self.showContextMenu)
        # self._image_view.mousePressEvent = self._tapped_image # causes memory leak in child
        
        image_info_layout = QVBoxLayout()
        image_info_widget = QWidget()
        image_info_widget.setLayout(image_info_layout)
        self._image_info_widget = image_info_widget
        layout.addWidget(image_info_widget)
        self._image_info_widget.setHidden(not self._configuration_provider.configuration.show_resource_details)
        
        
        self._card_display_name = QLabel()
        self._card_display_name.setOpenExternalLinks(True)
        self._card_display_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._card_display_name)
        
        self._size_info_label = QLabel()
        self._size_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._size_info_label)
        
        self._image_url_label = QLabel()
        self._image_url_label.setOpenExternalLinks(True)
        self._image_url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._image_url_label)

        self.loading_spinner = LoadingSpinner(self)

        self._local_resource: Optional[LocalCardResource] = None
        
        observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent, 
                                                 LocalResourceEvent])
        
        
        
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
        self._clear_image_info()
    
    def set_image(self, local_resource: LocalCardResource):
        self._local_resource = local_resource
        self._load_image()
    
    def _load_image(self):
        if self._local_resource is None:
            self.loading_spinner.stop()
            return
        self._image_view.clear()
        self._clear_image_info()
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
                    self._set_image_info()
                        
        else: # failed to load
            self.loading_spinner.stop()
    
    def _toggle_resource_details_visibility(self):
        self._image_info_widget.setHidden(not self._configuration_provider.configuration.show_resource_details)
    
    def _set_image_info(self):
        if self._local_resource is not None and self._local_resource.is_ready:
            self._card_display_name.setText(self._local_resource.display_name)
            
            if self._local_resource.size is not None:
                image_w, image_h = self._local_resource.size
                self._size_info_label.setText(f'{image_w}W x {image_h}H')
                
            if self._local_resource.remote_image_url is not None:
                url = self._local_resource.remote_image_url
                self._image_url_label.setText(f'<a href="{url}">{url}</a>')
                        
    def _clear_image_info(self):
        self._card_display_name.clear()
        self._size_info_label.clear()
        self._image_url_label.clear()

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            self._load_image()
            self._toggle_resource_details_visibility()
            
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