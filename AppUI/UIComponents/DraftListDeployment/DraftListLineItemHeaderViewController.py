
from PyQt5.QtWidgets import  QWidget, QLabel

from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding

from AppUI.Models.DraftListStyleSheet import DraftListStyleSheet
from R4UI import VerticalBoxLayout


class DraftListLineItemHeaderViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 stylesheet: DraftListStyleSheet,
                 text: str,
                 ):
        super().__init__()
        self._stylesheet = stylesheet
        self._asset_provider = app_dependencies_provider.asset_provider
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._text = text
        
        self._setup_view()
    
    def _setup_view(self):
        element = QLabel(self._text)
        
        extern_widget = self._external_app_dependencies_provider.draft_list_item_header(self._stylesheet, self._text)
        if extern_widget is not None:
            element = extern_widget
        
        VerticalBoxLayout([
            element
            ]).set_uniform_content_margins(0).set_layout_to_widget(self)