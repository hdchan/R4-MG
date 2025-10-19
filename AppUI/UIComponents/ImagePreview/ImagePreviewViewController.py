from typing import Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QClipboard, QGuiApplication, QPixmap
from PyQt5.QtWidgets import QAction, QLabel, QMenu, QVBoxLayout

from AppCore.Config import Configuration
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import (CacheClearedEvent,
                                        ConfigurationUpdatedEvent,
                                        LocalCardResourceFetchEvent,
                                        PublishStatusUpdatedEvent)
from AppCore.Service.PlatformServiceProvider import *
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import RWidget

from ..Base.LoadingSpinner import LoadingSpinner

MAX_PREVIEW_SIZE = 256
class ImagePreviewViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding, 
                 # whether we can manipulate images
                 can_post_process: bool = True):
        super().__init__()
        self._can_post_process = can_post_process
        self._observation_tower = app_dependencies_provider.observation_tower
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._asset_provider = app_dependencies_provider.asset_provider
        self._image_resource_processor_provider = app_dependencies_provider.image_resource_processor_provider
        self._platform_service_provider = app_dependencies_provider.platform_service_provider
        self._router = app_dependencies_provider.router
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._local_resource: Optional[LocalCardResource] = None
        
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self._image_view = label
        self._image_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._image_view.linkActivated.connect(self._handle_link_activated) # should only connect once
        self._image_view.customContextMenuRequested.connect(self._show_context_menu)
        # self._image_view.setMinimumSize(50, 50)
        self.loading_spinner = LoadingSpinner(self._image_view)
        
        # self._image_view.mousePressEvent = self._tapped_image # causes memory leak in child
        
        image_info_layout = QVBoxLayout()
        image_info_widget = RWidget()
        image_info_widget.setLayout(image_info_layout)
        self._image_info_widget = image_info_widget
        layout.addWidget(image_info_widget)
        
        
        self._card_display_name = QLabel()
        self._card_display_name.setWordWrap(True)
        self._card_display_name.setOpenExternalLinks(True)
        self._card_display_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._card_display_name)
        
        self._size_info_label = QLabel()
        self._size_info_label.setWordWrap(True)
        self._size_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._size_info_label)
        
        self._created_date_label = QLabel()
        self._created_date_label.setWordWrap(True)
        self._created_date_label.setOpenExternalLinks(True)
        self._created_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._created_date_label)

        self._image_url_label = QLabel()
        # self._image_url_label.setMaximumWidth(100)
        self._image_url_label.setWordWrap(True)
        self._image_url_label.setOpenExternalLinks(True)
        self._image_url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_info_layout.addWidget(self._image_url_label)

        self._toggle_resource_details_visibility()
        self._sync_image_view_state()

        app_dependencies_provider.observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent, 
                                                 LocalCardResourceFetchEvent, 
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
    
    @property
    def _platform_service(self) -> PlatformServiceProtocol:
        return self._platform_service_provider.platform_service

    @property
    def _image_resource_processor(self):
        return self._image_resource_processor_provider.image_resource_processor

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    def _show_context_menu(self, pos: QPoint):
        def _notify_delegate_regenerate_preview():
            if self._local_resource is not None:
                self._image_resource_processor.regenerate_resource_preview(self._local_resource)
                
        def _notify_delegate_redownload_resource():
            if self._local_resource is not None:
                self._image_resource_processor.async_store_local_resource(self._local_resource, True)
       
        def _notify_delegate_rotate_right_image():
            if self._local_resource is not None:
                self._image_resource_processor.rotate_and_save_resource(self._local_resource, -90)
        
        def _notify_delegate_rotate_left_image():
            if self._local_resource is not None:
                self._image_resource_processor.rotate_and_save_resource(self._local_resource, 90)

        def open_file():
            if self._local_resource is not None:
                self._platform_service.open_file(self._local_resource.image_path)

        def open_file_directory():
            if self._local_resource is not None:
                self._platform_service.open_file_directory_and_select_file(self._local_resource.image_path)
            
        def open_image_url():
            if self._local_resource is not None and self._local_resource.remote_image_url is not None:
                self._router.open_link_to_card_resource(self._local_resource)
            
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
                
                action_label = self._local_resource.file_name_with_ext if self._configuration.is_developer_mode else "image"
                open_action = QAction(f"Open {action_label}", self)
                open_action.triggered.connect(open_file)
                menu.addAction(open_action) # type: ignore
                
                reveal_action = QAction(f"Reveal {action_label} in file explorer", self)
                reveal_action.triggered.connect(open_file_directory)
                menu.addAction(reveal_action) # type: ignore
                
                if self._local_resource.remote_image_url is not None:
                    menu.addSeparator()
                    open_url_action = QAction(f'Open image url')
                    open_url_action.triggered.connect(open_image_url)
                    menu.addAction(open_url_action) # type: ignore
                    
                    copy_url_action = QAction(f'Copy image url')
                    copy_url_action.triggered.connect(copy_image_url)
                    menu.addAction(copy_url_action) # type: ignore
                
                if self._can_post_process:
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
        # self._image_view.setMinimumSize(50, 50)
        if self._local_resource is None:
            # empty state
            self.loading_spinner.stop()
            if self._configuration.hide_image_preview: # show text only
                self._image_view.setText('[Placeholder]')
            else:
                image = QPixmap()
                success = image.load(self._external_app_dependencies_provider.image_preview_logo_path)
                if success:
                    # TODO: consolidate with image logic below
                    image_width = image.size().width()
                    image_height = image.size().height()
                    multiplier = MAX_PREVIEW_SIZE / max(image_width, image_height)
                    multiplier *= self._configuration.image_preview_scale * 0.5 # normal should be smaller
                    final_width, final_height = int(image_width * multiplier), int(image_height * multiplier)
                    self._image_view.setMinimumSize(final_width, final_height)
                    scaled_image = image.scaled(final_width, final_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self._image_view.setPixmap(scaled_image)
                else:
                    self._image_view.setText('[Placeholder]')
            return
        self._image_view.clear()
        self._clear_image_info()

        if self._local_resource.is_loading:
            if self.loading_spinner.is_spinning is False:
                self.loading_spinner.start()
            # TODO: handle case where spinner is not closed?
        
        elif self._local_resource.is_ready:
            self.loading_spinner.stop()
            self._set_image_info()
            if self._configuration.hide_image_preview: # show text only
                self._image_view.setText(self._dynamic_display_name(self._local_resource))
                
            else: # show image
                image = QPixmap()
                success = image.load(self._local_resource.image_preview_path)
                if success:
                    # TODO: consolidate with image logic above
                    # TODO: create dimension specific for cache
                    image_width = image.size().width()
                    image_height = image.size().height()
                    multiplier = MAX_PREVIEW_SIZE / max(image_width, image_height)
                    multiplier *= self._configuration.image_preview_scale
                    final_width, final_height = int(image_width * multiplier), int(image_height * multiplier)
                    self._image_view.setMinimumSize(final_width, final_height)
                    scaled_image = image.scaled(final_width, final_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self._image_view.setPixmap(scaled_image)
                else:
                    # existing resource, but no preview
                    self._image_view.setText(f'⚠️ No preview for {self._local_resource.display_name}. <a href="{self.LinkKey.REGENERATE_PREVIEW}">Regenerate</a>')

        else: # failed to load
            self.loading_spinner.stop()
            if self._local_resource.remote_image_url is not None:
                self._image_view.setText(f'⛔ {self._local_resource.display_name} not found. <a href="{self.LinkKey.REDOWNLOAD_IMAGE}">Redownload</a>')
            elif self._local_resource.can_be_replaced_with_placeholder:
                self._image_view.setText(f'⛔ {self._local_resource.display_name} not found. <a href="{self.LinkKey.REGENERATE_PRODUCTION_FILE}">Generate placeholder</a>')
            else:
                self._image_view.setText(f'⛔ {self._local_resource.display_name} not found')
    
        
    def _dynamic_display_name(self, local_resource: LocalCardResource) -> str:
        if self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.NORMAL:
            return local_resource.display_name
        elif self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT:
            return local_resource.display_name_short
        elif self._configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED:
            return local_resource.display_name_detailed
        return " - "
    
    def _handle_link_activated(self, link: str):
        if self._local_resource is not None:
            if link == self.LinkKey.REDOWNLOAD_IMAGE:
                self._image_resource_processor.async_store_local_resource(self._local_resource, True)
            elif link == self.LinkKey.REGENERATE_PREVIEW:
                self._image_resource_processor
                self._image_resource_processor.regenerate_resource_preview(self._local_resource)
            elif link == self.LinkKey.REGENERATE_PRODUCTION_FILE:
                self._image_resource_processor.generate_placeholder(self._local_resource, self._external_app_dependencies_provider.card_back_image_path)
                self._sync_image_view_state()
    
    def _toggle_resource_details_visibility(self):
        self._card_display_name.setHidden(self._configuration.hide_image_preview)
        self._image_info_widget.setHidden(not self._configuration.show_resource_details or self._local_resource is None)
    
    def _set_image_info(self):
        if self._local_resource is not None and self._local_resource.is_ready:
            self._card_display_name.setText(self._dynamic_display_name(self._local_resource))
            
            image_w, image_h = self._local_resource.size
            self._size_info_label.setText(f'Size: {image_w}W x {image_h}H')

            self._image_url_label.setHidden(self._local_resource.remote_image_url is None)
            if self._local_resource.remote_image_url is not None:
                url = self._local_resource.remote_image_url
                self._image_url_label.setText(f'Source: <a href="{url}">{url}</a>')
            
            self._created_date_label.setText(f'Created: {self._local_resource.created_date.strftime("%m/%d/%Y, %I:%M %p")}')
                        
    def _clear_image_info(self):
        self._card_display_name.clear()
        self._size_info_label.clear()
        self._image_url_label.clear()
        self._created_date_label.clear()


    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if (type(event) == ConfigurationUpdatedEvent or 
            type(event) == PublishStatusUpdatedEvent or 
            type(event) == CacheClearedEvent):
            self._sync_image_view_state()
            
        if type(event) == LocalCardResourceFetchEvent:
            if self._local_resource is not None and self._local_resource.image_preview_path == event.local_resource.image_preview_path:
                self._sync_image_view_state()
                if event.event_type == LocalCardResourceFetchEvent.EventType.FAILED:
                    print(f"Failed resource: {self._local_resource.image_preview_path}")
                elif event.event_type == LocalCardResourceFetchEvent.EventType.FINISHED:
                    print(f"Reloading resource: {self._local_resource.image_preview_path}")
