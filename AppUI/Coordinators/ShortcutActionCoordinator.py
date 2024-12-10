from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QWidget

from AppUI.UIComponents.Composed import (CardSearchPreviewViewController,
                                         ImageDeploymentListViewController)


class ShortcutActionCoordinator:
    def __init__(self, 
                 parent: QWidget, 
                 card_search_view: CardSearchPreviewViewController, 
                 deployment_view: ImageDeploymentListViewController):
        self._card_search_view = card_search_view
        self._deployment_view = deployment_view
        # Needs to block ability to publish if not able to
        self.production_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_P), parent)
        self.production_shortcut.activated.connect(deployment_view.publish_to_production)

        self.focus_search = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_L), parent)
        self.focus_search.activated.connect(card_search_view.set_search_focus)

        self.flip_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_F), parent)
        self.flip_shortcut.activated.connect(card_search_view.tapped_flip_button)

        key_pad = [
            Qt.Key.Key_1,
            Qt.Key.Key_2,
            Qt.Key.Key_3,
            Qt.Key.Key_4,
            Qt.Key.Key_5,
            Qt.Key.Key_6,
            Qt.Key.Key_7,
            Qt.Key.Key_8,
            Qt.Key.Key_9,
            Qt.Key.Key_0,
        ]
        for i, k in enumerate(key_pad):
            self.staging_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + k), parent)
            self.staging_shortcut.activated.connect(partial(self._deployment_view.stage_current_image, i))
            
            
        self.search_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), parent)
        self.search_shortcut.activated.connect(card_search_view.search)
        
        self.search_leader_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_Return), parent)
        self.search_leader_shortcut.activated.connect(card_search_view.search_leader)
        
        self.search_base_shortcut = QShortcut(QKeySequence(Qt.Modifier.SHIFT + Qt.Key.Key_Return), parent)
        self.search_base_shortcut.activated.connect(card_search_view.search_base)