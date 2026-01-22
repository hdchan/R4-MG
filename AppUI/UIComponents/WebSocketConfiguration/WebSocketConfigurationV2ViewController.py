from R4UI import (
    RWidget,
    HorizontalBoxLayout,
    PushButton,
    RHorizontalExpandingSpacerWidget,
    LineEditText,
    Label,
)
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import QSizePolicy
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding

from AppCore.Observation.Events import WebSocketStatusUpdatedEvent
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol
from typing import Optional
from AppCore.Service.WebSocket.WebSocketServiceProtocol import WebSocketServiceProtocol, WebSocketServiceStatus

class WebSocketConfigurationV2ViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider

        self._setup_view()

        app_dependencies_provider.observation_tower.subscribe_multi(
            self, [WebSocketStatusUpdatedEvent]
        )

    def _setup_view(self):
        self._config_view_container = HorizontalBoxLayout().set_layout_to_widget(self)
        self._line_edit_ip_address: Optional[LineEditText] = None
        self._sync_ui()

    def _sync_ui(self):
        if (self._websocket_service.state == WebSocketServiceStatus.IS_HOST):
            self._config_view_container.replace_all_widgets([
                    RHorizontalExpandingSpacerWidget(),
                    Label(f"Host IP: {self._websocket_service.ip_address}"),
                    PushButton("Copy", self._copy_ip).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum),
                    PushButton("Disconnect", self._disconnect).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum),
                ])
        elif (self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT):
            self._config_view_container.replace_all_widgets([
                    RHorizontalExpandingSpacerWidget(),
                    Label("Connected to host"),
                    PushButton("Disconnect", self._disconnect).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum),
                ])
        else:
            self._line_edit_ip_address = LineEditText(placeholder_text="Server IP address")
            self._config_view_container.replace_all_widgets([
                    RHorizontalExpandingSpacerWidget(),
                    PushButton("Start Server", self._start_server).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum),
                    PushButton("Connect to Server", self._connect_to_server).set_size_policy(horizontal_policy=QSizePolicy.Policy.Maximum),
                    self._line_edit_ip_address,
                ])

    @property
    def _websocket_service(self) -> WebSocketServiceProtocol:
        return self._app_dependencies_provider.websocket_service

    def _start_server(self):
        self._websocket_service.connect_as_host()

    def _connect_to_server(self):
        if self._line_edit_ip_address is not None:
            self._websocket_service.connect_as_client(
                self._line_edit_ip_address.text(),
                None
            )

    def _copy_ip(self):
        cb = QGuiApplication.clipboard()
        cb.clear(mode=QClipboard.Mode.Clipboard)
        cb.setText(self._websocket_service.ip_address, mode=QClipboard.Mode.Clipboard)

    def _disconnect(self):
        self._websocket_service.disconnect()

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            self._sync_ui()
