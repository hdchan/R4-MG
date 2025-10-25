from PySide6.QtWidgets import QSizePolicy

from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                                LocalResourceDataSourceProviding)
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (CardSearchEvent,
                                        ConfigurationUpdatedEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.UIComponents.ImagePreview import \
    ImagePreviewLocalResourceDataSourceDecorator
from R4UI import RTabWidget, RWidget, VerticalBoxLayout, HorizontalBoxLayout

class CardSearchPreviewViewControllerDelegate:
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
        self._image_preview_view = ImagePreviewLocalResourceDataSourceDecorator(app_dependencies_provider)
        self._delegate = delegate


        # https://stackoverflow.com/a/19011496
        # image_preview_view.setMinimumHeight(360)
        self._image_preview_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self._observation_tower.subscribe_multi(self, [CardSearchEvent, ConfigurationUpdatedEvent])

        tab_count = self._delegate.csp_tab_count
        if tab_count > 1:
            self._tab_widget = RTabWidget([], self.on_tab_changed)

            for i in range(self._delegate.csp_tab_count):
                self._tab_widget.add_tabs([
                    (self._delegate.csp_local_resource_providing_vc(i), self._delegate.csp_tab_name(i)) # type: ignore
                ])
        else:
            self._tab_widget = self._delegate.csp_local_resource_providing_vc(0)

        self._box_layout = VerticalBoxLayout()
        if self._delegate.csp_is_vertical_orientation == False:
             self._box_layout = HorizontalBoxLayout()

        self._box_layout.set_layout_to_widget(self).set_uniform_content_margins(0)
        self._box_layout.add_widgets([
            self._image_preview_view,
            self._tab_widget
        ])
    
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self._image_preview_view
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._image_preview_view.selected_local_resource

    def set_retrieved_resource_from_vc(self, index: int = 0):
        selected_resource = self._delegate.csp_local_resource_providing_vc(index).data_source.selected_local_resource
        if selected_resource is None:
            return
        self._image_preview_view.set_image(selected_resource)

    def on_tab_changed(self, index: int):
        self.set_retrieved_resource_from_vc(index)

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        # if type(event) == ConfigurationUpdatedEvent:
        #     if self._tab_widget.current_index == CardSearchPreviewViewController.TabKeys.CARD_SEARCH:
                # self._search_table_view.get_selection()
                pass

    