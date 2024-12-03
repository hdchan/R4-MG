import time
from urllib import request

from PIL import Image

from .ImageFetcherProtocol import *
from .ImageFetcherRequestProtocol import *
import io

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
                print(f'fetching real image: {image_url}')
                time.sleep(self.configuration_provider.configuration.network_delay_duration)
                # https://stackoverflow.com/questions/41106599/python-3-5-urllib-request-urlopen-progress-bar-available
                # with request.urlopen(image_url) as response:
                #     total_size = int(response.headers.get('Content-Length', 0))
                #     downloaded = 0
                #     buf = io.BytesIO()
                #     while True:
                #         chunk = response.read()
                #         downloaded += len(chunk)
                #         print(f"{downloaded / total_size * 100}%")
                #         if not chunk:
                #             break
                #         buf.write(chunk)
                buf = request.urlopen(image_url)
                img = Image.open(buf) # type: ignore
                return img
            except Exception as error:
                if retry_count == max_retry:
                    raise Exception(error)
            retry_count += 1
            # delay before retry
            time.sleep(3)
        