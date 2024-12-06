from PyQt5.QtWidgets import QWidget

class ComponentProviding:
    @property
    def about_view(self) -> QWidget:
        return NotImplemented
    
    @property
    def settings_view(self) -> QWidget:
        return NotImplemented