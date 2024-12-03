from AppUI.UIComponents import ImagePopoutViewController
from typing import Dict
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Config import ConfigurationProviderProtocol
import gc

class PopoutImageManager:
    def __init__(self, 
                 obseration_tower: ObservationTower, 
                 configuration_provider: ConfigurationProviderProtocol):
        self.observation_tower = obseration_tower
        self.configuration_provider = configuration_provider
        self.popouts: Dict[str, object] = {}
        
    def spawn_for_resource(self, resource: LocalCardResource):
        if resource.file_name in self.popouts:
            test = gc.get_referrers(self.popouts[resource.file_name])
            self.popouts[resource.file_name].close()
            del self.popouts[resource.file_name]
            return
        spawn = ImagePopoutViewController(self.observation_tower,
                                          self.configuration_provider)
        self.popouts[resource.file_name] = spawn
        spawn.setup(resource)
        spawn.show()