from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.UIComponents.CardSearchPreview.CardSearchPreviewFactory import \
    CardSearchPreviewFactory
from AppUI.UIComponents.ImageDeployment.ImageDeploymentListViewController import \
    ImageDeploymentListViewController
from AppUI.UIComponents.WebSocketConfiguration.WebSocketConfigurationV2ViewController import \
    WebSocketConfigurationV2ViewController
from R4UI import HorizontalSplitter, RWidget, VerticalBoxLayout


class MainProgramViewController(RWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()

        card_search_preview_view_controller = CardSearchPreviewFactory.ImageDeploymentCardSearchPreviewViewController(
            app_dependencies_provider)

        splitter = HorizontalSplitter([
            card_search_preview_view_controller,
            ImageDeploymentListViewController(app_dependencies_provider,
                                              card_search_preview_view_controller)
        ])

        splitter.setSizes([450, 900])
        splitter.setStretchFactor(0, 0)  # prevent search pane from stretching
        splitter.setStretchFactor(1, 1)  # allow deployment list to stretch

        VerticalBoxLayout([
            WebSocketConfigurationV2ViewController(app_dependencies_provider),
            splitter
        ], [None, 1]).set_layout_to_widget(
            self).set_uniform_content_margins(0)

        app_dependencies_provider.data_source_image_resource_deployer.load_production_resources()
