import os
from pathlib import Path
from typing import Callable, Optional, Set, Tuple

from PIL import Image, ImageDraw
from PyQt5.QtCore import QMutex, QObject, QRunnable, QThreadPool, pyqtSignal

from ..ImageNetwork.ImageFetcherProvider import ImageFetcherProviding
from ..Models import LocalCardResource
from ..Observation import ObservationTower
from ..Observation.Events import LocalResourceFetchEvent
from .ImageResourceProcessorProtocol import ImageResourceProcessorProtocol

PNG_EXTENSION = '.png'
THUMBNAIL_SIZE = 256
ROUNDED_CORNERS = 25
NORMAL_CARD_HEIGHT = 468
NORMAL_CARD_WIDTH = 652
ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT = ROUNDED_CORNERS / NORMAL_CARD_HEIGHT

ImageDownscaleCallback = Callable[[Image.Image], Image.Image]
ImageAddCornersCallback = Callable[[Image.Image, int], Image.Image]

class ImageResourceProcessor(ImageResourceProcessorProtocol):
    def __init__(self,
                 image_fetcher_provider: ImageFetcherProviding,
                 observation_tower: ObservationTower):
        self.observation_tower = observation_tower
        self.image_fetcher_provider = image_fetcher_provider
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[str] = set()

    def async_store_local_resource(self, local_resource: LocalCardResource, retry: bool = False):
        # TODO: implement stale cache
        if retry and local_resource.remote_image_url is not None:
            assert(local_resource.remote_image_url is not None) # prevent deletion of resources that don't have any remote URL
            if os.path.exists(local_resource.image_path):
                Path(local_resource.image_path).unlink()
            if os.path.exists(local_resource.image_preview_path):
                Path(local_resource.image_preview_path).unlink()
        if local_resource.is_ready:
            return
        
        Path(local_resource.image_dir).mkdir(parents=True, exist_ok=True)
        Path(local_resource.image_preview_dir).mkdir(parents=True, exist_ok=True)
        # create temp file for loading state
        # prevent multiple jobs from running on the same resource
        if self._lock_resource_and_notify(local_resource):
            worker = StoreImageWorker(local_resource, 
                                    self.image_fetcher_provider, 
                                    self._downscale_image, 
                                    self._add_corners)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            self.pool.start(worker)

    def rotate_and_save_resource(self, local_resource: LocalCardResource, angle: float):
        if self._lock_resource_and_notify(local_resource):
            worker = RotateImageWorker(local_resource, angle)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            self.pool.start(worker)
    
    def regenerate_resource_preview(self, local_resource: LocalCardResource):
        if self._lock_resource_and_notify(local_resource):
            # should lock UI incase another job is added
            worker = RegenerateImageWorker(local_resource, self._downscale_image)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            self.pool.start(worker)

    def _lock_resource_and_notify(self, local_resource: LocalCardResource) -> bool:
        if local_resource.image_path in self.working_resources:
            return False
        self.mutex.lock()
        self.working_resources.add(local_resource.image_path)
        self.mutex.unlock()
        open(local_resource.image_temp_path, 'a').close() # generate 0kb file before notification
        self.observation_tower.notify(LocalResourceFetchEvent(LocalResourceFetchEvent.EventType.STARTED, local_resource))
        return True
        
    def _unlock_resource_and_notify(self, result: Tuple[LocalCardResource, Optional[Exception]]):
        local_resource, exception = result
        if os.path.exists(local_resource.image_temp_path):
            # prevent call to deletion from two successive calls
            Path(local_resource.image_temp_path).unlink() # unlink before notification
        if local_resource.image_path in self.working_resources:
            self.mutex.lock()
            self.working_resources.remove(local_resource.image_path)
            self.mutex.unlock()
        if exception is not None:
            self.observation_tower.notify(LocalResourceFetchEvent(LocalResourceFetchEvent.EventType.FAILED, local_resource))
        else:
            self.observation_tower.notify(LocalResourceFetchEvent(LocalResourceFetchEvent.EventType.FINISHED, local_resource))

    def _downscale_image(self, original_img: Image.Image) -> Image.Image:
        size = THUMBNAIL_SIZE, THUMBNAIL_SIZE
        # TODO: recover from truncated image
        preview_img = original_img.copy().convert('RGBA')
        preview_img.thumbnail(size, Image.Resampling.BICUBIC)
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

# https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
# https://stackoverflow.com/questions/13909195/how-run-two-different-threads-simultaneously-in-pyqt
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class StoreImageWorker(QRunnable):
    def __init__(self, 
                 local_resource: LocalCardResource,
                 image_fetcher_provider: ImageFetcherProviding, 
                 downscale_fn: ImageDownscaleCallback, 
                 add_corners_fn: ImageAddCornersCallback):
        super(StoreImageWorker, self).__init__()
        self.local_resource = local_resource
        self.image_fetcher_provider = image_fetcher_provider
        self.downscale_fn = downscale_fn
        self.add_corners_fn = add_corners_fn
        self.signals = WorkerSignals()

    def run(self):
        if self.local_resource.remote_image_url is not None:
            try:
                img = self.image_fetcher_provider.image_fetcher.fetch(self.local_resource.remote_image_url)
                img_height = min(img.height, img.width)
                rad = int(img_height * ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT)
                large_img = self.add_corners_fn(img.convert('RGB'), rad)
                preview_img = self.downscale_fn(large_img)
                large_img.save(self.local_resource.image_path)
                preview_img.save(self.local_resource.image_preview_path)
                self.signals.finished.emit((self.local_resource, None))
            except Exception as error:
                self.signals.finished.emit((self.local_resource, error))
        else:
            self.signals.finished.emit((self.local_resource, Exception('No image url')))

class RegenerateImageWorker(QRunnable):
    def __init__(self, local_resource: LocalCardResource, 
                 downscale_fn: ImageDownscaleCallback):
        super(RegenerateImageWorker, self).__init__()
        self.local_resource = local_resource
        self.downscale_fn = downscale_fn
        self.signals = WorkerSignals()

    def run(self):
        large_img = Image.open(self.local_resource.image_path)
        preview_img = self.downscale_fn(large_img)
        preview_img.save(self.local_resource.image_preview_path)
        self.signals.finished.emit((self.local_resource, None))

class RotateImageWorker(QRunnable):
    def __init__(self, local_resource: LocalCardResource, angle: float):
        super(RotateImageWorker, self).__init__()
        self.local_resource = local_resource
        self.angle = angle
        self.signals = WorkerSignals()
    
    def run(self):
        Image.open(self.local_resource.image_path).rotate(self.angle, resample=Image.Resampling.BICUBIC, expand=True).save(self.local_resource.image_path)
        Image.open(self.local_resource.image_preview_path).rotate(self.angle, resample=Image.Resampling.BICUBIC, expand=True).save(self.local_resource.image_preview_path)
        self.signals.finished.emit((self.local_resource, None))