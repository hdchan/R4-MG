from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from ...AppDependencyProviding import AppDependencyProviding


class ShortcutsViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependencyProviding):
        super().__init__()
        self.setWindowTitle("Shortcuts")
        self.setMinimumSize(400, 300)
        self.asset_provider = app_dependencies_provider.asset_provider
        
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)
        
        with open(app_dependencies_provider.asset_provider.text.shortcuts_path, 'r') as file:
            data = file.read()
        markdown = QTextEdit()
        markdown.setMarkdown(data)
        markdown.setReadOnly(True)
        v_layout.addWidget(markdown)