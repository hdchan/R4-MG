from typing import List, Optional

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QListWidget, QPushButton,
                             QVBoxLayout, QWidget)

from AppCore.Models import SearchConfiguration
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.ExternalAppDependenciesProviding import SearchQueryBarViewProviding
from R4UI import HorizontalBoxLayout, LineEditText

from .LoadingSpinner import LoadingSpinner


class SearchTableComboViewControllerDelegate:
    def stc_select_card_resource_for_card_selection(self, stc: 'SearchTableComboViewController', index: int) -> None:
        raise Exception
    
    def stc_did_click_search(self, stc: 'SearchTableComboViewController') -> None:
        raise Exception
    
    @property
    def stc_list_items(self) -> List[str]:
        raise Exception
    
    def stc_tapped_flip_button(self, stc: 'SearchTableComboViewController') -> None:
        raise Exception
    
    @property
    def stc_history_list(self) -> List[str]:
        return []
    
    def stc_did_select_history(self, stc: 'SearchTableComboViewController', index: int) -> None:
        return
    
    @property
    def stc_search_button_text(self) -> str:
        return "Search"
    
    @property
    def is_only_text_search(self) -> bool:
        return False
    
    @property
    def stc_is_flippable(self) -> bool:
        return False
    
    @property
    def stc_flip_button_text(self) -> str:
        return "Flip"
    
    def stc_result_list_scrolled(self, stc: 'SearchTableComboViewController', value: int) -> None:
        return
    
    @property
    def stc_has_more_pages(self) -> bool:
        return False
    
    @property
    def stc_is_flip_button_hidden(self) -> bool:
        return False
    
    @property 
    def stc_is_history_dropdown_hidden(self) -> bool:
        return False


# https://stackoverflow.com/a/65830989
class ComboBox(QComboBox):
    # https://code.qt.io/cgit/qt/qtbase.git/tree/src/widgets/widgets/qcombobox.cpp?h=5.15.2#n3173
    def paintEvent(self, event):
        
        painter = QtWidgets.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))

        # draw the combobox frame, focusrect and selected etc.
        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt)

        if self.currentIndex() < 0:
            opt.palette.setBrush(
                QtGui.QPalette.ButtonText,
                opt.palette.brush(QtGui.QPalette.ButtonText).color().lighter(),
            )
            if self.placeholderText():
                opt.currentText = self.placeholderText()

        # draw the icon and text
        painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

    # https://forum.qt.io/topic/105012/qcombobox-specify-width-less-than-content/11?_=1750960881253
    def showPopup(self):
        # we like the popup to always show the full contents
        # we only need to do work for this when the combo has had a maximum width specified
        maxWidth = self.maximumWidth()
        # see https://doc.qt.io/qt-5/qwidget.html#maximumWidth-prop for the 16777215 value
        if maxWidth and maxWidth < 16777215:
            self.setPopupMinimumWidthForItems()

        # call the base method now to display the popup
        super().showPopup()

    def setPopupMinimumWidthForItems(self):
        # we like the popup to always show the full contents
        # under Linux/GNOME popups always do this
        # but under Windows they get truncated/ellipsised
        # here we calculate the maximum width among the items
        # and set QComboBox.view() to accomodate this
        # which makes items show full width under Windows
        view = self.view()
        fm = self.fontMetrics()
        maxWidth = max([fm.width(self.itemText(i)) for i in range(self.count())])
        if maxWidth:
            view.setMinimumWidth(maxWidth + 50)

class DefaultSearchQueryBarViewController(SearchQueryBarViewProviding):
    def __init__(self):
        super().__init__()

        self._query_text: Optional[str] = None

        HorizontalBoxLayout([
            LineEditText(triggered_fn=self._set_text,
                         placeholder_text="Lookup by card name (Ctrl+L)"),
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)

    def _set_text(self, text: str):
        self._query_text = text

    @property
    def search_configuration(self) -> SearchConfiguration:
        config = SearchConfiguration()
        if self._query_text is not None:
            config.card_name = self._query_text
        return config
            
class SearchTableComboViewController(QWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 delegate: SearchTableComboViewControllerDelegate):
        super().__init__()
        self._delegate = delegate
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        top_button_layout = QHBoxLayout()
        top_button_layout.setContentsMargins(0, 0, 0, 0)
        top_button_widget = QWidget()
        top_button_widget.setLayout(top_button_layout)
        layout.addWidget(top_button_widget)

        flip_button = QPushButton()
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self._tapped_flip_button)
        self.flip_button = flip_button
        top_button_layout.addWidget(flip_button)

        search_history_selection = ComboBox()
        search_history_selection.setFixedWidth(50)
        search_history_selection.setPlaceholderText("🕙")
        search_history_selection.setMaxVisibleItems(25)
        search_history_selection.currentIndexChanged.connect(self._search_history_index_changed)
        search_history_selection.setCurrentIndex(-1)
        top_button_layout.addWidget(search_history_selection)
        self._search_history_selection = search_history_selection


        self._query_view = DefaultSearchQueryBarViewController()

        external_query_view = app_dependencies_provider.external_app_dependencies_provider.provide_card_search_query_view()
        if external_query_view is not None and delegate.is_only_text_search == False:
            self._query_view = external_query_view
        
        layout.addWidget(self._query_view)

        result_list = QListWidget()
        result_list.itemSelectionChanged.connect(self.get_selection)
        result_list.itemClicked.connect(self.get_selection)
        self.result_list = result_list
        layout.addWidget(result_list, 1)
        vertical_scroll_bar = result_list.verticalScrollBar()
        if vertical_scroll_bar is not None:
            vertical_scroll_bar.valueChanged.connect(self._result_list_scrolled)
        
        
        search_button = QPushButton()
        search_button.clicked.connect(self._search)
        layout.addWidget(search_button)
        self._search_button = search_button
        
        
        self._loading_spinner = LoadingSpinner(self)
        
        self.sync_ui()
    
    def _tapped_flip_button(self):
        self._delegate.stc_tapped_flip_button(self)

    def _search_history_index_changed(self, val: int):
        if val >= 0:
            self._delegate.stc_did_select_history(self, val)

    def reset_search_history(self):
        self._search_history_selection.setCurrentIndex(-1)

    def sync_ui(self):
        self._set_flip_button_enabled(self._delegate.stc_is_flippable)
        self.flip_button.setHidden(self._delegate.stc_is_flip_button_hidden)
        self.flip_button.setText(self._delegate.stc_flip_button_text)
        self._set_search_button_text(self._delegate.stc_search_button_text)

        self._search_history_selection.clear()
        history_list = self._delegate.stc_history_list
        self._search_history_selection.addItems(history_list)
        self._search_history_selection.setHidden(len(history_list) == 0 or self._delegate.stc_is_history_dropdown_hidden)

    def set_active(self):
        self.get_selection()
        
    def set_item_active(self, index: int):
        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(index)
    
    def set_search_focus(self):
        self._query_view.set_search_focus()

    def reset_search(self):
        self._query_view.reset_search()
    
    def get_selection(self):
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self._delegate.stc_select_card_resource_for_card_selection(self, selected_indexs[0].row())
            
    def _result_list_scrolled(self, value: int):
        # print(value)
        vertical_scroll_bar = self.result_list.verticalScrollBar()
        if vertical_scroll_bar is not None:
            if value >= vertical_scroll_bar.maximum() * .8:
                self._delegate.stc_result_list_scrolled(self, value)
                
    def _search(self):
        self._delegate.stc_did_click_search(self)
        
    def _get_search_button_text(self):
        self._delegate
        
    def set_search_components_enabled(self, is_on: bool):
        self._search_button.setEnabled(is_on)
        self._query_view.set_enabled(is_on)
        if is_on:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()
            
    def _set_search_button_text(self, text: str):
        self._search_button.setText(text)
        
    def set_configuration(self, configuration: SearchConfiguration):
        self._query_view.did_receive_configuration(configuration)
    
    @property
    def search_configuration(self) -> SearchConfiguration:
        return self._query_view.search_configuration
    
    @property
    def secondary_search_configuration(self) -> Optional[SearchConfiguration]:
        return self._query_view.secondary_search_configuration

    @property
    def tertiary_search_configuration(self) -> Optional[SearchConfiguration]:
        return self._query_view.tertiary_search_configuration
        
    
    def _set_flip_button_enabled(self, enabled: bool):
        self.flip_button.setEnabled(enabled)
        
    def load_list(self, is_initial_load: bool = True):
        # https://stackoverflow.com/questions/25187444/pyqt-qlistwidget-custom-items
        vertical_scroll_bar = self.result_list.verticalScrollBar()
        current_position = 0
        if vertical_scroll_bar is not None:
            current_position = vertical_scroll_bar.sliderPosition()
        
        selected_indexs = self.result_list.selectedIndexes()
        selected_index = 0
        if len(selected_indexs) > 0:
            selected_index = selected_indexs[0].row()
            
        self.result_list.clear()
        for i in self._delegate.stc_list_items:
            # TODO: async load list, incase its a large list
            self.result_list.addItem(i)
        
        if self._delegate.stc_has_more_pages:
            self.result_list.addItem('Loading more...')
        else:
            self.result_list.addItem('No more results')
        # important that this is the last thing that happens
        self.set_item_active(selected_index)
        self.set_search_components_enabled(True)
        
        if not is_initial_load and vertical_scroll_bar is not None:
            vertical_scroll_bar.setSliderPosition(current_position)