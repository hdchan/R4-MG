from collections.abc import Callable

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

    def _index_to_key_pad_map(self, index: int) -> Qt.Key:
        mapping = {
            0: Qt.Key.Key_1,
            1: Qt.Key.Key_2,
            2: Qt.Key.Key_3,
            3: Qt.Key.Key_4,
            4: Qt.Key.Key_5,
            5: Qt.Key.Key_6,
            6: Qt.Key.Key_7,
            7: Qt.Key.Key_8,
            8: Qt.Key.Key_9,
            9: Qt.Key.Key_0,
        }
        return mapping[index]

    def _index_to_key_pad_string_map(self, index: int) -> str:
        mapping = {
            0: '1',
            1: '2',
            2: '3',
            3: '4',
            4: '5',
            5: '6',
            6: '7',
            7: '8',
            8: '9',
            9: '0',
        }
        return mapping[index]


    def staging_shortcut_text(self, index: int) -> str | None:
        if 0 <= index <= 9:
            return f'Stage (Ctrl+{self._index_to_key_pad_string_map(index)})'
        elif 10 <= index <= 19:
            return f'Stage (Shift+{self._index_to_key_pad_string_map(index - 10)})'
        return None

    def unstaging_shortcut_text(self, index: int) -> str | None:
        if 0 <= index <= 9:
            return f'Unstage (Alt+{self._index_to_key_pad_string_map(index)})'
        return 'Unstage'

    def bind_stage(self, fn: Callable[[], None], index: int, parent: QWidget):
        if 0 <= index <= 9:
            QShortcut(QKeySequence(Qt.Modifier.CTRL | self._index_to_key_pad_map(index)), parent).activated.connect(fn)
        elif 10 <= index <= 19:
            QShortcut(QKeySequence(Qt.Modifier.SHIFT | self._index_to_key_pad_map(index - 10)), parent).activated.connect(fn)
            
    def bind_unstage(self, fn: Callable[[], None], index: int, parent: QWidget):
        if 0 <= index <= 9:
            QShortcut(QKeySequence(Qt.Modifier.ALT | self._index_to_key_pad_map(index)), parent).activated.connect(fn)