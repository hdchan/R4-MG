from AppCore.Config import ConfigurationManager
from AppCore.Models.LocalCardResource import LocalCardResource
from typing import List

class WebSocketModelLocalizer():
    def __init__(self, configuration_manager: ConfigurationManager):
        self._configuration_manager = configuration_manager

    def localize_local_card_resource(self, local_resource: LocalCardResource) -> LocalCardResource:
        def _image_path() -> str:
            return f'{self._configuration_manager.configuration.cache_card_search_dir_path}{local_resource.trading_card.image_source_domain}/'

        def _image_preview_dir() -> str:
            return f'{self._configuration_manager.configuration.cache_card_search_preview_dir_path}{local_resource.trading_card.image_source_domain}/'

        return LocalCardResource(image_dir=_image_path(),
                                 image_preview_dir=_image_preview_dir(),
                                 file_name=local_resource.file_name,
                                 display_name=local_resource.display_name,
                                 display_name_short=local_resource.display_name_short,
                                 display_name_detailed=local_resource.display_name_detailed,
                                 remote_image_url=local_resource.remote_image_url,
                                 trading_card=local_resource.trading_card)

    def localize_local_card_resource_list(self, local_resource_list: List[LocalCardResource]) -> List[LocalCardResource]:
        return list(map(lambda x: self.localize_local_card_resource(x), local_resource_list))