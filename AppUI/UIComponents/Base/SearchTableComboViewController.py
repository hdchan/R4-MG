from typing import List, Optional

from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QVBoxLayout, QWidget)
from PyQt5 import QtGui, QtWidgets
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
    def stc_default_card_type(self) -> Optional[str]: # can this optional?
        return None
    
    @property
    def stc_card_type_list(self) -> List[str]:
        return []
    
    @property
    def stc_history_list(self) -> List[str]:
        return []
    
    def stc_did_select_history(self, stc: 'SearchTableComboViewController', index: int) -> None:
        return
    
    @property
    def stc_search_button_text(self) -> str:
        return "Search"
    
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
            
class SearchTableComboViewController(QWidget):
    def __init__(self,
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

        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_widget = QWidget()
        query_widget.setLayout(query_layout)
        layout.addWidget(query_widget)

        card_name_search_bar = QLineEdit(self)
        card_name_search_bar.setPlaceholderText("Lookup by card name (Ctrl+L)")
        self.card_name_search_bar = card_name_search_bar
        query_layout.addWidget(card_name_search_bar)
        
        card_type_layout = QHBoxLayout()
        card_type_layout.setContentsMargins(0, 0, 0, 0)
        card_type_widget = QWidget()
        card_type_widget.setLayout(card_type_layout)
        query_layout.addWidget(card_type_widget)
        
        card_type_selection_label = QLabel("Type")
        card_type_layout.addWidget(card_type_selection_label)
        self._card_type_selection_label = card_type_selection_label
        
        card_type_selection = QComboBox()
        for i in self._delegate.stc_card_type_list:
            card_type_selection.addItem(i)
        self.card_type_selection = card_type_selection
        card_type_layout.addWidget(card_type_selection)
        
        

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
        self.card_type_selection.setHidden(not self._delegate.stc_card_type_list)
        self._card_type_selection_label.setHidden(not self._delegate.stc_card_type_list)

        self._search_history_selection.clear()
        history_list = self._delegate.stc_history_list
        self._search_history_selection.addItems(history_list)
        self._search_history_selection.setHidden(len(history_list) == 0 or self._delegate.stc_is_history_dropdown_hidden)

    def set_card_type_filter(self, card_type: Optional[str]):
        if card_type is not None:
            found_index = self.card_type_selection.findText(card_type)
        else:
            found_index = self.card_type_selection.findText(self._delegate.stc_default_card_type)
           
        if found_index >= 0:
                self.card_type_selection.setCurrentIndex(found_index)
        else:
            raise Exception("index not found")
    
    def set_active(self):
        self.get_selection()
        
    def set_item_active(self, index: int):
        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(index)
    
    def set_search_focus(self):
        self.card_name_search_bar.setFocus()
        self.card_name_search_bar.selectAll()

    def reset_search(self):
        self.card_name_search_bar.clear()
        self.card_name_search_bar.setFocus()
        self.set_card_type_filter(None)
    
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
        self.card_name_search_bar.setEnabled(is_on)
        self._search_button.setEnabled(is_on)
        self.card_type_selection.setEnabled(is_on)
        if is_on:
            self._loading_spinner.stop()
        else:
            self._loading_spinner.start()
            
    def _set_search_button_text(self, text: str):
        self._search_button.setText(text)
        
    def set_search_bar_text(self, text: str):
        self.card_name_search_bar.setText(text)
        
    @property
    def card_name_search_bar_text(self) -> str:
        return self.card_name_search_bar.text()
    
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