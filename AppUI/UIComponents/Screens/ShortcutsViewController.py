from PySide6.QtWidgets import QTextEdit

from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import RTabWidget, RWidget, VerticalBoxLayout


class ShortcutsViewController(RWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self.setWindowTitle("Quick Guide")
        self.setMinimumSize(400, 400)
        self.asset_provider = app_dependencies_provider.asset_provider
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        
        with open(app_dependencies_provider.asset_provider.text.shortcuts_path, 'r', encoding='utf-8') as file:
            data = file.read()
        markdown = QTextEdit()
        markdown.setMarkdown(data)
        markdown.setReadOnly(True)
        
        tab_widget = RTabWidget([
                (markdown, "Shortcuts")
            ])

        VerticalBoxLayout([
            tab_widget
        ]).set_layout_to_widget(self)

        additional_quick_guide = self._external_app_dependencies_provider.provide_additional_quick_guide()
        if additional_quick_guide is not None:
            tab_widget.add_tabs([
                (additional_quick_guide, "Misc")
            ])