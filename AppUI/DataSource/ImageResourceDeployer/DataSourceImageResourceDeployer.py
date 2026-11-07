import os
import shutil
from copy import deepcopy
from pathlib import Path
from typing import List, Optional

from PIL import Image

from AppCore.Config import Configuration, ConfigurationManager
from AppCore.ImageResourceProcessor.Events import LocalCardResourceFetchEvent
from AppCore.ImageResourceProcessor.ImageResourceProcessorProtocol import (
    ImageResourceProcessorProtocol,
    ImageResourceProcessorProviding,
)
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation import (
    ObservationTower,
    TransmissionProtocol,
    TransmissionReceiverProtocol,
)
from AppCore.Service.WebSocket.WebSocketServiceProtocol import WebSocketServiceProtocol

from .DataSourceImageResourceDeployerProtocol import (
    DataSourceImageResourceDeployerProtocol,
)
from .Events import (
    DataSourceImageResourceDeployerStateUpdatedEvent,
    # PublishStagedCardResourcesEvent,
    ProductionCardResourcesLoadEvent
)
from .DataSourceRecentPublished import DataSourceRecentPublished
import io
PNG_EXTENSION = 'png'


class ProductionLocalCardResource(LocalCardResource, TransmissionReceiverProtocol):
    def __init__(self,
                 image_dir: str,
                 image_preview_dir: str,
                 file_name: str,
                 display_name: str,
                 display_name_short: str,
                 display_name_detailed: str):
        super().__init__(image_dir=image_dir,
                         image_preview_dir=image_preview_dir,
                         file_name=file_name,
                         display_name=display_name,
                         display_name_short=display_name_short,
                         display_name_detailed=display_name_detailed,
                         can_generate_placeholder=True)


class DataSourceImageResourceDeployer(DataSourceImageResourceDeployerProtocol, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 image_resource_processor_provider: ImageResourceProcessorProviding,
                 websocket_service: WebSocketServiceProtocol, 
                 data_source_recent_published: DataSourceRecentPublished):
        self._observation_tower = observation_tower
        self._websocket_service = websocket_service
        self._configuration_manager = configuration_manager
        self._image_resource_processor_provider = image_resource_processor_provider
        self._data_source_recent_published = data_source_recent_published
        self._deployment_resources: List[DeploymentCardResource] = []
        self._is_publishing = False
        self._can_publish_staged_resources = False

        self._observation_tower.subscribe(self, LocalCardResourceFetchEvent)

    @property
    def deployment_resources(self) -> List[DeploymentCardResource]:
        return self._deployment_resources

    def deployment_resource_for_file_name(self, file_name: str) -> Optional[DeploymentCardResource]:
        results = list(filter(lambda x: x.production_resource.file_name_with_ext ==
                       file_name, self.deployment_resources))
        if len(results) == 0:
            return None
        return results[0]

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _image_resource_processor(self) -> ImageResourceProcessorProtocol:
        return self._image_resource_processor_provider.image_resource_processor

    def attach_preview_binary_to_prod_resources(self) -> None:
        for r in self._deployment_resources:
            staging_resource = r.staged_resource
            if staging_resource:
                if staging_resource.is_preview_ready and staging_resource.is_ready:
                    with Image.open(staging_resource.image_preview_path) as img:
                        buffer = io.BytesIO()
                        img.save(buffer, format="WEBP", quality=80)
                        webp_data = buffer.getvalue()
                        staging_resource.set_image_preview_binary(webp_data)
                else:
                    staging_resource.set_image_preview_binary(None)

            prod_resource = r.production_resource
            # should have previews at this point...
            if prod_resource.is_preview_ready:
                with Image.open(prod_resource.image_preview_path) as img:
                    buffer = io.BytesIO()
                    img.save(buffer, format="WEBP", quality=80)
                    webp_data = buffer.getvalue()
                    prod_resource.set_image_preview_binary(webp_data)
            else:
                prod_resource.set_image_preview_binary(None)

    def load_production_resources(self):
        """
        Will load images from production folder
        """

        start_load_event = ProductionCardResourcesLoadEvent(
            ProductionCardResourcesLoadEvent.EventType.STARTED)
        self._observation_tower.notify(start_load_event)

        self._generate_directories_if_needed()
        deployment_resources: List[DeploymentCardResource] = []
        file_list = os.listdir(self._configuration.production_dir_path)

        for production_file_name_with_ext in file_list[:]:
            path = Path(production_file_name_with_ext)
            if path.suffix == f'.{PNG_EXTENSION}':
                resource = ProductionLocalCardResource(image_dir=self._configuration.production_dir_path,
                                                       image_preview_dir=self._configuration.production_preview_dir_path,
                                                       file_name=path.stem,
                                                       display_name=path.stem + path.suffix,
                                                       display_name_short=path.stem + path.suffix,
                                                       display_name_detailed=path.stem + path.suffix)

                staged_resource = DeploymentCardResource(resource)
                deployment_resources.append(staged_resource)

                if not resource.is_preview_ready:
                    self._image_resource_processor.regenerate_resource_preview(
                        resource)

        # Maintains any existing staged resources when loading, removes any deleted prod files, and appends new prod files
        latest_prod_resources = list(
            map(lambda x: x.production_resource, deployment_resources))
        maintain_existing = list(filter(
            lambda x: x.production_resource in latest_prod_resources, self._deployment_resources))
        mapped_existing_prod_resources = list(
            map(lambda x: x.production_resource, maintain_existing))
        new_additions = list(filter(
            lambda x: x.production_resource not in mapped_existing_prod_resources, deployment_resources))

        self._deployment_resources = maintain_existing + new_additions

        if self._configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.FILE_NAME:
            self._deployment_resources.sort(
                key=lambda x: x.production_resource.file_name.lower(), reverse=self._configuration.deployment_list_sort_is_desc_order)
        elif self._configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE:
            self._deployment_resources.sort(key=lambda x: x.production_resource.created_date,
                                            reverse=self._configuration.deployment_list_sort_is_desc_order)

        finish_load_event = ProductionCardResourcesLoadEvent(
            ProductionCardResourcesLoadEvent.EventType.FINISHED)
        finish_load_event.predecessor = start_load_event
        self._observation_tower.notify(finish_load_event)
        self._notify_state_changed()

    def latest_deployment_resource(self, deployment_resource: DeploymentCardResource) -> Optional[DeploymentCardResource]:
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                return r
        return None

    def stage_resource(self, deployment_resource: DeploymentCardResource, selected_resource: LocalCardResource):
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                r.stage(selected_resource)
        self._notify_state_changed()

    def unstage_resource(self, deployment_resource: DeploymentCardResource):
        self._unstage_resource(deployment_resource)
        self._notify_state_changed()

    def unstage_all_resources(self):
        self._unstage_all_resources()
        self._notify_state_changed()
    
    # prevent unecessary observation calls for internal usage
    def _unstage_resource(self, deployment_resource: DeploymentCardResource):
        for r in self._deployment_resources:
            if r.production_resource == deployment_resource.production_resource:
                r.clear_staged_resource()

    def _unstage_all_resources(self):
        for r in self._deployment_resources:
            self._unstage_resource(r)

    @property
    def is_publishing(self) -> bool:
        return self._is_publishing

    @property
    def can_publish_staged_resources(self) -> bool:
        return self._can_publish_staged_resources
        
    def _update_can_publish_staged_resources(self):
        if len(self._deployment_resources) <= 0:
            self._can_publish_staged_resources = False
            return

        staged_resources = list(map(lambda x: x.staged_resource, self._deployment_resources))
        valid_staged_resources = list(filter(None, staged_resources))
        if len(valid_staged_resources) <= 0:
            self._can_publish_staged_resources = False
            return

        result = True
        for i in self._deployment_resources:
            if not i.can_publish_staged_resource:
                result = False
                break
        
        self._can_publish_staged_resources = result and len(self._deployment_resources) > 0 and len(valid_staged_resources) > 0

    def publish_staged_resources(self):
        """
        Publishes staged resources. Returns True if success.
        Otherwise returns false.
        """

        self._is_publishing = True
        self._notify_state_changed()

        deployment_resources_copy = deepcopy(self._deployment_resources)
        # initial_event = PublishStagedCardResourcesEvent(
        #     PublishStagedCardResourcesEvent.EventType.STARTED, deployment_resources_copy)
        # self._observation_tower.notify(initial_event)
        try:
            if self.can_publish_staged_resources:  # don't publish resources if one does not work
                self._generate_directories_if_needed()
                for r in self._deployment_resources:
                    if r.staged_resource is not None:
                        # TODO: continue published if exception, and notify about exceptions
                        production_dir_path = f'{self._configuration.production_dir_path}{r.production_resource.file_name_with_ext}'
                        production_preview_dir_path = f'{self._configuration.production_preview_dir_path}{r.production_resource.file_name_with_ext}'
                        # Resize if needed
                        if self._configuration.resize_prod_images and not r.staged_resource.is_local_only:
                            # Don't resize local only resources, assume that these are custom assets
                            assert (not r.staged_resource.is_local_only)
                            # TODO: with open close
                            cached_image = Image.open(
                                r.staged_resource.image_path)
                            downscaled_image = self._image_resource_processor.down_scale_image(
                                cached_image, self._configuration.resize_prod_images_max_size)
                            downscaled_image.save(production_dir_path)
                        else:
                            shutil.copy(r.staged_resource.image_path,
                                        production_dir_path)
                        try:
                            # raises exception can ignore
                            shutil.copy(
                                r.staged_resource.image_preview_path, production_preview_dir_path)
                        except Exception:
                            # remove previous preview file
                            Path(production_preview_dir_path).unlink()
                            # gets regenerated from reload
                            # do nothing because preview file is not critical, or maybe can regenerate file

                

                self._unstage_all_resources()
                # finished_event = PublishStagedCardResourcesEvent(
                #     PublishStagedCardResourcesEvent.EventType.FINISHED, deployment_resources_copy)
                # finished_event.predecessor = initial_event
                # self._observation_tower.notify(finished_event)

                self._is_publishing = False
                self._notify_state_changed()

                self._data_source_recent_published.save_published_resources(deployment_resources_copy)

                # NOTE: background thread causing crash when spamming publish from draft list, may need to add state for process of publishing
            else:
                self._is_publishing = False
                self._notify_state_changed()
                raise Exception(
                    "Failed to publish. Please redownload resources and retry.")

        except Exception as error:
            self._is_publishing = False
            self._notify_state_changed()
            raise Exception(error)

    def generate_new_file(self, file_name: str, placeholder_image_path: Optional[str]):
        local_resource = ProductionLocalCardResource(image_dir=self._configuration.production_dir_path,
                                                     image_preview_dir=self._configuration.production_preview_dir_path,
                                                     file_name=file_name,
                                                     display_name=file_name,
                                                     display_name_short=file_name,
                                                     display_name_detailed=file_name)
        self._image_resource_processor.generate_placeholder(
            local_resource, placeholder_image_path)

    def _notify_state_changed(self):
        # update state before notifying
        self._update_can_publish_staged_resources()
        self._observation_tower.notify(
            DataSourceImageResourceDeployerStateUpdatedEvent())

    def _generate_directories_if_needed(self):
        Path(self._configuration.production_preview_dir_path).mkdir(
            parents=True, exist_ok=True)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is LocalCardResourceFetchEvent:
            # event_type = event.event_type
            # if event_type == LocalCardResourceFetchEvent.EventType.FINISHED:
            staged_resources = list(map(lambda x: x.staged_resource, self._deployment_resources))
            valid_staged_resources = list(filter(None, staged_resources))
            if event.local_resource in valid_staged_resources:
                self._notify_state_changed()
