from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QWidget

from AppUI.AppDependencyProviding import AppDependencyProviding
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController)


class MainProgramViewController(QWidget):
    def __init__(self,
                 app_dependency_provider: AppDependencyProviding,
                 card_search_preview_view_controller: CardSearchPreviewViewController,
                 deployment_view_controller: ImageDeploymentListViewController):
        super().__init__()
        
        self._asset_provider = app_dependency_provider.asset_provider
        self._observation_tower = app_dependency_provider.observation_tower
        self._platform_service_provider = app_dependency_provider.platform_service_provider
        self._image_resource_deployer = app_dependency_provider.image_resource_deployer

        horizontal_layout = QHBoxLayout()
        self.setLayout(horizontal_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        horizontal_layout.addWidget(splitter)
        
        self.card_search_view = card_search_preview_view_controller
        
        splitter.addWidget(self.card_search_view)

        
        self.deployment_view = deployment_view_controller
        
        splitter.addWidget(deployment_view_controller)
        splitter.setSizes([450,900])
        splitter.setStretchFactor(0, 0) # prevent search pane from stretching
        splitter.setStretchFactor(1, 1) # allow deployment list to stretch

        app_dependency_provider.image_resource_deployer.load_production_resources()
