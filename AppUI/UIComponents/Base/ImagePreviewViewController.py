import webbrowser
from typing import Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QClipboard, QGuiApplication, QPixmap
from PyQt5.QtWidgets import QAction, QLabel, QMenu, QVBoxLayout, QWidget

from AppCore.Config import Configuration, ConfigurationProviderProtocol
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceEvent,
                                        PublishStatusUpdatedEvent,
                                        CacheClearedEvent)

from ...Assets import AssetProvider
from .LoadingSpinner import LoadingSpinner


class ImagePreviewViewControllerDelegate:
    def ip_rotate_resource(self, ip: ..., local_resource: LocalCardResource, angle: float) -> None:
        pass
    
    def ip_regenerate_preview(self, ip: ..., local_resource: LocalCardResource) -> None:
        pass
    
    def ip_redownload_resource(self, ip: ..., local_resource: LocalCardResource) -> None:
        pass
    
    def ip_regenerate_production_file(self, ip: ..., local_resource: LocalCardResource) -> None:
        pass
    
    def ip_open_file(self, ip: ..., local_resource: LocalCardResource) -> None:
        pass

    def ip_open_file_path_and_select_file(self, ip: ..., local_resource: LocalCardResource) -> None:
        pass

class ImagePreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProviderProtocol, 
                 asset_provider: AssetProvider):
        super().__init__()
        self.observation_tower = observation_tower
        self._configuration_provider = configuration_provider
        self._asset_provider = asset_provider
        self.delegate: Optional[ImagePreviewViewControllerDelegate] = None
        self._local_resource: Optional[LocalCardResource] = None
        
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self._image_view = label
        self._image_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._image_view.linkActivated.connect(self._handle_link_activated) # should only connect once
        self._image_view.customContextMenuRequested.connect(self._showContextMenu)
        self._image_view.setMinimumSize(256, 100)
        # self._image_view.setStyleSheet('background-color:red')
        self.loading_spinner = LoadingSpinner(self._image_view)
        
        # self._image_view.mousePressEvent = self._tapped_image # causes memory leak in child
        
        
        image_info_layout = QVBoxLayout()
        image_info_widget = QWidget()
        image_info_widget.setLayout(image_info_layout)
        self._image_info_widget = image_info_widget
        layout.addWidget(image_info_widget)
        
        # self._image_info_widget.setHidden(not self._configuration_provider.configuration.show_resource_details)
        
        
        
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

        self._toggle_resource_details_visibility()
        self._sync_image_view_state()

        observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent, 
                                                 LocalResourceEvent, 
                                                 PublishStatusUpdatedEvent, 
                                                 CacheClearedEvent])
    
    
    def set_image(self, local_resource: LocalCardResource):
        self._local_resource = local_resource
        self._sync_image_view_state()
    
    def clear_image(self):
        self._local_resource = None
        self._image_view.clear()
        self._clear_image_info()
        self._sync_image_view_state()
    
    def _showContextMenu(self, pos: QPoint):
        def _notify_delegate_regenerate_preview():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_regenerate_preview(self, self._local_resource)
                
        def _notify_delegate_redownload_resource():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_redownload_resource(self, self._local_resource)
       
        def _notify_delegate_rotate_right_image():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_rotate_resource(self, self._local_resource, -90)
        
        def _notify_delegate_rotate_left_image():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_rotate_resource(self, self._local_resource, 90)

        def open_file():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_open_file(self, self._local_resource)

        def open_file_path():
            if self._local_resource is not None and self.delegate is not None:
                self.delegate.ip_open_file_path_and_select_file(self, self._local_resource)
            
        def open_image_url():
            if self._local_resource is not None and self._local_resource.remote_image_url is not None:
                webbrowser.open(self._local_resource.remote_image_url)
            
        def copy_image_url():
            cb = QGuiApplication.clipboard()
            if cb is not None and self._local_resource is not None and self._local_resource.remote_image_url is not None:
                cb.clear(mode=QClipboard.Mode.Clipboard)
                cb.setText(self._local_resource.remote_image_url, mode=QClipboard.Mode.Clipboard)
        
        
        if self._local_resource is not None:
            menu = QMenu(self)
            refresh = QAction('Refresh')
            refresh.triggered.connect(self._sync_image_view_state)
            menu.addAction(refresh) # type: ignore
            
            if self._local_resource.is_ready:
                menu.addSeparator()
                regenerate_preview = QAction('Regenerate preview')
                regenerate_preview.triggered.connect(_notify_delegate_regenerate_preview)
                menu.addAction(regenerate_preview) # type: ignore
                
                if self._local_resource.remote_image_url is not None: # might need this even if resource is not ready
                    redownload_resource = QAction('Redownload')
                    redownload_resource.triggered.connect(_notify_delegate_redownload_resource)
                    menu.addAction(redownload_resource) # type: ignore
                
                menu.addSeparator()
                reveal_action = QAction(f"Open {self._local_resource.file_name_with_ext}", self)
                reveal_action.triggered.connect(open_file)
                menu.addAction(reveal_action) # type: ignore
                
                reveal_action = QAction(f"Reveal {self._local_resource.file_name_with_ext} in finder", self)
                reveal_action.triggered.connect(open_file_path)
                menu.addAction(reveal_action) # type: ignore
                
                if self._local_resource.remote_image_url is not None:
                    menu.addSeparator()
                    open_url_action = QAction(f'Open image url')
                    open_url_action.triggered.connect(open_image_url)
                    menu.addAction(open_url_action) # type: ignore
                    
                    copy_url_action = QAction(f'Copy image url')
                    copy_url_action.triggered.connect(copy_image_url)
                    menu.addAction(copy_url_action) # type: ignore
                    
                menu.addSeparator()
                rotate_right_action = QAction('Rotate right 90°')
                rotate_right_action.triggered.connect(_notify_delegate_rotate_right_image)
                menu.addAction(rotate_right_action) # type: ignore
                
                rotate_left_action = QAction('Rotate left 90°')
                rotate_left_action.triggered.connect(_notify_delegate_rotate_left_image)
                menu.addAction(rotate_left_action) # type: ignore
            
            menu.exec_(self.mapToGlobal(pos))

    class LinkKey:
        REGENERATE_PREVIEW = '#regenerate-preview'
        REDOWNLOAD_IMAGE = '#redownload-image'
        REGENERATE_PRODUCTION_FILE = '#regenerate-production-file'
    
    def _sync_image_view_state(self):
        self._toggle_resource_details_visibility()
        
        if self._local_resource is None:
            # empty state
            # self._image_view.setText('Image Placeholder')
            self.loading_spinner.stop()
            image = QPixmap()
            success = image.load(self._asset_provider.image.swu_logo_black_path)
            if success:
                self._image_view.setPixmap(image)
            return
        self._image_view.clear()
        self._clear_image_info()

        if self._local_resource.is_loading:
            self.loading_spinner.start()
            # TODO: handle case where spinner is not closed?
        
        elif self._local_resource.is_ready:
            self.loading_spinner.stop()
            self._set_image_info()
            if self._configuration_provider.configuration.hide_image_preview: # show text only
                self._image_view.setText(self._dynamic_display_name(self._local_resource))
                
            else: # show image
                image = QPixmap()
                success = image.load(self._local_resource.image_preview_path)
                if success:
                    self._image_view.setPixmap(image)
                else:
                    # existing resource, but no preview
                    self._image_view.setText(f'⚠️ No preview for {self._local_resource.display_name}. <a href="{self.LinkKey.REGENERATE_PREVIEW}">Regenerate</a>')

        else: # failed to load
            self.loading_spinner.stop()
            if self._local_resource.remote_image_url is not None:
                self._image_view.setText(f'⛔ {self._local_resource.display_name} not found. <a href="{self.LinkKey.REDOWNLOAD_IMAGE}">Redownload</a>')
            else:
                self._image_view.setText(f'⛔ {self._local_resource.display_name} not found. <a href="{self.LinkKey.REGENERATE_PRODUCTION_FILE}">Generate production file</a>')
    
        
    def _dynamic_display_name(self, local_resource: LocalCardResource) -> str:
        if self._configuration_provider.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.NORMAL:
            return local_resource.display_name
        elif self._configuration_provider.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
            return local_resource.display_name_short
        elif self._configuration_provider.configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
            return local_resource.display_name_detailed
        return " - "
    
    def _handle_link_activated(self, link: str):
        if self._local_resource is not None and self.delegate is not None:
            if link == self.LinkKey.REDOWNLOAD_IMAGE:
                self.delegate.ip_redownload_resource(self, self._local_resource)
            elif link == self.LinkKey.REGENERATE_PREVIEW:
                self.delegate.ip_regenerate_preview(self, self._local_resource)
            elif link == self.LinkKey.REGENERATE_PRODUCTION_FILE:
                self.delegate.ip_regenerate_production_file(self, self._local_resource)
    
    def _toggle_resource_details_visibility(self):
        self._card_display_name.setHidden(self._configuration_provider.configuration.hide_image_preview)
        self._image_info_widget.setHidden(not self._configuration_provider.configuration.show_resource_details or self._local_resource is None)
    
    def _set_image_info(self):
        if self._local_resource is not None and self._local_resource.is_ready:
            self._card_display_name.setText(self._dynamic_display_name(self._local_resource))
            
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
        if (type(event) == ConfigurationUpdatedEvent or 
            type(event) == PublishStatusUpdatedEvent or 
            type(event) == CacheClearedEvent):
            self._sync_image_view_state()
            
        if type(event) == LocalResourceEvent:
            if self._local_resource is not None and self._local_resource.image_preview_path == event.local_resource.image_preview_path:
                self._sync_image_view_state()
                if event.event_type == LocalResourceEvent.EventType.FAILED:
                    print(f"Failed resource: {self._local_resource.image_preview_path}")
                elif event.event_type == LocalResourceEvent.EventType.FINISHED:
                    print(f"Reloading resource: {self._local_resource.image_preview_path}")
