from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QSplitter
from PyQt5 import QtCore
from AppCore import ApplicationCore, ObservationTower
from AppCore.Observation import TransmissionReceiver, TransmissionProtocol
from AppCore.Observation.Events import ProductionResourcesLoadedEvent
# from UIComponents.Base import ImagePreviewViewController
class TwoStackImagePreviewViewController(QWidget):
    def __init__(self):
        layout = QVBoxLayout()
        super().__init__()
        self.setLayout(layout)
        
        top = QWidget()
        top.setStyleSheet("background-color: green")
        layout.addWidget(top)
        
        bottom = QWidget()
        bottom.setStyleSheet("background-color: red")
        layout.addWidget(bottom)
class ProfileDeploymentViewController(QWidget):
    
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        label = QLabel()
        label.setText("Player")
        layout.addWidget(label)
        
        staging_stack = TwoStackImagePreviewViewController()
        layout.addWidget(staging_stack)
        production_stack = TwoStackImagePreviewViewController()
        layout.addWidget(production_stack)
class AdvancedViewController(QWidget, TransmissionReceiver):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 application_core: ApplicationCore):
        super().__init__()
        
        h_layout = QHBoxLayout()
        self.setLayout(h_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        h_layout.addWidget(splitter)
        
        
        search_panel = QWidget()
        search_panel_layout = QVBoxLayout()
        search_panel.setLayout(search_panel_layout)
        
        base_image = QWidget()
        base_image.setStyleSheet("background-color: green")
        
        leader_image = QWidget()
        leader_image.setStyleSheet("background-color: red")
        
        search_panel_layout.addWidget(base_image)
        search_panel_layout.addWidget(leader_image)
        
        result_list = QListWidget()
        # result_list.itemSelectionChanged.connect(self.get_selection)
        self.result_list = result_list
        search_panel_layout.addWidget(result_list)
        
        result_list.addItem("stuff")
        
        splitter.addWidget(search_panel)
        
        
        player_slot_panel = QWidget()
        player_slot_layout = QVBoxLayout()
        player_slot_panel.setLayout(player_slot_layout)
        
        player_slot_layout.addWidget(ProfileDeploymentViewController())
        player_slot_layout.addWidget(ProfileDeploymentViewController())
        splitter.addWidget(player_slot_panel)
        
        observation_tower.subscribe(self, ProductionResourcesLoadedEvent)
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ProductionResourcesLoadedEvent:
            print(event.production_resources)