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
class DraftListDeployerSearchComboViewController(RWidget):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._setup_view()
        
    def _setup_view(self):
        card_search = CardSearchPreviewFactory.DraftListCardSearchPreviewViewController(self._app_dependencies_provider)

        VerticalBoxLayout([
            # WebSocketConfigurationV2ViewController(self._app_dependencies_provider),
            HorizontalSplitter([
                card_search,
                DraftListTabbedPackPreviewViewController(
                    self._app_dependencies_provider, 
                    data_source_local_resource_provider=card_search
                    ),
                
                DraftListWindowDeployerViewController(self._app_dependencies_provider)
                ])
        ], [None, 1]).set_layout_to_widget(self)
