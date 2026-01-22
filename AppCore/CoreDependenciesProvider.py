import atexit
from typing import Optional

from AppCore.Config import ConfigurationManager
from AppCore.DataSource import (
    CustomDirectorySearchDataSource,
    CustomDirectorySearchDataSourceDelegate,
    DataSourceCachedHistory,
    DataSourceDraftListWindowResourceDeployer,
    DataSourceEventCoordinator,
    DataSourceRecentPublished,
)

from AppCore.DataSource.ImageResourceDeployer import DataSourceImageResourceDeployerProvider, DataSourceImageResourceDeployerProtocol
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch,
    DataSourceCardSearchClientProviding,
    DataSourceCardSearchDelegate,
)
from AppCore.DataSource.DraftList import (
    DataSourceDraftListProvider,
    DataSourceDraftListProviding,
)
from AppCore.ImageFetcher import ImageFetcherProvider
from AppCore.ImageResource import (
    ImageResourceProcessor,
    ImageResourceProcessorProviding,
)
from AppCore.Models import ModelTransformer
from AppCore.Observation.Events import ApplicationEvent
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Service import DataSerializer, PlatformServiceProvider, StringFormatter
from AppCore.Service.WebSocket import WebSocketService, WebSocketServiceProtocol

from .CoreDependenciesInternalProviding import CoreDependenciesInternalProviding
from .CoreDependenciesProviding import CoreDependenciesProviding


class CoreDependenciesProvider(CoreDependenciesProviding, CoreDependenciesInternalProviding):
    def __init__(self,
                 observation_tower: ObservationTower,
                 configuration_manager: ConfigurationManager,
                 model_transformer: ModelTransformer):
        self._observation_tower = observation_tower
        self._model_transformer = model_transformer
        self._string_formatter = StringFormatter()
        self._data_serializer = DataSerializer()

        self._configuration_manager = configuration_manager

        self._websocket_service = WebSocketService(self._observation_tower)

        self._platform_service_provider = PlatformServiceProvider(self._configuration_manager,
                                                                  self._observation_tower)

        self._image_resource_processor_provider = ImageResourceProcessor(ImageFetcherProvider(self._configuration_manager),
                                                                         self.observation_tower)

        self._data_source_image_resource_deployer_provider = DataSourceImageResourceDeployerProvider(self._configuration_manager,
                                                                                                     self._observation_tower,
                                                                                                     self._image_resource_processor_provider, 
                                                                                                     self._websocket_service)

        self._data_source_draft_list_provider = DataSourceDraftListProvider(self._configuration_manager,
                                                                            self._observation_tower,
                                                                            self._data_serializer)

        self._data_source_recent_published = DataSourceRecentPublished(self._observation_tower,
                                                                       self._image_resource_processor_provider,
                                                                       self._configuration_manager,
                                                                       self._data_serializer)

        self._data_source_draft_list_window_resource_deployer = DataSourceDraftListWindowResourceDeployer(self._configuration_manager,
                                                                                                          self._observation_tower,
                                                                                                          self._data_source_draft_list_provider,
                                                                                                          self._data_serializer)

        self._data_source_event_coordinator = DataSourceEventCoordinator(self._observation_tower,
                                                                         self._configuration_manager,
                                                                         self._data_source_image_resource_deployer_provider)

        atexit.register(self._cleanup)

    @property
    def model_transformer(self) -> ModelTransformer:
        return self._model_transformer

    @property
    def image_resource_processor_provider(self) -> ImageResourceProcessorProviding:
        return self._image_resource_processor_provider

    @property
    def data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
        return self._data_source_image_resource_deployer_provider.data_source_image_resource_deployer

    @property
    def observation_tower(self) -> ObservationTower:
        return self._observation_tower

    @property
    def configuration_manager(self) -> ConfigurationManager:
        return self._configuration_manager

    @property
    def platform_service_provider(self) -> PlatformServiceProvider:
        return self._platform_service_provider

    @property
    def data_serializer(self) -> DataSerializer:
        return self._data_serializer

    @property
    def string_formatter(self) -> StringFormatter:
        return self._string_formatter

    def new_instance_card_search_data_source(self,
                                             delegate: DataSourceCardSearchDelegate,
                                             search_client_provider: DataSourceCardSearchClientProviding,
                                             ds_configuration: Optional[DataSourceCardSearch.DataSourceCardSearchConfiguration] = None) -> DataSourceCardSearch:
        ds = DataSourceCardSearch(self,
                                  search_client_provider,
                                  ds_configuration)
        ds.delegate = delegate
        return ds

    def new_instance_custom_directory_search_data_source(self,
                                                         delegate: CustomDirectorySearchDataSourceDelegate) -> CustomDirectorySearchDataSource:
        ds = CustomDirectorySearchDataSource(self)
        ds.delegate = delegate
        return ds

    @property
    # TODO: remove providing protocol from being exposed
    def data_source_draft_list_provider(self) -> DataSourceDraftListProviding:
        return self._data_source_draft_list_provider

    @property
    def data_source_recent_published(self) -> DataSourceCachedHistory:
        return self._data_source_recent_published

    @property
    def data_source_draft_list_window_resource_deployer(self) -> DataSourceDraftListWindowResourceDeployer:
        return self._data_source_draft_list_window_resource_deployer

    @property
    def websocket_service(self) -> WebSocketServiceProtocol:
        return self._websocket_service

    def _cleanup(self):
        print("Performing cleanup before exit...")
        self._observation_tower.notify(ApplicationEvent(
            ApplicationEvent.EventType.APP_WILL_TERMINATE))
