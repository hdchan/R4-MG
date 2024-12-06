from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QWidget


class ShortcutActionCoordinator:
    def bind_flip(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_F), parent).activated.connect(fn)

    def bind_focus_search(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_L), parent).activated.connect(fn)

    def bind_publish(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_P), parent).activated.connect(fn)

    def bind_search(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Key.Key_Return), parent).activated.connect(fn)

    def bind_search_leader(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.CTRL + Qt.Key.Key_Return), parent).activated.connect(fn)

    def bind_search_base(self, fn: Callable[[], None], parent: QWidget):
        QShortcut(QKeySequence(Qt.Modifier.SHIFT + Qt.Key.Key_Return), parent).activated.connect(fn)

    def bind_stage(self, fn: Callable[[], None], index: int, parent: QWidget):
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
        if 0 <= index < len(key_pad):
            QShortcut(QKeySequence(Qt.Modifier.CTRL + key_pad[index]), parent).activated.connect(fn)