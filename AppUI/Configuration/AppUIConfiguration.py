
import copy

from AppCore.Config import ConfigurationManager, MutableConfiguration
from AppUI.Models import DraftListStyleSheet


class AppUIConfiguration:
    
    def __init__(self, configuration: MutableConfiguration):
        super().__init__()
        self._configuration = configuration
        draft_styles_json = configuration.configuration_for_key(self.Keys.DRAFT_LIST_STYLES)
        if draft_styles_json is not None:
            self._draft_list_stylesheet = DraftListStyleSheet.from_json(draft_styles_json)
    
    class Keys:
        DRAFT_LIST_STYLES = 'draft_list_styles'
        
    @property
    def draft_list_styles(self) -> DraftListStyleSheet:
        return self._draft_list_stylesheet
    
    @property
    def configuration(self) -> MutableConfiguration:
        return self._configuration
    
class MutableAppUIConfiguration(AppUIConfiguration):
    def set_draft_list_styles(self, value: DraftListStyleSheet):
        self._configuration.set_configuration_for_key(self.Keys.DRAFT_LIST_STYLES, value.to_data())
        

class AppUIConfigurationManager:
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager
    
    @property
    def configuration(self) -> AppUIConfiguration:
        return self.mutable_configuration()
    
    def mutable_configuration(self) -> MutableAppUIConfiguration:
        return MutableAppUIConfiguration(copy.deepcopy(self._configuration_manager.mutable_configuration()))
    
    def save_configuration(self, new_configuration: MutableAppUIConfiguration):
        print('saving app UI configuration')
        self._configuration_manager.save_configuration(new_configuration.configuration)