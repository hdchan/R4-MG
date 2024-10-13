from functools import partial
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from ..Config import Configuration
from ..Models.TradingCard import LocalCardResource, TradingCard
from .ImageFetcherProvider import ImageFetcherProvider

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
                 image_fetcher_provider: ImageFetcherProvider, 
                 configuration: Configuration):
        self.configuration = configuration
        self.image_fetcher_provider = image_fetcher_provider
        self.pool = QThreadPool()
        self.delegate: Optional[ImageResourceCacherDelegate]

    def attach_local_resources(self, trading_card_list: List[TradingCard]):
        for trading_card in trading_card_list:
            image_path = f'{self.configuration.cache_file_path}{trading_card.unique_identifier_front}{PNG_EXTENSION}'
            image_preview_path = f'{self.configuration.cache_preview_file_path}{trading_card.unique_identifier_front}{PNG_EXTENSION}'
            
            front_local_resource = LocalCardResource(image_path, 
                                                    image_preview_path, 
                                                    trading_card.unique_identifier_front,
                                                    trading_card.friendly_display_name_front,
                                                    PNG_EXTENSION, 
                                                    trading_card.front_art)
            trading_card.front_art_resource = front_local_resource
            existing_file = Path(f'{self.configuration.cache_file_path}{trading_card.unique_identifier_front}{PNG_EXTENSION}')
            front_local_resource.is_ready = existing_file.is_file()
                
            
            if trading_card.back_art is not None:
                image_path = f'{self.configuration.cache_file_path}{trading_card.unique_identifier_back}{PNG_EXTENSION}'
                image_preview_path = f'{self.configuration.cache_preview_file_path}{trading_card.unique_identifier_back}{PNG_EXTENSION}'
                
                back_local_resource = LocalCardResource(image_path, 
                                                        image_preview_path, 
                                                        trading_card.unique_identifier_back,
                                                        trading_card.friendly_display_name_back,
                                                        PNG_EXTENSION, 
                                                        trading_card.back_art)
                trading_card.back_art_resource = back_local_resource
                existing_file = Path(f'{self.configuration.cache_file_path}{trading_card.unique_identifier_back}{PNG_EXTENSION}')
                back_local_resource.is_ready = existing_file.is_file()

    def async_store_local_resource(self, trading_card: TradingCard):
        if trading_card.local_resource.is_ready:
            return
        self._generate_directories_if_needed()
        # TODO: might need to prevent duplicate calls?
        # https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
        worker = StoreImageWorker(trading_card, self.image_fetcher_provider)
        worker.signals.finished.connect(partial(self._finish_storing_local_resource))
        self.pool.start(worker)

    def _generate_directories_if_needed(self):
        Path(self.configuration.cache_preview_file_path).mkdir(parents=True, exist_ok=True)

    def _finish_storing_local_resource(self, local_resource: LocalCardResource):
        if self.delegate is not None:
            self.delegate.rc_did_finish_storing_local_resource(self, local_resource)


# https://stackoverflow.com/questions/13909195/how-run-two-different-threads-simultaneously-in-pyqt
class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class StoreImageWorker(QRunnable):
    def __init__(self, 
                 trading_card: TradingCard,
                 image_fetcher_provider: ImageFetcherProvider):
        super(StoreImageWorker, self).__init__()
        self.trading_card = trading_card
        self.image_fetcher_provider = image_fetcher_provider
        self.signals = WorkerSignals()

    def run(self):
        # time.sleep(5)
        self.store_local_resource(self.trading_card)

    def store_local_resource(self, trading_card: TradingCard):
        img = self.image_fetcher_provider.provideImageFetcher().fetch(trading_card.image_url)
        img_height = min(img.height, img.width)
        rad = int(img_height * ROUNDED_CORDERS_MULTIPLIER_RELATIVE_TO_HEIGHT)
        # TODO: rounded rect needs to be propotional to size of image
        large_img = self._add_corners(img.convert('RGB'), rad)
        preview_img = self._downscale_image(large_img)
        large_img.save(trading_card.local_resource.image_path)
        preview_img.save(trading_card.local_resource.image_preview_path)
        trading_card.local_resource.is_ready = True
        self.signals.finished.emit(trading_card.local_resource)

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