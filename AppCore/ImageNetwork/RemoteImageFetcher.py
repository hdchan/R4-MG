import time
from urllib import request

from PIL import Image

from ..Config import ConfigurationManager
from .ImageFetcherProtocol import *
from .ImageFetcherRequestProtocol import *


class RemoteImageFetcher(ImageFetcherProtocol):
    def __init__(self, configuration_manager: ConfigurationManager):
        self.configuration_manager = configuration_manager
        
    def fetch(self, local_resource: LocalCardResource) ->Image.Image:
        try:
            image_url = local_resource.remote_image_url
            if image_url is not None:
                return self._retryable_fetch(image_url)
            else:
                raise Exception("No remote image url")
            
        except Exception as error:
            raise Exception(error)
        
    def _retryable_fetch(self, image_url: str) -> Image.Image:
        max_retry = 3
        retry_count = 1
        while True:
            try:
                # raise Exception(retry_count)
                print(f'fetching real image: {image_url}')
                time.sleep(self.configuration_manager.configuration.network_delay_duration)
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
        