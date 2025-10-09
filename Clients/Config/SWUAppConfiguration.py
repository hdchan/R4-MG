
import copy
from enum import Enum
from AppCore.Config import (Configuration, ConfigurationManager,
                            MutableConfiguration)
from ..Models.DeckListImageGeneratorStyles import DeckListImageGeneratorStyles


class SWUAppConfiguration():
    
    def __init__(self, configuration: MutableConfiguration):
        super().__init__()
        self._configuration = configuration

    class SearchSource(int, Enum):
            SWUDBAPI = 0
            LOCAL = 1 # NOTE: keep but dont reuse
            STARWARSUNLIMITED_FFG = 2
            LOCALLY_MANAGED_DECKS = 3
            DEFAULT = SWUDBAPI
        
    class Keys:
        DECK_LIST_IMAGE_GENERATOR_STYLES = 'deck_list_image_generator_styles'
        SEARCH_SOURCE = 'search_source'
    
    @property
    def core_configuration(self) -> Configuration:
        return self._configuration
    
    @property
    def core_mutable_configuration(self) -> MutableConfiguration:
        return self._configuration
    
    @property
    def deck_list_image_generator_styles(self) -> DeckListImageGeneratorStyles:
        styles_json = self._configuration.configuration_for_key(self.Keys.DECK_LIST_IMAGE_GENERATOR_STYLES)
        if styles_json is not None:
            return DeckListImageGeneratorStyles.from_json(styles_json)
        return DeckListImageGeneratorStyles.default_style()
    
    @property 
    def search_source(self) -> SearchSource:
        result = self._configuration.configuration_for_key(self.Keys.SEARCH_SOURCE)
        if result is None:
            return self.SearchSource.DEFAULT
        return result
    

class MutableSWUConfiguration(SWUAppConfiguration):
    def set_deck_list_image_generator_styles(self, value: DeckListImageGeneratorStyles):
        self._configuration.set_configuration_for_key(self.Keys.DECK_LIST_IMAGE_GENERATOR_STYLES, value.to_data())

    def set_search_source(self, source: Configuration.Settings.SearchSource):
        self._configuration.set_configuration_for_key(self.Keys.SEARCH_SOURCE, source.value)

class SWUAppConfigurationManager:
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self._configuration_manager = configuration_manager
    
    @property
    def configuration(self) -> SWUAppConfiguration:
        return self.mutable_configuration()
    
    def mutable_configuration(self) -> MutableSWUConfiguration:
        return MutableSWUConfiguration(copy.deepcopy(self._configuration_manager.mutable_configuration()))
    
    def save_configuration(self, new_configuration: MutableSWUConfiguration):
        print('saving app SWUApp configuration')
        self._configuration_manager.save_configuration(new_configuration.core_mutable_configuration)

    # does this save any work?
    def save_deck_list_image_generator_styles(self, deck_list_styles: DeckListImageGeneratorStyles):
        mutable_configuration = self.mutable_configuration()
        mutable_configuration.set_deck_list_image_generator_styles(deck_list_styles)
        self.save_configuration(mutable_configuration)