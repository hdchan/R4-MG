import urllib.parse
from typing import Optional

from PyQt5.QtCore import QPoint, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLabel, QMenu, QPushButton,
                             QVBoxLayout, QWidget)

from ...Assets import AssetProvider


class AddImageCTAViewControllerDelegate:
    def aicta_did_tap_generate_button(self, aicta: ...) -> None:
        pass

class AddImageCTAViewController(QWidget):
    def __init__(self, 
                 asset_provider: AssetProvider):
        super().__init__()
        
        self.setFixedHeight(150)
        self.asset_provider = asset_provider
        self.sound_effect = None
        
        pre_layout = QHBoxLayout()
        self.setLayout(pre_layout)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(layout)
        widget.setObjectName('parent')
        background_url = urllib.parse.urljoin("", asset_provider.image.sor_background.replace("\\", "/"))
        widget.setStyleSheet(f'''
                             #parent {{ 
                                background-image: url("{background_url}"); 
                                border-radius: 10px; 
                            }}
                             ''')
        layout.setSpacing(0)
        pre_layout.addWidget(widget)
        
        layout.addWidget(QWidget())
        
        r4_image = QLabel()
        image = QPixmap()
        image.load(asset_provider.image.r4_head)
        r4_image.setPixmap(image)
        r4_image.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        r4_image.customContextMenuRequested.connect(self._showContextMenu)
        layout.addWidget(r4_image)
        
        layout.addWidget(QWidget())
        
        cta_container_layout = QVBoxLayout()
        cta_container_widget = QWidget()
        cta_container_widget.setLayout(cta_container_layout)
        layout.addWidget(cta_container_widget)
        
        cta_container_layout.addWidget(QWidget())
        
        beep_text = QLabel()
        beep_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        beep_text.setStyleSheet('color: white;')
        beep_text.setText('<b>R4:</b> <i>Beep Boop</i>')
        cta_container_layout.addWidget(beep_text)
        
        text = QLabel()
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
        
        text2 = QLabel()
        text2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text2.setText('<b>File > New image file</b>')
        text2.setStyleSheet('color: white;')
        cta_container_layout.addWidget(text2)
        
        cta_container_layout.addWidget(QWidget())
        
        layout.addWidget(QWidget())
        
        self.delegate: Optional[AddImageCTAViewControllerDelegate] = None
    
    def _cta_clicked(self):
        if self.delegate is not None:
            self.delegate.aicta_did_tap_generate_button(self)
            
    def _showContextMenu(self, pos: QPoint):
        menu = QMenu(self)
        beep = QAction('Beep Boop')
        beep.triggered.connect(self._pressed_sound)
        menu.addAction(beep) # type: ignore
        menu.exec_(self.mapToGlobal(pos))
        
    def _pressed_sound(self):
        self.sound_effect = QSoundEffect()
        self.sound_effect.setVolume(0.5)
        self.sound_effect.setSource(QUrl.fromLocalFile(self.asset_provider.audio.r4_effect_path))
        print(f'playing sound effect: {self.asset_provider.audio.r4_effect_path}')
        self.sound_effect.play()