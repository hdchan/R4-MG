
from PyQt5.QtWidgets import QWidget

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents import ImagePreviewLocalResourceDataSourceDecorator
from R4UI import VerticalBoxLayout, HorizontalSplitter

from ..Base.SearchTableViewController import SearchTableViewController
from .DraftListTabbedPackPreviewViewController import DraftListTabbedPackPreviewViewController
from .DraftListWindowDeployerViewController import DraftListWindowDeployerViewController
class DraftListDeployerSearchComboViewController(QWidget):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._setup_view()
        
    def _setup_view(self):
        configuration = SearchTableViewController.SearchTableViewControllerConfiguration(is_flip_button_hidden=False)
        
        image_preview_view = ImagePreviewLocalResourceDataSourceDecorator(self._app_dependencies_provider)
        search_table = SearchTableViewController(self._app_dependencies_provider, configuration, image_preview_view)
        
        the_view = HorizontalSplitter([
                VerticalBoxLayout([
                    image_preview_view,
                    search_table
                ]),
                
                DraftListTabbedPackPreviewViewController(
                    self._app_dependencies_provider, 
                    data_source_local_resource_provider=search_table
                    ),
                
                DraftListWindowDeployerViewController(self._app_dependencies_provider)
                ])
        
        VerticalBoxLayout([
            the_view
        ]).set_layout_to_widget(self)
