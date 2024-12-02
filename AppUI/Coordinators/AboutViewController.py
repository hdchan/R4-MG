from PyQt5.QtCore import QPoint, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QLabel, QMenu, QPushButton, QVBoxLayout, QWidget, QAction

from AppCore.Config import ConfigurationProvider

from ..Assets import AssetProvider


class AboutViewController(QWidget):
    def __init__(self, 
                 configuration_provider: ConfigurationProvider, 
                 asset_provider: AssetProvider):
        super().__init__()
        self.setWindowTitle("About")
        self.configuration_provider = configuration_provider
        self.asset_provider = asset_provider
        self.sound_effect = None
        
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)
        
        image = QPixmap()
        
        success = image.load(asset_provider.image.logo_path)
        image = image.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        image_view = QLabel()
        image_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        image_view.customContextMenuRequested.connect(self._showContextMenu)
        image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_view.setPixmap(image)
        v_layout.addWidget(image_view)
        
        configuration = configuration_provider.configuration
        
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText(f'{configuration.app_display_name}\nv.{configuration.app_ui_version}')
        v_layout.addWidget(label)
        
        
        # button = QPushButton()
        # button.setText("Beep Boop")
        # button.clicked.connect(self._pressed_sound)
        # v_layout.addWidget(button)
        
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