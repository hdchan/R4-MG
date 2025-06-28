from PyQt5.QtWidgets import QWidget
from PyQtUI import VerticalBoxLayout, HorizontalBoxLayout, PushButton

# class SettingsApplicableViewControllerProtocol:
#     def _will_apply

class SettingsContainerViewController(QWidget):
    def __init__(self):
        super().__init__()
        VerticalBoxLayout([
            HorizontalBoxLayout([
                PushButton("Apply", self._apply),
                PushButton("Save && Close", self._save_and_close)
            ])
        ]).set_to_layout(self)
        
    def _apply(self):
        pass
    
    def _save_and_close(self):
        self._apply()
        self.close()