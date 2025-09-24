from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QSpacerItem,
                             QVBoxLayout, QWidget, QBoxLayout)

class BoxLayout(QWidget):
    def __init__(self, 
                 layout: QBoxLayout,  
                 widgets: List[QWidget] = []):
        super().__init__()
        self._widgets: List[QWidget] = []
        self._layout = layout
        self.setLayout(self._layout)
        self.add_widgets(widgets)
    
    def set_alignment_for_all_widgets(self, alignment: Qt.AlignmentFlag) -> 'BoxLayout':
        for w in self._widgets:
            self._layout.setAlignment(w, alignment)
        return self
            
    def set_alignment_top(self) -> 'BoxLayout':
        return self.set_alignment_for_all_widgets(Qt.AlignmentFlag.AlignTop)
    
    def add_widgets(self, widgets: List[QWidget]):
        for w in widgets:
            self.add_widget(w)
            
    def add_widget(self, widget: QWidget):
        self._widgets.append(widget)
        self._layout.addWidget(widget)
    
    def add_spacer(self, spacer_item: QSpacerItem) -> 'BoxLayout':
        self._layout.addSpacerItem(spacer_item)
        return self
        
    def set_to_layout(self, layout: QWidget) -> 'BoxLayout':
        layout.setLayout(self.layout())
        return self
    
    def set_spacing(self, spacing: int) -> 'BoxLayout':
        self._layout.setSpacing(spacing)
        return self
    
    def set_uniform_content_margins(self, margin: int) -> 'BoxLayout':
        return self.set_content_margins(margin, margin, margin, margin)
    
    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'BoxLayout':
        self._layout.setContentsMargins(left, top, right, bottom)
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
                    
    def replace_all_widgets(self, widgets: List[QWidget]):
        self._clear_widgets()
        self.add_widgets(widgets)
    
    def insert_widget(self, index: int, widget: QWidget):
        self._layout.insertWidget(index, widget)
     
    def remove_widget_at_index(self, index_to_remove: int):
        if self._layout.count() > index_to_remove:
            # takeAt() removes the QLayoutItem at the specified index
            # and returns it.
            item = self._layout.takeAt(index_to_remove)

            if item is not None:
                widget = item.widget()
                if widget is not None:
                    # It's good practice to call deleteLater() to properly
                    # destroy the widget and free its resources.
                    widget.deleteLater()
                    # You might also want to remove it from your internal list
                    # if you're tracking widgets this way.
                    if widget in self._widgets:
                        self._widgets.remove(widget)
    
    def swap_widgets(self, index_1: int, index_2: int):
        # Remove widgets
        item_1 = self._layout.takeAt(index_1)
        item_2 = self._layout.takeAt(index_2)

        # Insert widgets at swapped positions
        # Note: When an item is removed, subsequent indices shift.
        # It's safer to insert at the original indices after removal,
        # or adjust indices if inserting before a removed item.
        # In this case, since we're swapping two specific items,
        # inserting at their *original* positions (which are now effectively empty) works.
        self._layout.insertItem(index_1, item_2)
        self._layout.insertItem(index_2, item_1)

class HorizontalBoxLayout(BoxLayout):
    def __init__(self, widgets: List[QWidget] = []):
        super().__init__(QHBoxLayout(), widgets)
        pass
    
            
class VerticalBoxLayout(BoxLayout):
    def __init__(self, widgets: List[QWidget] = []):
        super().__init__(QVBoxLayout(), widgets)
        pass

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
                    
    def replace_all_widgets(self, widgets: List[tuple[QWidget, tuple[int, int]]]):
        self._clear_widgets()
        self.add_widgets(widgets)
        
    def set_to_layout(self, layout: QWidget) -> 'GridLayout':
        layout.setLayout(self.layout())
        return self
    
    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> 'HorizontalBoxLayout':
        self._layout.setContentsMargins(left, top, right, bottom)
        return self