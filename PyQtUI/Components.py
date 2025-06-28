
from typing import Callable, List, Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (QAction, QCheckBox, QComboBox, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMenu,
                             QMenuBar, QPushButton, QScrollArea, QSpacerItem,
                             QSplitter, QTabWidget, QVBoxLayout, QWidget)


class CheckBox(QCheckBox):
    def __init__(self, checked_fn: Callable[[Qt.CheckState], None]):
        super().__init__()
        self._checked_fn = checked_fn
        self.stateChanged.connect(self._checked)
        
    def _checked(self, state: Qt.CheckState):
        self._checked_fn(state)
    
class ComboBox(QComboBox):
    def __init__(self, options: List[str] = []):
        super().__init__()
        self.add_options(options)
            
    def add_options(self, options: List[str]):
        for o in options:
            self.addItem(o)
            
    def replace_options(self, options: List[str]):
        self.clear()
        self.add_options(options)
class Label(QLabel):
    def __init__(self, 
                 text: str,
                 point_size: int = 9,
                 is_bold: bool = False):
        super().__init__()
        self.setText(text)
        font = self.font()
        font.setBold(is_bold)
        font.setPointSize(point_size)
        self.setFont(font)
        
class BoldLabel(Label):
    def __init__(self, 
                 text: str):
        super().__init__(text, is_bold=True)
        
class HeaderLabel(Label):
    def __init__(self, 
                 text: str):
        super().__init__(text, point_size=12, is_bold=True)
class ScrollArea(QScrollArea):
    def __init__(self,
                 widget: QWidget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(widget)

class HorizontalBoxLayout(QWidget):
    def __init__(self, widgets: List[QWidget] = []):
        super().__init__()
        self._widgets: List[QWidget] = []
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self.add_widgets(widgets)
        
    def add_widgets(self, widgets: List[QWidget]):
        for w in widgets:
            self._widgets.append(w)
            self._layout.addWidget(w)
    
    def add_spacer(self, spacer_item: QSpacerItem) -> 'HorizontalBoxLayout':
        self._layout.addSpacerItem(spacer_item)
        return self
    
    def _clear_widgets(self):
        for i in reversed(range(self._layout.count())):
            layout_item = self._layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
                    widget = None
        self._widgets = []
                    
    def replace_widgets(self, widgets: List[QWidget]):
        self._clear_widgets()
        self.add_widgets(widgets)
        
    def set_to_layout(self, layout: QWidget) -> 'HorizontalBoxLayout':
        layout.setLayout(self.layout())
        return self
    
    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'HorizontalBoxLayout':
        self._layout.setContentsMargins(left, top, right, bottom)
        return self
            
class VerticalBoxLayout(QWidget):
    def __init__(self, widgets: List[QWidget] = []):
        super().__init__()
        self._widgets: List[QWidget] = []
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.add_widgets(widgets)
        
    def add_widgets(self, widgets: List[QWidget]):
        for w in widgets:
            self._widgets.append(w)
            self._layout.addWidget(w)
            
    def _clear_widgets(self):
        for i in reversed(range(self._layout.count())):
            layout_item = self._layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
                    widget = None
        self._widgets = []
                    
    def replace_widgets(self, widgets: List[QWidget]):
        self._clear_widgets()
        self.add_widgets(widgets)
        
    def set_to_layout(self, layout: QWidget) -> 'HorizontalBoxLayout':
        layout.setLayout(self.layout())
        return self
    
    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'HorizontalBoxLayout':
        self._layout.setContentsMargins(left, top, right, bottom)
        return self

class GridLayout(QWidget):
    def __init__(self, widgets: List[tuple[QWidget, tuple[int, int]]] = []):
        super().__init__()
        self._widgets: List[QWidget] = []
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.add_widgets(widgets)
        
    def add_widgets(self, widgets: List[tuple[QWidget, tuple[int, int]]]):
        for w, p in widgets:
            self._widgets.append(w)
            self._layout.addWidget(w, p[0], p[1])
            
    def _clear_widgets(self):
        for i in reversed(range(self._layout.count())):
            layout_item = self._layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
                    widget = None
        self._widgets = []
                    
    def replace_widgets(self, widgets: List[tuple[QWidget, tuple[int, int]]]):
        self._clear_widgets()
        self.add_widgets(widgets)
        
    def set_to_layout(self, layout: QWidget) -> 'HorizontalBoxLayout':
        layout.setLayout(self.layout())
        return self
    
    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'HorizontalBoxLayout':
        self._layout.setContentsMargins(left, top, right, bottom)
        return self

class PushButton(QPushButton):
    def __init__(self, 
                 text: Optional[str], 
                 triggered_fn: Callable[[], None]):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.setText(text)
        self.clicked.connect(self._triggered)
        
        
    def _triggered(self):
        self._triggered_fn()

class ActionMenuItem(QAction):
    def __init__(self,
                 text: str,
                 triggered_fn: Callable[[], None]):
        super().__init__(text)
        self._triggered_fn = triggered_fn
        self.triggered.connect(self._triggered)
        
    def _triggered(self):
        self._triggered_fn()
        
class MenuListBuilder(QMenu):
    def __init__(self, 
                 text: Optional[str] = None, 
                 actions: List[QAction] = []):
        super().__init__(text)
        self._items: List[QAction] = []
        self.add_actions(actions)
    
    def add_actions(self, actions: List[QAction]) -> 'MenuListBuilder':
        for a in actions:
            self._items.append(a)
            self.addAction(a) # type: ignore
        return self
    
    def add_action(self, 
                   text: str,
                   triggered_fn: Callable[[], None]) -> 'MenuListBuilder':
        action = ActionMenuItem(text, triggered_fn)
        self._items.append(action)
        self.addAction(action) # type: ignore
        return self
    
    def add_separator(self) -> 'MenuListBuilder':
        self.addSeparator()
        return self
    
    
    def exec_menu(self, point: QPoint):
        self.exec(point)
    
class MenuBarBuilder(QMenuBar):
    def __init__(self,
                 menus: List[QMenu] = []):
        super().__init__()
        self._menus: List[QMenu] = []
        self.add_menus(menus)
    
    def add_menus(self, menus: List[QMenu]) -> 'MenuBarBuilder':
        for m in menus:
            self._menus.append(m)
            self.addMenu(m)
        return self

class LineEditInt(QLineEdit):
    def __init__(self,
                 int: int, 
                 triggered_fn: Optional[Callable[[int], None]] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.setText(str(int))
        self.textChanged.connect(self._triggered)
        
    def _triggered(self, text: str):
        try:
            value = int(text)
            if self._triggered_fn is not None:
                self._triggered_fn(value)
        except:
            pass
        
    @property
    def value(self) -> Optional[int]:
        try:
            return int(self.text())
        except:
            pass
        
class LineEditText(QLineEdit):
    def __init__(self,
                 text: str, 
                 triggered_fn: Callable[[str], None]):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.setText(text)
        self.textChanged.connect(self._triggered)
        
    def _triggered(self, text: str):
        self._triggered_fn(text)

class HorizontalLabeledInputRow(QWidget):
    def __init__(self, 
                 text: str,
                 input: QWidget, 
                 description: Optional[str] = None):
        super().__init__()
        HorizontalBoxLayout([
            VerticalBoxLayout([
               Label(text),
            #    Label("descriptions are there to be for the benefit of us")
            ]),
            
            input
        ]).set_to_layout(self)

class VerticalGroupBox(QGroupBox):
    def __init__(self, initial_widgets: List[QWidget] = []):
        super().__init__()
        self._layout = VerticalBoxLayout(initial_widgets).set_to_layout(self)
    
    def add_widgets(self, widgets: List[QWidget]):
        self._layout.add_widgets(widgets)
            
    def replace_widgets(self, widgets: List[QWidget]):
        self._layout.replace_widgets(widgets)


class TabWidget(QWidget):
    def __init__(self, 
                 tabs: List[tuple[QWidget, str]] = [], 
                 tab_change_fn: Optional[Callable[[int], None]] = None):
        super().__init__()
        self._tab_change_fn = tab_change_fn
        self._tab_widget = QTabWidget()
        self._layout = VerticalBoxLayout([self._tab_widget]).set_to_layout(self)
        self._widgets: List[QWidget] = []
        self.add_tabs(tabs)
        
    def add_tabs(self, tabs: List[tuple[QWidget, str]]):
        for t in tabs:
            self._widgets.append(t[0])
            self._tab_widget.addTab(t[0], t[1])
    
    def _tab_changed(self, index: int):
        if self._tab_change_fn is not None:
            self._tab_change_fn(index)
        
    def set_to_layout(self, layout: QWidget) -> 'TabWidget':
        layout.setLayout(self.layout())
        return self
    
class Splitter(QSplitter):
    def __init__(self, 
                 orientation: Qt.Orientation, 
                 widgets: List[QWidget]):
        super().__init__()
        self.setOrientation(orientation)
        self._widgets: List[QWidget] = []
        self.add_widgets(widgets)
        
    def add_widgets(self, widgets: List[QWidget]):
        for w in widgets:
            self._widgets.append(w)
            self.addWidget(w)
            
class HorizontalSplitter(Splitter):
    def __init__(self,
                 widgets: List[QWidget]):
        super().__init__(Qt.Orientation.Horizontal, widgets)
        
class VerticalSplitter(Splitter):
    def __init__(self,
                 widgets: List[QWidget]):
        super().__init__(Qt.Orientation.Vertical, widgets)