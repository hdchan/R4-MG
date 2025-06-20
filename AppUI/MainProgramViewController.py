from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QWidget

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController)


class MainProgramViewController(QWidget):
    def __init__(self,
                 app_dependency_provider: AppDependenciesProviding,
                 card_search_preview_view_controller: CardSearchPreviewViewController,
                 deployment_view_controller: ImageDeploymentListViewController):
        super().__init__()

        horizontal_layout = QHBoxLayout()
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
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
