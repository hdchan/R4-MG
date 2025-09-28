from PyQt5.QtWidgets import QTextEdit, QWidget

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from R4UI import VerticalBoxLayout


class ShortcutsViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self.setWindowTitle("Quick Guide")
        self.setMinimumSize(400, 650)
        self.asset_provider = app_dependencies_provider.asset_provider
        
        with open(app_dependencies_provider.asset_provider.text.shortcuts_path, 'r', encoding='utf-8') as file:
            data = file.read()
        markdown = QTextEdit()
        markdown.setMarkdown(data)
        markdown.setReadOnly(True)
        
        VerticalBoxLayout([
            markdown
        ]).set_layout_to_widget(self)