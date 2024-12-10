import random
import time
from urllib import parse

from PIL import Image, ImageDraw, ImageFont

from .ImageFetcherProtocol import *
import platform

class MockImageFetcher(ImageFetcherProtocol):
    def fetch(self, image_url: str) ->Image.Image:
        time.sleep(self.configuration_manager.configuration.network_delay_duration)
        parsed_url = parse.urlparse(image_url)
        split_path = parsed_url.path.split('/')
        file_name = split_path[-2] + split_path[-1]
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
        if platform.system() == "Darwin":
            myFont = ImageFont.truetype('/Library/Fonts/Arial.ttf', 20)
        elif platform.system() == "Windows":
            myFont = ImageFont.truetype('arial.ttf', 20)
        I1.text((0, 100), file_name, font=myFont, fill=(0, 0, 0)) # type: ignore
        return img