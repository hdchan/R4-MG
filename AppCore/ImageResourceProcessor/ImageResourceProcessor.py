import os
from pathlib import Path
from typing import Callable, List, Optional, Set, Tuple, TypeVar

from PIL import Image, ImageDraw, ImageFile
from PySide6.QtCore import QMutex, QRunnable, QThreadPool

from AppCore.ImageFetcher.ImageFetcherProvider import (
    ImageFetcherProtocol,
    ImageFetcherProviding,
)
from AppCore.Models import LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Service.GeneralWorker import GeneralWorker, WorkerSignals

from .Events.LocalCardResourceFetchEvent import LocalCardResourceFetchEvent
from .ImageResourceProcessorProtocol import (
    ImageResourceProcessorProtocol,
    ImageResourceProcessorProviding,
)

THUMBNAIL_SIZE = 256
ROUNDED_CORNERS = 30
NORMAL_CARD_HEIGHT = 468
ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT = ROUNDED_CORNERS / NORMAL_CARD_HEIGHT

ImageDownscaleCallback = Callable[[Image.Image], Image.Image]
ImageAddCornersCallback = Callable[[Image.Image, int], Image.Image]

T = TypeVar("T")

# hopefully this is safe
# prevents error being throw when retrieving image from importer
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _down_scale_image(original_img: Image.Image, max_size: float) -> Image.Image:
    # TODO: recover from truncated image
    preview_img = original_img.copy().convert('RGBA')
    # prevent lower than thumbnail size
    downscaled_size = max_size
    if downscaled_size < THUMBNAIL_SIZE:
        downscaled_size = THUMBNAIL_SIZE
    preview_img.thumbnail(
        (downscaled_size, downscaled_size), Image.Resampling.BICUBIC)
    return preview_img


def _add_corners(im: Image.Image, rad: int) -> Image.Image:
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

# This is placed outside the scope of a class because multiprocessing requires a function to be pickle-able, which is difficult to do for image resource processor


def _process(resource: LocalCardResource, image_fetcher: ImageFetcherProtocol):
    Path(resource.image_dir).mkdir(parents=True, exist_ok=True)
    Path(resource.image_preview_dir).mkdir(parents=True, exist_ok=True)
    # generate 0kb file before notification
    open(resource.image_temp_path, 'a').close()
    if not resource.is_ready:
        img = image_fetcher.fetch(resource)
        img_height = min(img.height, img.width)
        rad = int(img_height * ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT)
        large_img = _add_corners(img.convert('RGB'), rad)
        large_img.save(resource.image_path)
        preview_img = _down_scale_image(large_img, THUMBNAIL_SIZE)
        preview_img.save(resource.image_preview_path)
    elif not resource.is_preview_ready:
        with Image.open(resource.image_path) as large_img:
            preview_img = _down_scale_image(large_img, THUMBNAIL_SIZE)
            preview_img.save(resource.image_preview_path)
    if os.path.exists(resource.image_temp_path):
        # prevent call to deletion from two successive calls
        Path(resource.image_temp_path).unlink()  # unlink before notification


class ImageResourceProcessor(ImageResourceProcessorProtocol, ImageResourceProcessorProviding):
    def __init__(self,
                 image_fetcher_provider: ImageFetcherProviding,
                 observation_tower: ObservationTower):
        self.observation_tower = observation_tower
        self.image_fetcher_provider = image_fetcher_provider
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[str] = set()
        self.workers: Set[QRunnable] = set()

    @property
    def image_resource_processor(self) -> 'ImageResourceProcessor':
        return self

    def async_store_local_resources_multi(self, local_resources: List[LocalCardResource], completed: Callable[[], None]) -> None:
        # TODO: handle failure
        # TODO: should it be not (is_ready, etc..)?
        # only process the ones that we need to
        filtered_resources = list(
            filter(lambda x: not x.is_ready or x.is_preview_ready, local_resources))
        self.mutex.lock()
        for resource in filtered_resources:
            self.working_resources.add(resource.image_path)
        self.mutex.unlock()

        def _finished():
            self.mutex.lock()
            for resource in filtered_resources:
                if resource.image_path in self.working_resources:
                    self.working_resources.remove(resource.image_path)
            self.mutex.unlock()
            completed()

        def _cleanup(identifier: QRunnable):
            self.workers.remove(identifier)

        def _runnable_fn():
            for r in filtered_resources:
                _process(r, self.image_fetcher_provider.image_fetcher)

        worker = GeneralWorker(_runnable_fn)
        worker.signals.finished.connect(_finished)
        worker.signals.cleanup.connect(_cleanup)
        self.workers.add(worker)
        self.pool.start(worker)

    def async_store_local_resource(self, local_resource: LocalCardResource, retry: bool = False, is_async: bool = True):
        # TODO: implement stale cache
        if retry and local_resource.remote_image_url is not None:
            # We should maybe guard against retry if no internet connection?
            # prevent deletion of resources that don't have any remote URL
            assert (local_resource.remote_image_url is not None)
            if os.path.exists(local_resource.image_path):
                Path(local_resource.image_path).unlink()
            if os.path.exists(local_resource.image_preview_path):
                Path(local_resource.image_preview_path).unlink()

        if local_resource.is_ready or local_resource.is_local_only:
            # regenerate preview image if needed
            if not local_resource.is_preview_ready and local_resource.is_ready:
                self.regenerate_resource_preview(local_resource)
            return

        assert (not local_resource.is_ready)
        assert (not local_resource.is_local_only)

        Path(local_resource.image_dir).mkdir(parents=True, exist_ok=True)
        Path(local_resource.image_preview_dir).mkdir(
            parents=True, exist_ok=True)
        # create temp file for loading state
        # prevent multiple jobs from running on the same resource
        worker = StoreImageWorker(local_resource,
                                  self.image_fetcher_provider,
                                  self._generate_preview_image,
                                  self._add_corners)

        if not is_async:  # TODO: remove force sync
            self._lock_resource_and_notify(local_resource)
            worker.run()
            self._unlock_resource_and_notify((local_resource, None))
            return

        if self._lock_resource_and_notify(local_resource):
            def _cleanup(identifier: QRunnable):
                self.workers.remove(identifier)

            worker = StoreImageWorker(local_resource,
                                      self.image_fetcher_provider,
                                      self._generate_preview_image,
                                      self._add_corners)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            worker.signals.cleanup.connect(_cleanup)
            self.workers.add(worker)
            self.pool.start(worker)

    def rotate_and_save_resource(self, local_resource: LocalCardResource, angle: float):
        if self._lock_resource_and_notify(local_resource):
            def _cleanup(identifier: QRunnable):
                self.workers.remove(identifier)

            worker = RotateImageWorker(local_resource, angle)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            worker.signals.cleanup.connect(_cleanup)
            self.workers.add(worker)
            self.pool.start(worker)

    def regenerate_resource_preview(self, local_resource: LocalCardResource):
        if self._lock_resource_and_notify(local_resource):
            def _cleanup(identifier: QRunnable):
                self.workers.remove(identifier)

            # should lock UI incase another job is added
            worker = RegenerateImageWorker(
                local_resource, self._generate_preview_image)
            worker.signals.finished.connect(self._unlock_resource_and_notify)
            worker.signals.cleanup.connect(_cleanup)
            self.workers.add(worker)
            self.pool.start(worker)

    def _lock_resource_and_notify(self, local_resource: LocalCardResource) -> bool:
        if local_resource.image_path in self.working_resources:
            return False
        self.mutex.lock()
        self.working_resources.add(local_resource.image_path)
        self.mutex.unlock()
        Path(local_resource.image_preview_dir).mkdir(
            parents=True, exist_ok=True)  # ensure directory exists
        # generate 0kb file before notification
        open(local_resource.image_temp_path, 'a').close()
        self.observation_tower.notify(LocalCardResourceFetchEvent(
            LocalCardResourceFetchEvent.EventType.STARTED, local_resource))
        return True

    def _unlock_resource_and_notify(self, result: Tuple[LocalCardResource, Optional[Exception]]):
        local_resource, exception = result
        if os.path.exists(local_resource.image_temp_path):
            # prevent call to deletion from two successive calls
            # unlink before notification
            Path(local_resource.image_temp_path).unlink()
        if local_resource.image_path in self.working_resources:
            self.mutex.lock()
            self.working_resources.remove(local_resource.image_path)
            self.mutex.unlock()
        if exception is not None:
            self.observation_tower.notify(LocalCardResourceFetchEvent(
                LocalCardResourceFetchEvent.EventType.FAILED, local_resource))
        else:
            self.observation_tower.notify(LocalCardResourceFetchEvent(
                LocalCardResourceFetchEvent.EventType.FINISHED, local_resource))

    def _generate_preview_image(self, original_img: Image.Image) -> Image.Image:
        return self.down_scale_image(original_img, THUMBNAIL_SIZE)

    def down_scale_image(self, original_img: Image.Image, max_size: float) -> Image.Image:
        return _down_scale_image(original_img, max_size)

    def generate_placeholder(self, local_resource: LocalCardResource, placeholder_image_path: Optional[str]):
        existing_file = Path(local_resource.image_path)
        if existing_file.is_file():
            raise Exception(
                f"File already exists: {local_resource.file_name_with_ext}")

        Path(local_resource.image_dir).mkdir(parents=True, exist_ok=True)

        img = Image.new("RGB", (1, 1))
        if placeholder_image_path is not None:
            try:
                with Image.open(placeholder_image_path) as opened_img:
                    # .load() pulls the data into RAM so the file can be closed
                    opened_img.load()
                    img = opened_img.copy()
            except Exception as e:
                pass
        img.save(local_resource.image_path, "PNG")

        Path(local_resource.image_preview_dir).mkdir(
            parents=True, exist_ok=True)
        preview_img = self._generate_preview_image(img)
        preview_img.save(local_resource.image_preview_path, "PNG")

    def _add_corners(self, im: Image.Image, rad: int) -> Image.Image:
        return _add_corners(im, rad)


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
                img = self.image_fetcher_provider.image_fetcher.fetch(
                    self.local_resource)
                img_height = min(img.height, img.width)
                rad = int(
                    img_height * ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT)
                large_img = self.add_corners_fn(img.convert('RGB'), rad)
                preview_img = self.downscale_fn(large_img)
                large_img.save(self.local_resource.image_path)
                preview_img.save(self.local_resource.image_preview_path)
                self.signals.finished.emit((self.local_resource, None))
            except Exception as error:
                self.signals.finished.emit((self.local_resource, error))
            finally:
                self.signals.cleanup.emit(self)
        else:
            self.signals.finished.emit(
                (self.local_resource, Exception('No image url')))
            self.signals.cleanup.emit(self)


class RegenerateImageWorker(QRunnable):
    def __init__(self,
                 local_resource: LocalCardResource,
                 downscale_fn: ImageDownscaleCallback):
        super(RegenerateImageWorker, self).__init__()
        self.local_resource = local_resource
        self.downscale_fn = downscale_fn
        self.signals = WorkerSignals()

    def run(self):
        try:
            # Use 'with' to ensure the file handle is closed as soon as the block ends
            with Image.open(self.local_resource.image_path) as img:
                # .load() forces Pillow to read the pixel data into memory
                img.load()
                # Pass the loaded image to your downscale function
                preview_img = self.downscale_fn(img)

            # The file handle for image_path is now officially CLOSED here.
            # You can now safely save, delete, or overwrite the original file.
            preview_img.save(self.local_resource.image_preview_path)

            self.signals.finished.emit((self.local_resource, None))
        except Exception as e:
            # It's good practice to emit an error signal if something fails
            print(f"Error regenerating image: {e}")
        finally:
            self.signals.cleanup.emit(self)


class RotateImageWorker(QRunnable):
    def __init__(self,
                 local_resource: LocalCardResource,
                 angle: float):
        super(RotateImageWorker, self).__init__()
        self.local_resource = local_resource
        self.angle = angle
        self.signals = WorkerSignals()

    def run(self):
        try:
            # Rotate the main image
            with Image.open(self.local_resource.image_path) as img:
                # Load into RAM and rotate
                rotated_main = img.rotate(
                    self.angle, resample=Image.Resampling.BICUBIC, expand=True)
                rotated_main.load()
            # File is closed here; safe to overwrite
            rotated_main.save(self.local_resource.image_path)

            # Rotate the preview image
            with Image.open(self.local_resource.image_preview_path) as prev_img:
                rotated_prev = prev_img.rotate(
                    self.angle, resample=Image.Resampling.BICUBIC, expand=True)
                rotated_prev.load()
            # File is closed here; safe to overwrite
            rotated_prev.save(self.local_resource.image_preview_path)

            self.signals.finished.emit((self.local_resource, None))
        except Exception as e:
            print(f"Rotation error: {e}")
        finally:
            self.signals.cleanup.emit(self)
