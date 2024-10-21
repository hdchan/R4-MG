import copy
from typing import List, Optional

from AppCore.Models.SearchConfiguration import SearchConfiguration

from .CardSearchFlow import CardSearchFlow, CardSearchFlowDelegate
from .Data import APIClientProvider
from .Image import (ImageFetcherProvider, ImageResourceDeployer,
                    ImageResourceDeployerDelegate)
from .Observation import ObservationTower
from .Observation.Events import *
from .CardMetadataFlow import CardMetadataFlow

class ApplicationCoreDelegate:
    def app_did_complete_search(self, app_core: ..., display_name_list: List[str], error: Optional[Exception]) -> None:
        pass
    
    def app_did_retrieve_card_resource_for_card_selection(self, app_core: ..., local_resource: LocalCardResource, is_flippable: bool) -> None:
        pass
    
    def app_publish_status_changed(self, app_core: ..., can_publish: bool) -> None:
        pass
    
    def app_did_load_production_resources(self, app_core: ..., local_resource: List[LocalCardResource]) -> None:
        pass
    
    def app_did_update_search_configuration(self, app_core: ..., search_configuration: SearchConfiguration) -> None:
        pass

class ApplicationCore(CardSearchFlowDelegate, ImageResourceDeployerDelegate):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 api_client_provider: APIClientProvider,
                 image_fetcher_provider: ImageFetcherProvider, 
                 configuration: Configuration):
        self._card_search_flow = CardSearchFlow(observation_tower, 
                                                api_client_provider, 
                                                image_fetcher_provider, 
                                                configuration)
        self._card_search_flow.delegate = self
        
        self._resource_deployer = ImageResourceDeployer(configuration)
        self._resource_deployer.delegate = self
        
        self._card_metadata_flow = CardMetadataFlow(self._card_search_flow, 
                                                    self._resource_deployer)
        self._card_metadata_flow.delegate = self
        
        self._observation_tower = observation_tower
        self.delegate: Optional[ApplicationCoreDelegate] = None
        
    @property
    def card_search_flow(self) -> CardSearchFlow:
        return self._card_search_flow

    @property
    def card_metadata_flow(self) -> CardMetadataFlow:
        return self._card_metadata_flow

    @property
    def resource_deployer(self) -> ImageResourceDeployer:
        return self._resource_deployer
    
    # MARK: - DS Delegate methods
    def sf_did_complete_search(self, sf: CardSearchFlow, result_list: List[str], error: Optional[Exception]):
        if self.delegate is not None:
            self.delegate.app_did_complete_search(self, result_list, error)

    def sf_did_retrieve_card_resource_for_card_selection(self, sf: CardSearchFlow, local_resource: LocalCardResource, is_flippable: bool):
        if self.delegate is not None:
            self.delegate.app_did_retrieve_card_resource_for_card_selection(self, copy.deepcopy(local_resource), is_flippable)

    def sf_did_update_search_configuration(self, sf: CardSearchFlow, search_configuration: SearchConfiguration):
        if self.delegate is not None:
            self.delegate.app_did_update_search_configuration(self, search_configuration)

    # MARK: - Resource Cacher Delegate
    def sf_did_finish_storing_local_resource(self, sf: CardSearchFlow, local_resource: LocalCardResource):
        self._retrieve_publish_status_and_notify_if_needed()

    def _retrieve_publish_status_and_notify_if_needed(self):
        publish_status = self._resource_deployer.can_publish_staged_resources()
        if self.delegate is not None:
            self.delegate.app_publish_status_changed(self, publish_status)
    


    # MARK: - Resource manager
    def can_stage_current_card_search_resource_to_stage_index(self, index: int) -> bool:
        return self._card_search_flow.current_card_search_resource is not None and index < len(self._resource_deployer.production_resources)

    def stage_resource(self, index: int):
        if self._card_search_flow.current_card_search_resource is not None:
            self._resource_deployer.stage_resource(self._card_search_flow.current_card_search_resource, index)
            self._retrieve_publish_status_and_notify_if_needed()

    def unstage_resource(self, index: int):
        self._resource_deployer.unstage_resource(index)
        self._retrieve_publish_status_and_notify_if_needed()

    def unstage_all_resources(self):
        self._resource_deployer.unstage_all_resources()
        self._retrieve_publish_status_and_notify_if_needed()

    def load_production_resources(self):
        self._resource_deployer.load_production_resources()

    def can_publish_staged_resources(self) -> bool:
        return self._resource_deployer.can_publish_staged_resources()

    def publish_staged_resources(self) -> bool:
        return self._resource_deployer.publish_staged_resources()
    
    # MARK: - Resource Deployer Delegate methods
    def rd_did_load_production_resources(self, rd: ImageResourceDeployer, local_resources: List[LocalCardResource]):
        if self.delegate is not None:
            self.delegate.app_did_load_production_resources(self, copy.deepcopy(local_resources))