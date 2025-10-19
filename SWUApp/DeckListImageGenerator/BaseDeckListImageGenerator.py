import sys
from enum import Enum
from typing import List, Tuple

from PIL import Image
from PIL.ImageFile import ImageFile


class BaseDeckListImageGenerator:
    def create_canvas_image(self,
                            width: int,
                            height: int,
                            location: str = "") -> Image.Image:
        color_value = (0, 0, 0, 0)
        return Image.new('RGBA', (width, height), color_value)

    def uniform_card_dimensions(self, image_paths: List[ImageFile]) -> Tuple[int, int]:
        uniform_card_height = sys.maxsize
        uniform_card_width = sys.maxsize
        
        # Obtain uniform height and width since images can vary in dimensions
        # We want to use the smallest width/height
        for img in image_paths:
            # assuming height is taller than width
            height = max(img.width, img.height)
            width = min(img.width, img.height)

            uniform_card_height = min(uniform_card_height, height)
            uniform_card_width = min(uniform_card_width, width)
        return uniform_card_width, uniform_card_height

    class VAlignment(int, Enum):
        TOP = 0
        CENTER = 1
        BOTTOM = 2

    class HAlignment(int, Enum):
        LEFT = 3
        CENTER = 4
        RIGHT = 5

    # def generate_random_rgb():
    #     r = random.randint(0, 255)
    #     g = random.randint(0, 255)
    #     b = random.randint(0, 255)
    #     return (r, g, b)

    def stitch_image_columns(self, 
                             images: List[Image.Image],
                             v_alignment: VAlignment = VAlignment.TOP,
                             column_spacing: int = 0, 
                             location: str = "stitch-columns") -> Image.Image:
        width = 0
        height = 0
        for i, img in enumerate(images):
            height = max(height, img.height)
            width += img.width
            if i < len(images) - 1:
                width += column_spacing
        combined_image = self.create_canvas_image(width, height, location)
        curr_x = 0
        for i, img in enumerate(images):
            if v_alignment == self.VAlignment.CENTER:
                y = int(combined_image.height / 2 - img.height / 2)
                combined_image.paste(img, (curr_x, y), img)
            elif v_alignment == self.VAlignment.BOTTOM:
                y = combined_image.height - img.height
                combined_image.paste(img, (curr_x, y), img)
            else:
                combined_image.paste(img, (curr_x, 0), img)
            curr_x += img.width
            if i < len(images) - 1:
                curr_x += column_spacing
        return combined_image

    def stitch_image_rows(self, 
                          images: List[Image.Image],
                          h_alignment: HAlignment = HAlignment.LEFT,
                          row_spacing: int = 0, 
                          location: str = "stitch-rows") -> Image.Image:
        width = 0
        height = 0
        for i, img in enumerate(images):
            width = max(width, img.width)
            height += img.height
            if i < len(images) - 1:
                height += row_spacing
        
        combined_image = self.create_canvas_image(width, height, location)
        curr_y = 0
        for i, img in enumerate(images):
            if h_alignment == self.HAlignment.CENTER:
                x = int(combined_image.width / 2 - img.width / 2)
                combined_image.paste(img, (x, curr_y), img)
            elif h_alignment == self.HAlignment.RIGHT:
                x = combined_image.width - img.width
                combined_image.paste(img, (x, curr_y), img)
            else:
                combined_image.paste(img, (0, curr_y), img)
            curr_y += img.height
            if i < len(images) - 1:
                curr_y += row_spacing
        return combined_image

    def stitch_image_grid_right_to_down(self, 
                                        images: List[Image.Image],
                                        grid_width: int,
                                        v_alignment: VAlignment = VAlignment.TOP, 
                                        column_spacing: int = 0, 
                                        h_alignment: HAlignment = HAlignment.LEFT,
                                        row_spacing: int = 0, location: str = "stitch-grid"):
        sanitized_grid_width = max(grid_width, 1)
        rows: List[Image.Image] = []
        current_row: List[Image.Image] = []
        for i, img in enumerate(images):
            current_row.append(img)
            if (i + 1) % sanitized_grid_width == 0:
                row = self.stitch_image_columns(current_row, v_alignment, column_spacing, location)
                rows.append(row)
                current_row = []
            
        if len(current_row) > 0:
            row = self.stitch_image_columns(current_row, v_alignment, column_spacing, location)
            rows.append(row)
        return self.stitch_image_rows(rows, h_alignment, row_spacing, location)