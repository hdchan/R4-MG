from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from AppCore.Config import ConfigurationProviderProtocol
from AppCore.Observation import *
from AppCore.Observation.Events import ConfigurationUpdatedEvent


class ContainerViewController(QWidget, TransmissionReceiverProtocol):
    
    def __init__(self, 
                 basic_view: QWidget, 
                 advanced_view: QWidget, 
                 configuration_provider: ConfigurationProviderProtocol, 
                 observation_tower: ObservationTower):
        
        
        super().__init__()
        self.basic_view = basic_view
        self.advanced_view = advanced_view
        self.configuration_provider = configuration_provider
        self.current_widget = None
        self.view_layout = QVBoxLayout()
        self.setLayout(self.view_layout)
        
        self._load_view()
        
        observation_tower.subscribe(self, ConfigurationUpdatedEvent)
        
    def _load_view(self):
        if self.current_widget != None:
            self.view_layout.removeWidget(self.current_widget)
        
        if self.configuration_provider.configuration.is_developer_mode:
            self.tabs = QTabWidget()
            self.tabs.resize(300, 200)
            
            self.tabs.addTab(self.basic_view, "Basic")
            self.tabs.addTab(self.advanced_view, "Advanced")
            
            self.view_layout.addWidget(self.tabs)
            self.current_widget = self.tabs
            
        else:
            self.view_layout.addWidget(self.basic_view)
            self.current_widget = self.basic_view            

        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            pass