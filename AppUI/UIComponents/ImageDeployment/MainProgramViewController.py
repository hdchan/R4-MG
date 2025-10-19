from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.UIComponents.ImageDeployment.ImageDeploymentListViewController import ImageDeploymentListViewController
from AppUI.UIComponents.CardSearchPreview.CardSearchPreviewFactory import \
    CardSearchPreviewFactory
from R4UI import RWidget, HorizontalBoxLayout, HorizontalSplitter

class MainProgramViewController(RWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        
        card_search_preview_view_controller = CardSearchPreviewFactory.ImageDeploymentCardSearchPreviewViewController(app_dependencies_provider)
        
        deployment_view_controller = ImageDeploymentListViewController(app_dependencies_provider,
                                                                       card_search_preview_view_controller)
        
        horizontal_layout = HorizontalBoxLayout().set_layout_to_widget(self).set_uniform_content_margins(0)
        
        splitter = HorizontalSplitter()
        horizontal_layout.add_widget(splitter)
        
        self.card_search_view = card_search_preview_view_controller
        
        splitter.add_widget(self.card_search_view)

        
        self.deployment_view = deployment_view_controller
        
        splitter.add_widget(deployment_view_controller)
        splitter.setSizes([450, 900])
        splitter.setStretchFactor(0, 0) # prevent search pane from stretching
        splitter.setStretchFactor(1, 1) # allow deployment list to stretch

        app_dependencies_provider.data_source_image_resource_deployer.load_production_resources()
