from typing import List, Optional, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton, QScrollArea, QVBoxLayout,
                             QWidget, QSizePolicy, QAbstractSlider)

from AppCore import ConfigurationProvider, ObservationTower
from AppCore.Models import LocalCardResource

from ...Assets import AssetProvider
from . import ImageDeploymentViewController, ImagePreviewViewControllerDelegate
from ..Base import AddImageCTAViewController, AddImageCTAViewControllerDelegate

class ImageDeploymentListViewControllerDelegate:
    def idl_did_tap_staging_button(self, id_list: ..., id_cell: ImageDeploymentViewController, index: int) -> None:
        pass

    def idl_did_tap_unstaging_button(self, id_list: ..., id_cell: ImageDeploymentViewController, index: int) -> None:
        pass
    
    def idl_did_tap_production_button(self, id_list: ...) -> None:
        pass

class ImageDeploymentListViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProvider, 
                 asset_provider: AssetProvider, 
                 image_preview_delegate: Union[AddImageCTAViewControllerDelegate, ImagePreviewViewControllerDelegate]):
        super().__init__()

        self.observation_tower = observation_tower
        self.configuration_provider = configuration_provider
        self.asset_provider = asset_provider
        self.image_preview_delegate = image_preview_delegate

        outer_container_layout = QVBoxLayout()
        self.setLayout(outer_container_layout)
        
        cells_container_layout = QVBoxLayout()
        cells_container_layout.setContentsMargins(0, 0, 0, 0)
        cells_container_widget = QWidget()
        cells_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # prevent stretching of container in scroll view
        cells_container_widget.setLayout(cells_container_layout)
        
        deployment_cells_layout = QVBoxLayout()
        deployment_cells_layout.setContentsMargins(0, 0, 0, 0)
        deployment_cells_widget = QWidget()
        deployment_cells_widget.setLayout(deployment_cells_layout)
        self._deployment_cells_layout = deployment_cells_layout
        cells_container_layout.addWidget(deployment_cells_widget)
        
        
        add_image_cta = AddImageCTAViewController(asset_provider)
        add_image_cta.delegate = image_preview_delegate
        cells_container_layout.addWidget(add_image_cta)
        
        
        self.scroll_view = QScrollArea(self)
        # https://stackoverflow.com/a/75781450
        # scroll_view.verticalScrollBar().actionTriggered.connect(self.scrolled)
        # self.position = self.scroll_view.verticalScrollBar().sliderPosition()
        # self.scroll_view.verticalScrollBar().actionTriggered.connect(self.on_scroll)
        # self.scroll_view.verticalScrollBar().valueChanged.connect(self.scrolled)
        self.scroll_view.setWidget(cells_container_widget)
        self.scroll_view.setWidgetResizable(True)
        # self.scroll = scroll_view
        outer_container_layout.addWidget(self.scroll_view)
        

        production_button = QPushButton()
        production_button.setText("Production (Ctrl+P)")
        production_button.setEnabled(False)
        production_button.clicked.connect(self.tapped_production_button)
        self.production_button = production_button
        outer_container_layout.addWidget(production_button)

        self.list_items: List[ImageDeploymentViewController] = []
        
        self.delegate: Optional[ImageDeploymentListViewControllerDelegate] = None
    
    def on_scroll(self, action):
        
        # In case you scroll using the mouse wheel or clicking the bar.
        if(self.scroll_view.verticalScrollBar().sliderPosition() > self.position):
            print('scroll down occurred ')
            self.position = self.scroll_view.verticalScrollBar().sliderPosition()
        if(self.scroll_view.verticalScrollBar().sliderPosition() < self.position):
            print('scroll up occurred ')
            self.position = self.scroll_view.verticalScrollBar().sliderPosition()
        
        # SliderSingleStepAdd for when you click the arrow up.
        # SliderPageStepAdd for when you click the bar up.    
        if (action == QAbstractSlider.SliderSingleStepAdd) or (action == QAbstractSlider.SliderPageStepAdd):
            print('scroll down occurred ')
        # SliderSingleStepSub for when you click the arrow down.
        # SliderPageStepSub for when you click the bar down.
        if (action == QAbstractSlider.SliderSingleStepSub) or (action == QAbstractSlider.SliderPageStepSub):
            print('scroll up occurred ')

    # https://stackoverflow.com/questions/23525448/python-pyqt-scrollbar-in-the-end-position-event
    def scrolled(self, value):
        print(self.scroll_view.verticalScrollBar().sliderPosition(), value, self.scroll_view.verticalScrollBar().maximum())
        if value == self.scroll_view.verticalScrollBar().maximum():
            print ('reached max') # that will be the bottom/right end
        if value == self.scroll_view.verticalScrollBar().minimum():
            print ('reached min') # top/left end
    
    def load_production_resources(self, card_resources: List[LocalCardResource], staging_button_enabled: bool):
        for index, resource in enumerate(card_resources):
            self._create_list_item(resource,
                                   staging_button_enabled,
                                   index)
            
        print(self.scroll_view.verticalScrollBar().sliderPosition(), self.scroll_view.verticalScrollBar().maximum())

    def _create_list_item(self,
                         local_resource: LocalCardResource,
                         staging_button_enabled: bool,
                         index: int):
        item = ImageDeploymentViewController(self.observation_tower, 
                                             self.configuration_provider, 
                                             self.image_preview_delegate, 
                                             self.asset_provider)
        item.delegate = self
        item.set_production_image(local_resource)
        if index <= 9:
            item.stage_button.setText(f'Stage (Ctrl+{index + 1})')
        else:
            item.stage_button.setText(f'Stage')
        item.set_staging_button_enabled(staging_button_enabled)
        
        pal = item.palette()
        pal.setColor(item.backgroundRole(), Qt.GlobalColor.lightGray)
        item.setAutoFillBackground(True)
        item.setPalette(pal)
        self._deployment_cells_layout.addWidget(item)

        self.list_items.append(item)

    def clear_list(self):
        for i in reversed(range(self._deployment_cells_layout.count())):
            layout_item = self._deployment_cells_layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.list_items = []

    def id_did_tap_staging_button(self, id_cell: ImageDeploymentViewController):
        for idx, i in enumerate(self.list_items):
            if i == id_cell and self.delegate is not None:
                self.delegate.idl_did_tap_staging_button(self, id_cell, idx)

    def id_did_tap_unstaging_button(self, id_cell: ImageDeploymentViewController):
        for idx, i in enumerate(self.list_items):
            if i == id_cell and self.delegate is not None:
                self.delegate.idl_did_tap_unstaging_button(self, id_cell, idx)

    def set_staging_image(self, local_resource: LocalCardResource, index: int):
        self.list_items[index].set_staging_image(local_resource)

    def clear_staging_image(self, index: int):
        self.list_items[index].clear_staging_image()
    
    def set_production_image(self, local_resource: LocalCardResource, index: int):
        self.list_items[index].set_production_image(local_resource)


    def clear_all_staging_images(self):
        for i in self.list_items:
            i.clear_staging_image()

    def tapped_production_button(self):
        if self.delegate is not None:
            self.delegate.idl_did_tap_production_button(self)
        
    def set_all_staging_button_enabled(self, enabled: bool):
        for i in self.list_items:
            i.set_staging_button_enabled(enabled)

    def set_production_button_enabled(self, enabled: bool):
        self.production_button.setEnabled(enabled)
        if enabled:
            self.production_button.setStyleSheet("background-color : #41ad49; color: white;")
        else:
            self.production_button.setStyleSheet("")