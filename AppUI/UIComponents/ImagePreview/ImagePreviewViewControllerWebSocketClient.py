from typing import Optional

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QPixmap

from AppCore.Config import Configuration
from AppCore.Models import LocalCardResource
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from R4UI import Label, RWidget, VerticalBoxLayout

from ..Base.LoadingSpinner import LoadingSpinner

MAX_PREVIEW_SIZE = 256

class ImagePreviewViewControllerWebSocketClient(RWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._local_resource: Optional[LocalCardResource] = None
        self._setup_view()

    def _setup_view(self):
        self._image_view = Label()
        self._image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_spinner = LoadingSpinner(self._image_view)
        VerticalBoxLayout([
            self._image_view
        ]).set_layout_to_widget(self)

    def set_image(self, local_resource: LocalCardResource):
        self._local_resource = local_resource
        self._sync_image_view_state()

    def clear_image(self):
        self._local_resource = None
        self._image_view.clear()
        self._sync_image_view_state()

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def _sync_image_view_state(self):
        if self._local_resource is None:
            self.loading_spinner.stop()
            image = QPixmap()
            success = image.load(
                self._external_app_dependencies_provider.image_preview_logo_path)
            if success:
                # TODO: consolidate with image logic below
                image_width = image.size().width()
                image_height = image.size().height()
                multiplier = MAX_PREVIEW_SIZE / \
                    max(image_width, image_height)
                multiplier *= self._configuration.image_preview_scale * \
                    0.5  # normal should be smaller
                final_width, final_height = int(
                    image_width * multiplier), int(image_height * multiplier)
                self._image_view.setMinimumSize(final_width, final_height)
                scaled_image = image.scaled(
                    final_width, final_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self._image_view.setPixmap(scaled_image)
            else:
                self._image_view.setText('[Placeholder]')
        else:
            if self._local_resource.image_preview_binary is not None:
                # giving binary image previews priority if from web socket
                image = QPixmap()
                # binary = self._local_resource.image_preview_binary.getvalue()
                # byte_array = QByteArray(binary)
                # success = image.loadFromData(byte_array)
                binary = self._local_resource.image_preview_binary
                if hasattr(binary, 'getvalue'):
                    binary = binary.getvalue()
                if image.loadFromData(binary):
                    image_width = image.size().width()
                    image_height = image.size().height()
                    multiplier = MAX_PREVIEW_SIZE / \
                        max(image_width, image_height)
                    multiplier *= self._configuration.image_preview_scale
                    final_width, final_height = int(
                        image_width * multiplier), int(image_height * multiplier)
                    self._image_view.setMinimumSize(final_width, final_height)
                    scaled_image = image.scaled(
                        final_width, final_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self._image_view.setPixmap(scaled_image)
                    
                    self.loading_spinner.stop()
                    return
            self._image_view.clear()
            self.loading_spinner.start()
