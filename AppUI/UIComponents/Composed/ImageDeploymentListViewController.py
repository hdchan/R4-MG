
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QScrollArea, QVBoxLayout, QWidget

from AppCore import Configuration, ObservationTower

from . import ImageDeploymentViewController


class ImageDeploymentListViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration: Configuration):
        super().__init__()

        self.observation_tower = observation_tower
        self.configuration = configuration

        layout = QVBoxLayout()
        scroll = QScrollArea(self)
        widget = QWidget()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        layout_2 = QVBoxLayout()
        layout_2.addWidget(scroll)

        unstage_all_button = QPushButton()
        unstage_all_button.setText("Unstage All")
        unstage_all_button.setEnabled(False)
        unstage_all_button.clicked.connect(self.tapped_unstage_all_button)
        self.unstage_all_button = unstage_all_button
        # layout_2.addWidget(unstage_all_button)

        production_button = QPushButton()
        production_button.setText("Production (Ctrl+P)")
        production_button.setEnabled(False)
        production_button.clicked.connect(self.tapped_production_button)
        self.production_button = production_button
        layout_2.addWidget(production_button)

        self.setLayout(layout_2)
        

        self._layout = layout
        self.list_items = []
        self.scroll = scroll
        self.delegate = None

    def create_list_item(self, file_name: str, img_alt: str, img: str, staging_button_enabled: bool, index: int):
        item = ImageDeploymentViewController(self.observation_tower, 
                                             self.configuration)
        item.delegate = self
        item.set_production_image(img_alt, img)
        item.stage_button.setText(f'Stage (Ctrl+{index + 1})')
        item.set_label(file_name)
        item.set_staging_button_enabled(staging_button_enabled)
        pal = item.palette()
        pal.setColor(item.backgroundRole(), Qt.GlobalColor.lightGray)
        item.setAutoFillBackground(True)
        item.setPalette(pal)
        self._layout.addWidget(item)

        self.list_items.append(item)

    def clear_list(self):
        for i in reversed(range(self._layout.count())):
            self._layout.takeAt(i).widget().deleteLater()
        self.list_items = []

    def id_did_tap_staging_button(self, id_cell):
        for idx, i in enumerate(self.list_items):
            if i == id_cell:
                self.delegate.idl_did_tap_staging_button(self, id_cell, idx)

    def id_did_tap_unstaging_button(self, id_cell):
        for idx, i in enumerate(self.list_items):
            if i == id_cell:
                self.delegate.idl_did_tap_unstaging_button(self, id_cell, idx)

    def set_staging_image(self, text, img, index):
        self.list_items[index].set_staging_image(text, img)

    def clear_staging_image(self, index):
        self.list_items[index].clear_staging_image()
    
    def set_production_image(self, text, img, index):
        self.list_items[index].set_production_image(text, img)

    def clear_all_staging_images(self):
        for idx, i in enumerate(self.list_items):
            i.clear_staging_image()

    def tapped_production_button(self):
        self.delegate.idl_did_tap_production_button()

    def tapped_unstage_all_button(self):
        self.delegate.idl_did_tap_unstage_all_button()

    def set_all_staging_button_enabled(self, enabled: bool):
        for idx, i in enumerate(self.list_items):
            i.set_staging_button_enabled(enabled)

    def set_production_button_enabled(self, enabled: bool):
        # https://stackoverflow.com/questions/21685414/qt5-setting-background-color-to-qpushbutton-and-qcheckbox
        # pal = self.production_button.palette()
        # pal.setColor(self.production_button.backgroundRole(), Qt.green)
        # self.production_button.setAutoFillBackground(True)
        # self.production_button.setPalette(pal)
        # self.production_button.update()
        self.production_button.setEnabled(enabled)
        if enabled:
            self.production_button.setStyleSheet("background-color : #90EE90")
        else:
            self.production_button.setStyleSheet("")