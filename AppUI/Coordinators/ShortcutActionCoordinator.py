from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from ..MainProgramViewController import MainProgramViewController


class ShortcutActionCoordinator:
    def __init__(self, main_program: MainProgramViewController):
        # Needs to block ability to publish if not able to
        self.production_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_P), main_program)
        self.production_shortcut.activated.connect(main_program.idl_did_tap_production_button)

        self.search_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_L), main_program)
        self.search_shortcut.activated.connect(main_program.set_search_bar_focus)

        self.flip_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_F), main_program)
        self.flip_shortcut.activated.connect(main_program.flip_current_previewed_card_if_possible)

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
            self.staging_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL + k), main_program)
            self.staging_shortcut.activated.connect(partial(main_program.stage_current_card_search_resource, i))