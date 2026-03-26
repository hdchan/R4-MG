from typing import Optional

from PySide6.QtGui import QClipboard, QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QSizePolicy

from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppCore.Service.WebSocket.WebSocketServiceProtocol import (
    WebSocketServiceProtocol, WebSocketServiceStatus)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import (HorizontalBoxLayout, Label, LineEditText, PushButton,
                  RHorizontalExpandingSpacerWidget, RWidget)


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
        self._update_background_color()
        if (self._websocket_service.state == WebSocketServiceStatus.IS_HOST):
            self._config_view_container.replace_all_widgets([
                RHorizontalExpandingSpacerWidget(),
                Label(f"Host IP: {self._websocket_service.ip_address}"),
                PushButton("Copy", self._copy_ip).set_size_policy(
                    horizontal_policy=QSizePolicy.Policy.Maximum),
                PushButton("Disconnect", self._disconnect).set_size_policy(
                    horizontal_policy=QSizePolicy.Policy.Maximum),
            ])
        elif (self._websocket_service.state == WebSocketServiceStatus.IS_CLIENT):
            self._config_view_container.replace_all_widgets([
                RHorizontalExpandingSpacerWidget(),
                Label("Connected to host"),
                PushButton("Disconnect", self._disconnect).set_size_policy(
                    horizontal_policy=QSizePolicy.Policy.Maximum),
            ])
        else:
            self._line_edit_ip_address = LineEditText(text=self._websocket_service.ip_address, placeholder_text="Server IP address").set_size_policy(
                horizontal_policy=QSizePolicy.Policy.Maximum)
            self._line_edit_ip_address.setMinimumWidth(200)
            self._config_view_container.replace_all_widgets([
                RHorizontalExpandingSpacerWidget(),
                PushButton("Start Server", self._start_server).set_size_policy(
                    horizontal_policy=QSizePolicy.Policy.Maximum),
                PushButton("Connect to Server", self._connect_to_server).set_size_policy(
                    horizontal_policy=QSizePolicy.Policy.Maximum),
                self._line_edit_ip_address,
            ])

    def _update_background_color(self):
        if self._websocket_service.state == WebSocketServiceStatus.NONE:
            self.setPalette(QPalette())
        else:
            self.setAutoFillBackground(True)

            # 2. Get the current palette and change the 'Window' role
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor("green"))

            # 3. Apply the modified palette back to the widget
            self.setPalette(palette)

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
        text = self._websocket_service.ip_address
        if text:
            cb.setText(text,
                       mode=QClipboard.Mode.Clipboard)

    def _disconnect(self):
        self._websocket_service.disconnect()

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            self._sync_ui()
