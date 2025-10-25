from PyQt5.QtCore import QPoint, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QAction, QMenu, QTextEdit, QVBoxLayout,
                             QWidget)

from AppCore.Config import ConfigurationManager

from ..Assets import AssetProvider
from R4UI import Label


class AboutViewController(QWidget):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 asset_provider: AssetProvider):
        super().__init__()
        self.setWindowTitle("About")
        self.configuration_manager = configuration_manager
        self.asset_provider = asset_provider
        self.sound_effect = None
        
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)
        
        image = QPixmap()
        
        image.load(self.asset_provider.image.logo_path)
        image = image.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        image_view = Label()
        image_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        image_view.customContextMenuRequested.connect(self._showContextMenu)
        image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_view.setPixmap(image)
        v_layout.addWidget(image_view)
        
        configuration = self.configuration_manager.configuration
        
        label = Label()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText(f'{configuration.app_display_name}')
        v_layout.addWidget(label)

        with open(self.asset_provider.text.change_log_path, 'r') as file:
            data = file.read()
        markdown = QTextEdit()
        markdown.setMarkdown(data)
        markdown.setReadOnly(True)
        v_layout.addWidget(markdown)
        
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