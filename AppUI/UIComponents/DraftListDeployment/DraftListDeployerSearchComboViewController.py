from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.UIComponents.CardSearchPreview.CardSearchPreviewFactory import \
    CardSearchPreviewFactory
from R4UI import HorizontalSplitter, RWidget, VerticalBoxLayout
from AppUI.UIComponents.WebSocketConfiguration.WebSocketConfigurationV2ViewController import WebSocketConfigurationV2ViewController
from .DraftListTabbedPackPreviewViewController import \
    DraftListTabbedPackPreviewViewController
from .DraftListWindowDeployerViewController import \
    DraftListWindowDeployerViewController
from AppCore.Service.WebSocket.WebSocketServiceProtocol import WebSocketServiceStatus
from AppCore.Service.WebSocket.Events import WebSocketStatusUpdatedEvent
from AppCore.Observation import TransmissionReceiverProtocol, TransmissionProtocol
class DraftListDeployerSearchComboViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._websocket_service = app_dependencies_provider.websocket_service

        app_dependencies_provider.observation_tower.subscribe(self, WebSocketStatusUpdatedEvent)
        self._setup_view()
        
    def _setup_view(self):
        card_search = CardSearchPreviewFactory.DraftListCardSearchPreviewViewController(self._app_dependencies_provider)
        self._draft_list_deployer_view_controller = DraftListWindowDeployerViewController(self._app_dependencies_provider)
        VerticalBoxLayout([
            WebSocketConfigurationV2ViewController(self._app_dependencies_provider),
            HorizontalSplitter([
                card_search,
                DraftListTabbedPackPreviewViewController(
                    self._app_dependencies_provider, 
                    data_source_local_resource_provider=card_search
                    ),
                
                self._draft_list_deployer_view_controller
                ])
        ], [None, 1]).set_layout_to_widget(self)

        self._sync_ui()

    def _sync_ui(self):
        self._draft_list_deployer_view_controller.setVisible(self._websocket_service.state != WebSocketServiceStatus.IS_CLIENT)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is WebSocketStatusUpdatedEvent:
            self._sync_ui()