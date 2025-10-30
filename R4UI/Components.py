
from typing import Any, Callable, List, Optional, TypeVar, Generic

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIntValidator, QDoubleValidator, QAction
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox,
                             QGroupBox, QLabel, QLineEdit, QMenu, QMenuBar,
                             QPushButton, QRadioButton, QScrollArea,
                             QSizePolicy, QSpacerItem, QTabWidget, QMainWindow)

from .BoxLayouts import HorizontalBoxLayout, VerticalBoxLayout
from .RWidget import RWidget


T = TypeVar("T")
class RLabeledRadioButton(RWidget, Generic[T]):
    def __init__(self, 
                 text: str, 
                 value: T, 
                 toggled_fn: Optional[Callable[[T], None]] = None, 
                 is_checked: bool = False):
        super().__init__()
        self._radio_button = QRadioButton(text)
        self._radio_button.toggled.connect(self._toggled)
        self._toggled_fn = toggled_fn
        self.value = value
        self._radio_button.setChecked(is_checked)
        HorizontalBoxLayout([
            self._radio_button
        ]).set_layout_to_widget(self)
        
    def _toggled(self):
        if self._toggled_fn is not None:
            self._toggled_fn(self.value)
    
    @property
    def radio_button(self) -> QRadioButton:
        return self._radio_button
    
    def set_checked(self, checked: bool) -> QRadioButton:
        self._radio_button.setChecked(checked)
        return self

class RButtonGroup(RWidget, Generic[T]):
    def __init__(self, 
                 values: List[tuple[str, T]], 
                 toggled_fn: Optional[Callable[[T], None]] = None):
        super().__init__()
        self._toggled_fn = toggled_fn
        self._button_group = QButtonGroup(self)
        self._buttons: List[RLabeledRadioButton[T]] = []
        self._selected_value: T
        
        def _selected(value: T):
            self._selected_value = value
            self._toggled()
            
        for text, value in values:
            self._buttons.append(RLabeledRadioButton(text, value, _selected))
        
        self._layout = VerticalBoxLayout().set_layout_to_widget(self)
        for b in self._buttons:
            self._layout.add_widget(b.radio_button)
    
    def set_checked_index(self, index: int) -> 'RButtonGroup[T]':
        self._buttons[index].radio_button.setChecked(True)
        return self
    
    def set_object_checked(self, o: T) -> 'RButtonGroup[T]':
        found = list(filter(lambda x: x.value == o, self._buttons))
        if len(found) > 0:
            found[0].set_checked(True)
        return self
    
    def _toggled(self):
        if self._toggled_fn is not None:
            self._toggled_fn(self._selected_value)
            
    def set_alignment_top(self) -> 'RButtonGroup[T]':
        self._layout.set_alignment_top()
        return self

class RCheckBox(QCheckBox):
    def __init__(self, 
                 checked_fn: Callable[[bool], None], 
                 is_checked: bool = False):
        super().__init__()
        self._checked_fn = checked_fn
        self.setChecked(is_checked)
        # pyside .stateChanged returns in
        # should use .checkStateChanged
        self.checkStateChanged.connect(self._checked)
        
    def _checked(self, state: Qt.CheckState):
        self._checked_fn(state == Qt.CheckState.Checked)
    
class RComboBox(QComboBox):
    def __init__(self, options: List[str] = []):
        super().__init__()
        self.add_options(options)
            
    def add_options(self, options: List[str]):
        for o in options:
            self.addItem(o)
            
    def replace_options(self, options: List[str]):
        self.clear()
        self.add_options(options)
        
class RObjectComboBox(QComboBox):
    def __init__(self, options: List[tuple[str, Optional[Any]]] = []):
        super().__init__()

        self._data: List[Any] = []
        self.add_options(options)
            
    def add_options(self, options: List[tuple[str, Optional[Any]]]):
        for string, obj in options:
            self._data.append(obj)
            self.addItem(string, obj)
            
    def replace_options(self, options: List[tuple[str, Optional[Any]]]):
        self.clear()
        self._data = []
        self.add_options(options)

    @property
    def current_data(self) -> Any:
        # custom property because currentData returning string instead of object
        index = self.currentIndex()
        return self._data[index]

class Label(QLabel):
    def __init__(self, 
                 text: str = "",
                 point_size: int = 9,
                 is_bold: bool = False):
        super().__init__()
        self.setText(text)
        font = self.font()
        font.setBold(is_bold)
        font.setPointSize(point_size)
        self.setFont(font)
        # self.setMinimumWidth(1)

    def set_word_wrap(self, val: bool) -> 'Label':
        self.setWordWrap(val)
        return self

    def set_text(self, text: str):
        self.setText(text)
        
class RBoldLabel(Label):
    def __init__(self, 
                 text: str):
        super().__init__(text, is_bold=True)
        
class RHeaderLabel(Label):
    def __init__(self, 
                 text: str):
        super().__init__(text, point_size=12, is_bold=True)
class ScrollArea(QScrollArea):
    def __init__(self,
                 widget: RWidget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(widget)

class PushButton(QPushButton):
    def __init__(self, 
                 text: Optional[str], 
                 triggered_fn: Callable[[], None], 
                 tooltip: Optional[str] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.set_text(text)
        self.clicked.connect(self._triggered)
        self.setToolTip(tooltip)
        
    def _triggered(self):
        self._triggered_fn()

    def set_text(self, text: Optional[str]):
        self.setText(text)

class RActionMenuItem(QAction):
    def __init__(self,
                 text: str,
                 triggered_fn: Callable[[], None]):
        super().__init__(text)
        self._triggered_fn = triggered_fn
        self.triggered.connect(self._triggered)
        
    def _triggered(self):
        self._triggered_fn()
        
class RMenuListBuilder(QMenu):
    def __init__(self, 
                 text: Optional[str] = None, 
                 actions: List[QAction] = []):
        super().__init__(text)
        self._items: List[QAction] = []
        self._menus: List[QMenu] = []
        self.add_actions(actions)
    
    def add_actions(self, actions: List[QAction]) -> 'RMenuListBuilder':
        for a in actions:
            self.add_action(a)
        return self
    
    def add_action(self, action: QAction) -> 'RMenuListBuilder':
        self._items.append(action)
        self.addAction(action) # type: ignore
        return self
    
    def add_separator(self) -> 'RMenuListBuilder':
        self.addSeparator()
        return self
    
    def add_menus(self, menus: List[QMenu]) -> 'RMenuListBuilder':
        for m in menus:
            self.addMenu(m)
            self._menus.append(m)
        return self
    
    def exec_menu(self, point: QPoint):
        self.exec(point)
    
class RMenuBarBuilder(QMenuBar):
    def __init__(self,
                 menus: List[Optional[QMenu]] = []):
        super().__init__()
        self._menus: List[QMenu] = []
        self.add_menus(menus)
        self.setNativeMenuBar(False)
    
    def add_menus(self, menus: List[Optional[QMenu]]) -> 'RMenuBarBuilder':
        for m in menus:
            if m is None:
                continue
            self._menus.append(m)
            self.addMenu(m)
        return self
    
    def add_separator(self) -> 'RMenuBarBuilder':
        self.addSeparator()
        return self

    def set_to_window(self, window: QMainWindow) -> 'RMenuBarBuilder':
        self.setParent(window)
        window.setMenuBar(self)
        return self


class LineEditInt(QLineEdit):
    def __init__(self,
                 int: Optional[int] = None, 
                 triggered_fn: Optional[Callable[[int], None]] = None,
                 placeholder_text: Optional[str] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.setValidator(QIntValidator())
        self.setPlaceholderText(placeholder_text)
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

class LineEditFloat(QLineEdit):
    def __init__(self,
                 int: Optional[float] = None, 
                 triggered_fn: Optional[Callable[[float], None]] = None,
                 placeholder_text: Optional[str] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.setValidator(QDoubleValidator())
        self.setPlaceholderText(placeholder_text)
        self.set_value(int)
        self.textChanged.connect(self._triggered)
        
    def _triggered(self, text: str):
        try:
            value = float(text)
            if self._triggered_fn is not None:
                self._triggered_fn(value)
        except:
            pass
        
    @property
    def value(self) -> Optional[float]:
        try:
            return float(self.text())
        except:
            pass
        
    def set_value(self, int: Optional[float]):
        if int is None:
            return
        self.setText(str(int))

        
class LineEditText(QLineEdit):
    def __init__(self,
                 text: Optional[str] = None, 
                 triggered_fn: Optional[Callable[[str], None]] = None, 
                 placeholder_text: Optional[str] = None):
        super().__init__()
        self._triggered_fn = triggered_fn
        self.set_value(text)
        self.setPlaceholderText(placeholder_text)
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

class HorizontalLabeledInputRow(RWidget):
    def __init__(self, 
                 text: str,
                 input: RWidget,
                 description: Optional[str] = None):
        super().__init__()
        self._text_label = Label(text)
        self._layout = HorizontalBoxLayout([
            VerticalBoxLayout([
               self._text_label,
            #    Label("descriptions are there to be for the benefit of us")
            ]).set_uniform_content_margins(0),
            
            input
        ], [None, 1]).set_layout_to_widget(self)

    def set_uniform_content_margins(self, margin: int) -> 'HorizontalLabeledInputRow':
        return self.set_content_margins(margin, margin, margin, margin)
    
    def set_word_wrap(self, is_word_wrap: bool) -> 'HorizontalLabeledInputRow':
        self._text_label.set_word_wrap(is_word_wrap)
        return self

    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'HorizontalLabeledInputRow':
        self._layout.setContentsMargins(left, top, right, bottom)
        return self

class VerticalLabeledInputRow(RWidget):
    def __init__(self, 
                 text: str,
                 input: RWidget, 
                 description: Optional[str] = None):
        super().__init__()
        VerticalBoxLayout([
               Label(text),
            #    Label("descriptions are there to be for the benefit of us")
            
            input
        ]).set_layout_to_widget(self)

class VerticalGroupBox(QGroupBox):
    def __init__(self, initial_widgets: List[RWidget] = []):
        super().__init__()
        self._layout = VerticalBoxLayout(initial_widgets).set_layout_to_widget(self)
    
    def add_widgets(self, widgets: List[RWidget]):
        self._layout.add_widgets(widgets)
            
    def replace_all_widgets(self, widgets: List[RWidget]):
        self._layout.replace_all_widgets(widgets)
        
    def set_alignment_top(self) -> 'VerticalGroupBox':
        self._layout.set_alignment_top()
        return self
    
    def add_spacer(self, spacer_item: QSpacerItem) -> 'VerticalGroupBox':
        self._layout.add_spacer(spacer_item)
        return self


class RTabWidget(RWidget):
    def __init__(self, 
                 tabs: List[tuple[RWidget, str]] = [], 
                 tab_change_fn: Optional[Callable[[int], None]] = None):
        super().__init__()
        self._tab_change_fn = tab_change_fn
        self._tab_widget = QTabWidget()
        self._tab_widget.currentChanged.connect(self._tab_changed)
        self._layout = VerticalBoxLayout([self._tab_widget]).set_layout_to_widget(self)
        self._widgets: List[RWidget] = []
        self.add_tabs(tabs)
    
    def set_current_index(self, index: int):
        if index < len(self._widgets):
            self._tab_widget.setCurrentIndex(index)

    @property
    def current_index(self) -> int:
        return self._tab_widget.currentIndex()

    def add_tabs(self, tabs: List[tuple[RWidget, str]]):
        for t in tabs:
            self._widgets.append(t[0])
            self._tab_widget.addTab(t[0], t[1])
    
    def _tab_changed(self, index: int):
        if self._tab_change_fn is not None:
            self._tab_change_fn(index)
        
    def set_layout_to_widget(self, layout: RWidget) -> 'RWidget':
        layout.setLayout(self.layout())
        return self
    

class RSpacer(QSpacerItem):
    def __init__(self, width: int, height: int, h_policy: QSizePolicy.Policy, v_policy: QSizePolicy.Policy):
        super().__init__(width, height, h_policy, v_policy)
        pass

class RVerticallyExpandingSpacer(RSpacer):
    def __init__(self, width: int = 0, height: int = 0):
        super().__init__(width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        pass
        
class RHorizontallyExpandingSpacer(RSpacer):
    def __init__(self, width: int = 0, height: int = 0):
        super().__init__(width, height, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        pass