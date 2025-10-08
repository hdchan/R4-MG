import platform
import random
import time
from PIL import Image, ImageDraw, ImageFont

from .ImageFetcherProtocol import *


class ImageFetcherLocal(ImageFetcherProtocol):
    def __init__(self):
        self.network_delay_duration = 0
        
    def fetch(self, local_resource: LocalCardResource) ->Image.Image:
        image_url = local_resource.remote_image_url
        if image_url is not None:
            time.sleep(self.network_delay_duration)
            file_name = local_resource.display_name
            color_palette = [
                (255, 179, 186),
                (255, 223, 186),
                (255, 255, 186),
                (186, 255, 201),
                (186, 255, 255)
            ]
            selected_color = random.choice(color_palette)
            if '(back)' in file_name:
                img = Image.new("RGB", (300, 200), selected_color)
            else:
                img = Image.new("RGB", (200, 300), selected_color)
            I1 = ImageDraw.Draw(img)
    
            # Add Text to an image
            if platform.system() == "Darwin":
                myFont = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
            elif platform.system() == "Windows":
                myFont = ImageFont.truetype('arial.ttf', 15)
            I1.text((0, 100), file_name, font=myFont, fill=(0, 0, 0)) # type: ignore
            return img
        else:
            raise Exception