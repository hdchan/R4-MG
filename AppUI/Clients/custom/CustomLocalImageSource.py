from AppCore.Resource.CardImageSourceProtocol import LocalCardImageSourceProtocol
from PyQt5.QtCore import QStandardPaths

class CustomLocalImageSource(LocalCardImageSourceProtocol):
    @property
    def source_label_display(self) -> str:
        return "NotImplemented"
    
    @property
    def image_path(self) -> str:
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/R4-MG/custom/'
    
    @property
    def image_preview_dir(self) -> str:
        return f'{self.image_path}preview/'