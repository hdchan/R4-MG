from AppCore.Config import ConfigurationManager
from AppCore.ImageResource.ImageResourceProcessorProvider import \
    ImageResourceProcessorProviding
from AppCore.Models import ModelTransformer, CardResourceProvider
from AppCore.Observation import (ObservationTower, TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import SocketIOReceivedCardEvent
from AppCore.Service import DataSerializer

from .DataSourceCachedHistory import DataSourceCachedHistory


class DataSourceSocketIOHistory(DataSourceCachedHistory, TransmissionReceiverProtocol):
    def __init__(self, 
                 model_transformer: ModelTransformer,
                 observation_tower: ObservationTower, 
                 image_resource_processor_provider: ImageResourceProcessorProviding, 
                 configuration_manager: ConfigurationManager, 
                 data_serializer: DataSerializer):
        self._model_transformer = model_transformer
        self._configuration_manager = configuration_manager
        configuration = DataSourceCachedHistory.DataSourceCachedHistoryConfiguration(cache_history_identifier="socket_io_history")
        super().__init__(observation_tower, 
                         image_resource_processor_provider, 
                         configuration_manager, 
                         data_serializer, 
                         configuration)
        self._observation_tower.subscribe(self, SocketIOReceivedCardEvent)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is SocketIOReceivedCardEvent:
            json = event.data['data']
            trading_card = self._model_transformer.transform_json_to_trading_card(json)
            if trading_card is not None:
                resource_provider = CardResourceProvider(trading_card, self._configuration_manager)
                self.add_resource(resource_provider.local_resource)
                self.save_data()