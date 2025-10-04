import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
class AssetProvider:
    class Text:
        @property
        def shortcuts_path(self) -> str:
            return self._text_path('shortcuts.md')

        def _text_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Text/{file_name}')
    class Image:
        
        def _image_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Images/{file_name}')
        
    
    class Data:
        
        def _data_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Data/{file_name}')
    
    class Fonts:
        
        def _fonts_path(self, file_name: str) -> str:
            return os.path.join(APP_DIR, f'Fonts/{file_name}')
    
    def __init__(self):
        self.text = self.Text()
        self.image = self.Image()
        self.data = self.Data()
        self.fonts = self.Fonts()