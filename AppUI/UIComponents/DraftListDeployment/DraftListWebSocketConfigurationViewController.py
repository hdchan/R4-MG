from R4UI import (
    RWidget,
    HorizontalBoxLayout,
    PushButton,
    RHorizontalExpandingSpacerWidget,
    LineEditText,
    Label,
)
from PySide6.QtWidgets import QSizePolicy
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppCore.DataSource.DraftList import (
    DataSourceDraftListProviding,
    DataSourceDraftListProviderConnectionStatus,
)
from AppCore.Observation.Events import DataSourceDraftListProviderStatusUpdatedEvent
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol


class DraftListWebSocketConfigurationViewController(
    RWidget, TransmissionReceiverProtocol
):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider

        self._setup_view()

        app_dependencies_provider.observation_tower.subscribe_multi(
            self, [DataSourceDraftListProviderStatusUpdatedEvent]
        )

    def _setup_view(self):
        self._config_view_container = HorizontalBoxLayout().set_layout_to_widget(self)

        self._sync_ui()

    def _sync_ui(self):
        if (self._data_source_draft_list_provider.state == DataSourceDraftListProviderConnectionStatus.IS_HOST):
            _disconnect_button = PushButton(
                "Disconnect", self._disconnect
            ).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum)
            self._config_view_container.replace_all_widgets(
                [
                    RHorizontalExpandingSpacerWidget(),
                    Label(
                        f"Server: {self._data_source_draft_list_provider.ip_address}"
                    ),
                    _disconnect_button,
                ]
            )
        elif (self._data_source_draft_list_provider.state == DataSourceDraftListProviderConnectionStatus.IS_CLIENT):
            _disconnect_button = PushButton(
                "Disconnect", self._disconnect
            ).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum)
            self._config_view_container.replace_all_widgets(
                [
                    RHorizontalExpandingSpacerWidget(),
                    Label(
                        f"Client: {self._data_source_draft_list_provider.ip_address}"
                    ),
                    _disconnect_button,
                ]
            )
        else:
            _start_server_button = PushButton(
                "Start Server", self._start_server
            ).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum)
            _connect_to_server_button = PushButton(
                "Connect to Server", self._connect_to_server
            ).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum)
            _line_edit_ip_address = LineEditText(placeholder_text="Server IP address")
            self._config_view_container.replace_all_widgets(
                [
                    RHorizontalExpandingSpacerWidget(),
                    _start_server_button,
                    _connect_to_server_button,
                    _line_edit_ip_address,
                ]
            )

    @property
    def _data_source_draft_list_provider(self) -> DataSourceDraftListProviding:
        return self._app_dependencies_provider.data_source_draft_list_provider

    def _start_server(self):
        self._data_source_draft_list_provider.connect_as_host()

    def _connect_to_server(self):
        self._data_source_draft_list_provider.connect_as_client(
            self._line_edit_ip_address.text()
        )

    def _disconnect(self):
        self._data_source_draft_list_provider.disconnect()

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is DataSourceDraftListProviderStatusUpdatedEvent:
            self._sync_ui()
