import time
from urllib import request

from PIL import Image

from .ImageFetcherProtocol import *
from .ImageFetcherRequestProtocol import *


class RemoteImageFetcher(ImageFetcherProtocol):
    def fetch(self, image_url: str) ->Image.Image:
        try:
            return self._retryable_fetch(image_url)
        except Exception as error:
            raise Exception(error)
        
    def _retryable_fetch(self, image_url: str) -> Image.Image:
        max_retry = 3
        retry_count = 1
        while True:
            try:
                # raise Exception(retry_count)
                time.sleep(self.configuration_provider.configuration.network_delay_duration)
                img_data = request.urlopen(image_url)
                print(f'fetching real image: {image_url}')
                img = Image.open(img_data) # type: ignore
                return img
            except Exception as error:
                if retry_count == max_retry:
                    raise Exception(error)
            retry_count += 1
            # delay before retry
            time.sleep(3)
        