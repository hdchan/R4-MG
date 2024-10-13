import random
from urllib import request, parse
import time
from PIL import Image, ImageDraw, ImageFont

from ...Image import ImageFetcherProtocol


class MockImageFetcher(ImageFetcherProtocol):
    def fetch(self, image_url: str) ->Image.Image:
        time.sleep(self.configuration.network_delay_duration)
        parsed_url = parse.urlparse(image_url)
        file_name = parsed_url.path.split('/')[-1]
        color_palette = [
            (255, 179, 186),
            (255, 223, 186),
            (255, 255, 186),
            (186, 255, 201),
            (186, 255, 255)
        ]
        selected_color = random.choice(color_palette)
        if '-b.png' in file_name:
            img = Image.new("RGB", (300, 200), selected_color)
        else:
            img = Image.new("RGB", (200, 300), selected_color)
        I1 = ImageDraw.Draw(img)
 
        # Add Text to an image
        myFont = ImageFont.truetype('arial.ttf', 20)
        I1.text((0, 100), file_name, font=myFont, fill=(0, 0, 0)) # type: ignore
        return img

class RemoteImageFetcher(ImageFetcherProtocol):
    def fetch(self, image_url: str) -> Image.Image:
        # TODO: retry if failed, and delete from cache
        time.sleep(self.configuration.network_delay_duration)
        try:
            img_data = request.urlopen(image_url)
            print(f'fetching real image: {image_url}')
            img = Image.open(img_data) # type: ignore
            return img
        except Exception as error:
            raise Exception(error)
        