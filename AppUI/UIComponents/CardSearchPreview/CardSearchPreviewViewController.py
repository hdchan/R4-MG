from typing import Optional

from PySide6.QtWidgets import QSizePolicy

from AppCore.Models import (
    DataSourceSelectedLocalCardResourceProtocol,
    LocalCardResource,
    LocalResourceDataSourceProviding,
)
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.UIComponents.ImagePreview import ImagePreviewLocalResourceDataSourceDecorator
from R4UI import HorizontalBoxLayout, RTabWidget, RWidget, VerticalBoxLayout


class CardSearchPreviewViewControllerDelegate:
    @property
    def csp_is_tab_visible(self, index: int) -> bool:
        return True

    @property
    def csp_tab_count(self) -> int:
        return 1

    def csp_local_resource_providing_vc(self, index: int) -> LocalResourceDataSourceProviding:
        raise Exception

    def csp_tab_name(self, index: int) -> str:
        return f'Card Search Preview Source {index + 1}'

    @property
    def csp_is_vertical_orientation(self) -> bool:
        return True


class CardSearchPreviewViewController(RWidget, TransmissionReceiverProtocol, LocalResourceDataSourceProviding):

    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 delegate: CardSearchPreviewViewControllerDelegate):
        super().__init__()
        self._observation_tower = app_dependencies_provider.observation_tower
        self._shortcut_action_coordinator = app_dependencies_provider.shortcut_action_coordinator
        self._image_preview_view = ImagePreviewLocalResourceDataSourceDecorator(
            app_dependencies_provider)
        self._delegate = delegate
        self._tab_widget = None
        # https://stackoverflow.com/a/19011496
        # image_preview_view.setMinimumHeight(360)
        self._image_preview_view.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._observation_tower.subscribe_multi(
            self, [WebSocketStatusUpdatedEvent])

        self._setup_view()

    def _setup_view(self):

        self._tab_widget_container = VerticalBoxLayout().set_uniform_content_margins(0)

        if self._delegate.csp_is_vertical_orientation:
            self._box_layout = VerticalBoxLayout([
                self._image_preview_view,
                self._tab_widget_container
            ])
        else:
            # self._tab_widget_container.setMinimumWidth(400)
            # self._image_preview_view.setMinimumWidth(270)
            self._box_layout = HorizontalBoxLayout([
                self._tab_widget_container,
                self._image_preview_view
            ])

        self._box_layout.set_layout_to_widget(
            self).set_uniform_content_margins(0)

        tab_count = self._delegate.csp_tab_count
        if tab_count > 1:
            self._tab_widget = RTabWidget([], self.on_tab_changed)

            for i in range(self._delegate.csp_tab_count):
                self._tab_widget.add_tabs([
                    (self._delegate.csp_local_resource_providing_vc(i),
                     self._delegate.csp_tab_name(i))  # type: ignore
                ])
            self._tab_widget_container.replace_all_widgets([self._tab_widget])
        else:
            _tab_widget = self._delegate.csp_local_resource_providing_vc(
                0)

            self._tab_widget_container.replace_all_widgets([_tab_widget])

    def _sync_ui(self):
        if self._tab_widget is not None:
            self._tab_widget.update_tab_visibility(
                self._delegate.csp_is_tab_visible)

    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self._image_preview_view

    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._image_preview_view.selected_local_resource

    def set_retrieved_resource_from_vc(self, index: int = 0):
        selected_resource = self._delegate.csp_local_resource_providing_vc(
            index).data_source.selected_local_resource
        if selected_resource is None:
            return
        self._image_preview_view.set_image(selected_resource)

    def on_tab_changed(self, index: int):
        self.set_retrieved_resource_from_vc(index)

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) is WebSocketStatusUpdatedEvent:
            self._sync_ui()
