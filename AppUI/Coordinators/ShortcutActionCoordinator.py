from typing import Callable, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget


# Update `shortcuts.md` when adding new shortcut
class ShortcutActionCoordinator:
    def bind_flip(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_F), parent).activated.connect(fn)

    def bind_focus_search(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_L), parent).activated.connect(fn)
        
    def bind_reset_search(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_K), parent).activated.connect(fn)

    def bind_publish(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_P), parent).activated.connect(fn)

    def bind_search(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Key.Key_Return), parent).activated.connect(fn)

    def bind_search_leader(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return), parent).activated.connect(fn)

    def bind_search_base(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Return), parent).activated.connect(fn)
        
    def bind_add_card_to_draft_list(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_D), parent).activated.connect(fn)

    @property
    def _key_pad(self) -> List[Qt.Key]:
        return [
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

    def bind_stage(self, fn: Callable[[], None], index: int, parent: QWidget):
        if 0 <= index < len(self._key_pad):
            QShortcut(QKeySequence(Qt.Modifier.CTRL | self._key_pad[index]), parent).activated.connect(fn)
            
    def bind_unstage(self, fn: Callable[[], None], index: int, parent: QWidget):
        if 0 <= index < len(self._key_pad):
            QShortcut(QKeySequence(Qt.Modifier.ALT | self._key_pad[index]), parent).activated.connect(fn)