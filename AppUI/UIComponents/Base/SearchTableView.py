from typing import List

from PyQt5.QtWidgets import (QLineEdit, QListWidget, QPushButton, QVBoxLayout,
                             QWidget)

from AppCore.Observation import ObservationTower, TransmissionReceiver
from .LoadingSpinner import LoadingSpinner

class SearchTableView(QWidget, TransmissionReceiver):
    def __init__(self, observation_tower: ObservationTower):
        super().__init__()
        searchbar = QLineEdit(self)
        searchbar.setPlaceholderText("Search card by name (Ctrl+L)")
        searchbar.returnPressed.connect(self.search)
        self.searchbar = searchbar

        search_button = QPushButton()
        search_button.setText("Search (Enter)")
        search_button.clicked.connect(self.search)
        self.search_button = search_button

        result_list = QListWidget(self)
        result_list.itemSelectionChanged.connect(self.get_selection)
        self.result_list = result_list

        layout = QVBoxLayout(self)
        layout.addWidget(searchbar)
        layout.addWidget(search_button)
        layout.addWidget(result_list)
        self.setLayout(layout)
        
        self._loading_spinner = LoadingSpinner(self)

        self.delegate = None

    def get_selection(self):
        selected_indexs = self.result_list.selectedIndexes()
        if len(selected_indexs) > 0:
            self.delegate.tv_did_select(self, selected_indexs[0].row())

    def set_search_focus(self):
        self.searchbar.setFocus()

    def set_item_active(self, index: int):
        self.result_list.setCurrentRow(index)

    def search(self):
        # important that this happens before the delegate methods are called
        self._set_search_components_enabled(False)
        self._loading_spinner.start()
        # prevent query errors
        stripped_text = self.searchbar.text().strip()
        self.searchbar.setText(stripped_text)
        self.delegate.tv_did_tap_search(self, stripped_text)
        

    def update_list(self, list: List[str]):
        self.result_list.clear()
        for i in list:
            self.result_list.addItem(i)
        # important that this is the last thing that happens
        self._set_search_components_enabled(True)
        self._loading_spinner.stop()

    def _set_search_components_enabled(self, is_on: bool):
        self.searchbar.setEnabled(is_on)
        self.search_button.setEnabled(is_on)