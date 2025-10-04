
import copy
from typing import Optional, Dict

from AppCore.Config import (Configuration, ConfigurationManager,
                            MutableConfiguration)
from AppUI.Models import DraftListStyleSheet, WindowDimensions


class AppUIConfiguration():
    
    def __init__(self, configuration: MutableConfiguration):
        super().__init__()
        self._configuration = configuration
        
    class Keys:
        DRAFT_LIST_STYLES = 'draft_list_styles'
        WINDOW_DIMENSIONS = 'window_dimensions'
    
    @property
    def core_configuration(self) -> Configuration:
        return self._configuration
    
    @property
    def core_mutable_configuration(self) -> MutableConfiguration:
        return self._configuration
    
    @property
    def draft_list_styles(self) -> DraftListStyleSheet:
        draft_styles_json = self._configuration.configuration_for_key(self.Keys.DRAFT_LIST_STYLES)
        if draft_styles_json is not None:
            return DraftListStyleSheet.from_json(draft_styles_json)
        return DraftListStyleSheet.default_style()
    
    @property
    def window_dimensions(self) -> WindowDimensions:
        json = self._configuration.configuration_for_key(self.Keys.WINDOW_DIMENSIONS)
        if json is not None:
            return WindowDimensions.from_json(json)
        return WindowDimensions.default()
    
class MutableAppUIConfiguration(AppUIConfiguration):
    def set_draft_list_styles(self, value: DraftListStyleSheet):
        self._configuration.set_configuration_for_key(self.Keys.DRAFT_LIST_STYLES, value.to_data())
        
    def set_window_dimensions(self, value: WindowDimensions):
        self._configuration.set_configuration_for_key(self.Keys.WINDOW_DIMENSIONS, value.to_data())

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
        self._configuration_manager.save_configuration(new_configuration.core_mutable_configuration)