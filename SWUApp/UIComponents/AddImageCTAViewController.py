import urllib.parse
from typing import Optional

from PyQt5.QtCore import QPoint, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QMenu, QPushButton,
                             QVBoxLayout, QWidget)

from AppCore.DataSource import DataSourceImageResourceDeployer
from AppCore.Observation import *
from AppCore.Observation.Events import CardSearchEvent
from AppUI.Router.Router import Router
from R4UI import RWidget, Label

from ..Assets import AssetProvider
from .LoadingSpinnerDisc import LoadingSpinnerDisc


class AddImageCTAViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 observation_tower: ObservationTower,
                 data_source_image_resource_deployer: DataSourceImageResourceDeployer,
                 asset_provider: AssetProvider, 
                 router: Router):
        super().__init__()
        self._asset_provider = asset_provider
        self._observation_tower = observation_tower
        self._data_source_image_resource_deployer = data_source_image_resource_deployer
        self._observation_tower.subscribe(self, CardSearchEvent)
        self._router = router

        self.setFixedHeight(150)
        self.sound_effect = None
        
        pre_layout = QHBoxLayout()
        self.setLayout(pre_layout)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(layout)
        widget.setObjectName('parent')
        background_url = urllib.parse.urljoin("", self._asset_provider.image.sor_background.replace("\\", "/"))
        widget.setStyleSheet(f'''
                             #parent {{ 
                                background-image: url("{background_url}"); 
                                border-radius: 10px; 
                            }}
                             ''')
        layout.setSpacing(0)
        pre_layout.addWidget(widget)
        
        layout.addWidget(QWidget())
        
        r4_image = Label()
        image = QPixmap()
        image.load(self._asset_provider.image.r4_head)
        r4_image.setPixmap(image)
        r4_image.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        r4_image.customContextMenuRequested.connect(self._showContextMenu)
        layout.addWidget(r4_image)
        
        self._loading_spinner = LoadingSpinnerDisc()
        layout.addWidget(self._loading_spinner)
        
        cta_container_layout = QVBoxLayout()
        cta_container_widget = QWidget()
        cta_container_widget.setLayout(cta_container_layout)
        layout.addWidget(cta_container_widget)
        
        cta_container_layout.addWidget(QWidget())
        
        beep_text = Label()
        beep_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        beep_text.setStyleSheet('color: white;')
        beep_text.setText('<b>R4:</b> <i>Beep Boop</i>')
        cta_container_layout.addWidget(beep_text)
        
        text = Label()
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet('color: white;')
        text.setText('I can help you create a new image file.')
        cta_container_layout.addWidget(text)
        
        cta = QPushButton()
        cta.setMinimumHeight(25)
        cta.setText('Create a new image')
        cta.setStyleSheet('background-color: #6694ce ; color: white;')
        cta.clicked.connect(self._cta_clicked)
        cta_container_layout.addWidget(cta)
        
        text2 = Label()
        text2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text2.setText('<b>File > New image file</b>')
        text2.setStyleSheet('color: white;')
        cta_container_layout.addWidget(text2)
        
        cta_container_layout.addWidget(QWidget())
        
        layout.addWidget(QWidget())
    
    def _cta_clicked(self):
        def prompt_generate_new_file_with_placeholder(placeholder_image_path: Optional[str]):
            file_name, ok = self._router.prompt_text_input('Create new image file', 'Enter file name:')
            if ok:
                try:
                    self._data_source_image_resource_deployer.generate_new_file(file_name, placeholder_image_path)
                    self._data_source_image_resource_deployer.load_production_resources()
                except Exception as error:
                    self._router.show_error(error)
        prompt_generate_new_file_with_placeholder(self._asset_provider.image.swu_card_back)
            
    def _showContextMenu(self, pos: QPoint):
        menu = QMenu(self)
        beep = QAction('Beep Boop')
        beep.triggered.connect(self._pressed_sound)
        menu.addAction(beep) # type: ignore
        menu.exec_(self.mapToGlobal(pos))
        
    def _pressed_sound(self):
        self.sound_effect = QSoundEffect()
        self.sound_effect.setVolume(0.5)
        self.sound_effect.setSource(QUrl.fromLocalFile(self._asset_provider.audio.r4_effect_path))
        print(f'playing sound effect: {self._asset_provider.audio.r4_effect_path}')
        self.sound_effect.play()
        
        
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == CardSearchEvent:
            if event.event_type == CardSearchEvent.EventType.STARTED:
                self._loading_spinner.start()
            else:
                self._loading_spinner.stop()