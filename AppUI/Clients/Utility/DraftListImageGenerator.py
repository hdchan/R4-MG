
from typing import List, Optional

from PIL import Image
from PIL.ImageFile import ImageFile

from ..Models import SWUTradingCardBackedLocalCardResource


class DraftListImageGenerator:
    
    @staticmethod
    def generate(selected_leader: Optional[SWUTradingCardBackedLocalCardResource],
                 selected_base: Optional[SWUTradingCardBackedLocalCardResource],
                 main_deck: List[SWUTradingCardBackedLocalCardResource],
                 side_board: List[SWUTradingCardBackedLocalCardResource], 
                 main_deck_cols: int) -> Image.Image:
        image_paths = list(map(lambda x: x.asset_path, main_deck))
        
        leader_and_base_image = DraftListImageGenerator.combine_leader_and_base(selected_leader, selected_base)
        main_deck_image = DraftListImageGenerator.combine_images_grid(image_paths, min(main_deck_cols, len(main_deck)))
        
        combined_width = 0
        max_height = 0
        if leader_and_base_image is not None:
            combined_width += leader_and_base_image.width
            max_height = max(max_height, leader_and_base_image.height)
        if main_deck_image is not None:
            combined_width += main_deck_image.width
            max_height = max(max_height, main_deck_image.height)

        combined_image = Image.new('RGBA', (combined_width, max_height), (255, 255, 255, 0))
        
        if leader_and_base_image is not None:
            combined_image.paste(leader_and_base_image, (0, 0))
            if main_deck_image is not None:
                combined_image.paste(main_deck_image, (leader_and_base_image.width, 0))
        elif main_deck_image is not None:
            combined_image.paste(main_deck_image, (0, 0))
            
        # combined_image.save(file_path)
        return combined_image
    
    @staticmethod
    def combine_leader_and_base(leader_resource: Optional[SWUTradingCardBackedLocalCardResource], 
                                base_resource: Optional[SWUTradingCardBackedLocalCardResource]) -> Optional[Image.Image]:
        resources: List[str] = []
        if leader_resource is not None:
            resources.append(leader_resource.asset_path)
        if base_resource is not None:
            resources.append(base_resource.asset_path)
        if len(resources) == 0:
            return None
        
        return DraftListImageGenerator.combine_images_grid(resources, 1)
    
    @staticmethod
    def combine_images_grid(image_paths: List[str], columns: int, spacing: int = 0) -> Optional[Image.Image]:
        if not image_paths:
            return None
        
        # Open all images and get their dimensions
        images = [Image.open(path) for path in image_paths]
        return DraftListImageGenerator.combine_images_grid_with_images(images, columns, spacing)
    
    @staticmethod
    def combine_images_grid_with_images(images: List[ImageFile], columns: int, spacing: int = 0) -> Optional[Image.Image]:
        if not images:
            return None
        
        # Calculate max width and height for individual images (for consistent sizing)
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)

        # Calculate the number of rows needed
        rows = (len(images) + columns - 1) // columns

        # Calculate the dimensions of the final combined image
        background_width = max_width * columns + spacing * (columns - 1)
        background_height = max_height * rows + spacing * (rows - 1)

        # Create a new blank image for the background
        combined_image = Image.new('RGBA', (background_width, background_height), (255, 255, 255, 0)) # White background

        x_offset = 0
        y_offset = 0

        for i, img in enumerate(images):
            # Calculate position for the current image
            col_index = i % columns
            row_index = i // columns

            x_offset = col_index * (max_width + spacing)
            y_offset = row_index * (max_height + spacing)

            # Paste the image onto the background, centering if needed
            # (adjust x_offset and y_offset to center if images are smaller than max_width/height)
            paste_x = x_offset + (max_width - img.width) // 2
            paste_y = y_offset + (max_height - img.height) // 2
            
            combined_image.paste(img, (paste_x, paste_y))

        return combined_image