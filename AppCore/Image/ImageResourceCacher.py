import os
from functools import partial
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from ..Models import LocalCardResource
from ..Observation import ObservationTower
from ..Observation.Events import LocalResourceEvent
from ..ImageNetwork.ImageFetcherProvider import ImageFetcherProviderProtocol

PNG_EXTENSION = '.png'
THUMBNAIL_SIZE = 256
ROUNDED_CORNERS = 25
NORMAL_CARD_HEIGHT = 468
NORMAL_CARD_WIDTH = 652
ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT = ROUNDED_CORNERS / NORMAL_CARD_HEIGHT

class ImageResourceCacherDelegate:
    def rc_did_finish_storing_local_resource(self, rc: ..., local_resource: LocalCardResource) -> None:
        pass

class ImageResourceCacher:
    def __init__(self,
                 image_fetcher_provider: ImageFetcherProviderProtocol,
                 observation_tower: ObservationTower):
        self.observation_tower = observation_tower
        self.image_fetcher_provider = image_fetcher_provider
        self.pool = QThreadPool()
        self.delegate: Optional[ImageResourceCacherDelegate]

    def async_store_local_resource(self, local_resource: LocalCardResource, retry: bool = False):
        if retry:
            if os.path.exists(local_resource.image_path):
                Path(local_resource.image_path).unlink()
            if os.path.exists(local_resource.image_preview_path):
                Path(local_resource.image_preview_path).unlink()
        if local_resource.is_ready:
            return
        # TODO: might need to prevent duplicate calls?
        # https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
        
        Path(local_resource.image_dir).mkdir(parents=True, exist_ok=True)
        Path(local_resource.image_preview_dir).mkdir(parents=True, exist_ok=True)
        # create temp file for loading state
        img = Image.new("RGB", (1, 1))
        img.save(f"{local_resource.image_temp_path}", "PNG") # generate before notification
        
        self.observation_tower.notify(LocalResourceEvent(LocalResourceEvent.EventType.STARTED, local_resource))
        
        worker = StoreImageWorker(local_resource, self.image_fetcher_provider)
        worker.signals.finished.connect(partial(self._finish_storing_local_resource))
        self.pool.start(worker)

    def _finish_storing_local_resource(self, result: Tuple[LocalCardResource, Optional[Exception]]):
        local_resource, exception = result
        Path(local_resource.image_temp_path).unlink() # unlink before notification
        if exception is not None:
            self.observation_tower.notify(LocalResourceEvent(LocalResourceEvent.EventType.FAILED, local_resource))
        else:
            self.observation_tower.notify(LocalResourceEvent(LocalResourceEvent.EventType.FINISHED, local_resource))
        if self.delegate is not None:
            self.delegate.rc_did_finish_storing_local_resource(self, local_resource)


# https://stackoverflow.com/questions/13909195/how-run-two-different-threads-simultaneously-in-pyqt
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class StoreImageWorker(QRunnable):
    def __init__(self, 
                 local_resource: LocalCardResource,
                 image_fetcher_provider: ImageFetcherProviderProtocol):
        super(StoreImageWorker, self).__init__()
        self.local_resource = local_resource
        self.image_fetcher_provider = image_fetcher_provider
        self.signals = WorkerSignals()

    def run(self):
        self.store_local_resource(self.local_resource)

    def store_local_resource(self, local_resource: LocalCardResource):
        if local_resource.remote_image_url is not None:
            try:
                img = self.image_fetcher_provider.provideImageFetcher().fetch(local_resource.remote_image_url)
                img_height = min(img.height, img.width)
                rad = int(img_height * ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT)
                # TODO: rounded rect needs to be propotional to size of image
                large_img = self._add_corners(img.convert('RGB'), rad)
                preview_img = self._downscale_image(large_img)
                large_img.save(local_resource.image_path)
                preview_img.save(local_resource.image_preview_path)
                self.signals.finished.emit((local_resource, None))
            except Exception as error:
                self.signals.finished.emit((local_resource, error))

    def _downscale_image(self, original_img: Image.Image) -> Image.Image:
        size = THUMBNAIL_SIZE, THUMBNAIL_SIZE
        preview_img = original_img.copy().convert('RGBA')
        preview_img.thumbnail(size)
        return preview_img

    def _add_corners(self, im: Image.Image, rad: int) -> Image.Image:
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im