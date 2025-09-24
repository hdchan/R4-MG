
from typing import Any, Callable, List, Optional, TypeVar

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (QAction, QButtonGroup, QCheckBox, QComboBox,
                             QGroupBox, QLabel, QLineEdit, QMenu, QMenuBar,
                             QPushButton, QRadioButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QSplitter, QTabWidget,
                             QWidget)

from .BoxLayouts import HorizontalBoxLayout, VerticalBoxLayout

T = TypeVar("T")
class LabeledRadioButton(QWidget):
    def __init__(self, 
                 text: str, 
                 value: T, 
                 toggled_fn: Optional[Callable[[T], None]] = None):
        super().__init__()
        self._radio_button = QRadioButton(text)
        self._radio_button.toggled.connect(self._toggled)
        self._toggled_fn = toggled_fn
        self.value = value
        HorizontalBoxLayout([
            self._radio_button
        ]).set_to_layout(self)
        
    def _toggled(self):
        if self._toggled_fn is not None:
            self._toggled_fn(self.value)
    
    @property
    def radio_button(self) -> QRadioButton:
        return self._radio_button

class ButtonGroup(QWidget):
    def __init__(self, 
                 values: List[tuple[str, T]], 
                 toggled_fn: Optional[Callable[[T], None]] = None):
        super().__init__()
        self._toggled_fn = toggled_fn
        self._button_group = QButtonGroup(self)
        self._buttons: List[LabeledRadioButton] = []
        self._selected_value: T
        
        def _selected(value: T):
            self._selected_value = value
            self._toggled()
            
        for text, value in values:
            self._buttons.append(LabeledRadioButton(text, value, _selected))
        
        self._layout = VerticalBoxLayout().set_to_layout(self)
        for b in self._buttons:
            self._layout.add_widget(b.radio_button)
    
    def set_checked(self, index: int):
        self._buttons[index].radio_button.setChecked(True)
    
    def _toggled(self):
        if self._toggled_fn is not None:
            self._toggled_fn(self._selected_value)
            
    def set_alignment_top(self) -> 'ButtonGroup':
        self._layout.set_alignment_top()
        return self

class CheckBox(QCheckBox):
    def __init__(self, checked_fn: Callable[[bool], None]):
        super().__init__()
        self._checked_fn = checked_fn
        self.stateChanged.connect(self._checked)
        
    def _checked(self, state: Qt.CheckState):
        self._checked_fn(state == Qt.CheckState.Checked)
    
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
        
class ObjectComboBox(QComboBox):
    def __init__(self, options: List[tuple[str, Optional[Any]]] = []):
        super().__init__()
        self.add_options(options)
            
    def add_options(self, options: List[tuple[str, Optional[Any]]]):
        for string, object in options:
            self.addItem(string, object)
            
    def replace_options(self, options: List[tuple[str, Optional[Any]]]):
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
                 int: Optional[int] = None, 
                 triggered_fn: Optional[Callable[[int], None]] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.set_value(int)
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
        
    def set_value(self, int: Optional[int]):
        if int is None:
            return
        self.setText(str(int))
        
class LineEditText(QLineEdit):
    def __init__(self,
                 text: Optional[str] = None, 
                 triggered_fn: Optional[Callable[[str], None]] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.set_value(text)
        self.textChanged.connect(self._triggered)
        
    def _triggered(self, text: str):
        if self._triggered_fn is not None:
            self._triggered_fn(text)
    
    @property
    def value(self) -> Optional[int]:
        self.text()
    
    def set_value(self, value: Optional[str]):
        if value is None:
            return
        self.setText(value)

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
            
    def replace_all_widgets(self, widgets: List[QWidget]):
        self._layout.replace_all_widgets(widgets)
        
    def set_alignment_top(self) -> 'VerticalGroupBox':
        self._layout.set_alignment_top()
        return self
    
    def add_spacer(self, spacer_item: QSpacerItem) -> 'VerticalGroupBox':
        self._layout.add_spacer(spacer_item)
        return self


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


class Spacer(QSpacerItem):
    def __init__(self, width: int, height: int, h_policy: QSizePolicy.Policy, v_policy: QSizePolicy.Policy):
        super().__init__(width, height, h_policy, v_policy)
        pass

class VerticallyExpandingSpacer(Spacer):
    def __init__(self, width: int = 0, height: int = 0):
        super().__init__(width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        pass
        
class HorizontallyExpandingSpacer(Spacer):
    def __init__(self, width: int = 0, height: int = 0):
        super().__init__(width, height, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        pass