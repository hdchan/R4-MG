
from typing import List, Optional, Callable

from PIL import Image
from PIL.ImageFile import ImageFile
import sys
from ..Models import SWUTradingCardBackedLocalCardResource, ParsedDraftList

class DraftListImageGenerator:
    def generate_basic(self,
                       parsed_draft_list: ParsedDraftList,
                       main_deck_cols: int) -> Image.Image:
        selected_leader = parsed_draft_list.first_leader
        selected_base = parsed_draft_list.first_base
        main_deck = parsed_draft_list.main_deck
        
        image_paths = list(map(lambda x: x.asset_path, main_deck))
        
        leader_and_base_image = self.combine_leader_and_base(selected_leader, selected_base)
        main_deck_image = self.combine_images_grid(image_paths, min(main_deck_cols, len(main_deck)))
        
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
            
        return combined_image
    
    def combine_leader_and_base(self, 
                                leader_resource: Optional[SWUTradingCardBackedLocalCardResource], 
                                base_resource: Optional[SWUTradingCardBackedLocalCardResource]) -> Optional[Image.Image]:
        resources: List[str] = []
        if leader_resource is not None:
            resources.append(leader_resource.asset_path)
        if base_resource is not None:
            resources.append(base_resource.asset_path)
        if len(resources) == 0:
            return None
        
        return self.combine_images_grid(resources, 1)
    
    def combine_images_grid(self,
                            image_paths: List[str], 
                            columns: int, 
                            spacing: int = 0) -> Optional[Image.Image]:
        if not image_paths:
            return None
        
        # Open all images and get their dimensions
        images = [Image.open(path) for path in image_paths]
        return self.combine_images_grid_with_images(images, columns, spacing)
    
    def combine_images_grid_with_image_image(self,
                                             images: List[Image.Image],
                                             columns: int,
                                             spacing: int = 0) -> Optional[Image.Image]:
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
    
    def combine_images_grid_with_images(self,
                                        images: List[ImageFile], 
                                        columns: int, 
                                        spacing: int = 0) -> Optional[Image.Image]:
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
    
    
    # MARK: - cost curve
    # TODO
    # Add leader and base
    # remove blank spaces below
    # combine upgrades and events
    # sideboard images (optional)
    def generate_cost_curve(self, parsed_draft_list: ParsedDraftList) -> Optional[Image.Image]:
        if parsed_draft_list.has_cards == False:
            return None
        
        uniform_card_height = sys.maxsize
        uniform_card_width = sys.maxsize
        
        # for _, r in enumerate(parsed_draft_list.main_deck):
        #     img = Image.open(r.asset_path)
        #     uniform_card_height = min(uniform_card_height, img.height)
        #     uniform_card_width = min(uniform_card_width, img.width)
        
        for _, r in enumerate(parsed_draft_list.all_cards):
            img = Image.open(r.asset_path)
            height = max(img.width, img.height)
            width = min(img.width, img.height)

            uniform_card_height = min(uniform_card_height, height)
            uniform_card_width = min(uniform_card_width, width)

        
        HEIGHT_FACTOR = 0.15
        
        def create_col(images: List[ImageFile]) -> Image.Image:
            if len(images) == 0:
                return Image.new('RGBA', (uniform_card_width, uniform_card_height), (255, 255, 255, 0))
            height = 0
            for i, img in enumerate(images):
                if i == len(images) - 1:
                    height += uniform_card_height
                else:
                    height += int(uniform_card_height * HEIGHT_FACTOR)
            combined_image = Image.new('RGBA', (uniform_card_width, height), (255, 255, 255, 0)) # White background
            
            curr_y = 0
            for i, img in enumerate(images):
                scaled_image = img.copy().convert('RGBA')
                scaled_image.thumbnail((uniform_card_height, uniform_card_height), Image.Resampling.BICUBIC)
                combined_image.paste(scaled_image, (0, curr_y), scaled_image)
                curr_y += int(scaled_image.height * HEIGHT_FACTOR)
            
            return combined_image
        
        cost_curve_values = parsed_draft_list.cost_curve_values
        
        def create_row(get_cards: Callable[[int], List[SWUTradingCardBackedLocalCardResource]]) -> Image.Image:
            images: List[Image.Image] = []
            for c in cost_curve_values:
                image_paths = list(map(lambda x: x.asset_path, get_cards(c)))
                image_files = [Image.open(path) for path in image_paths]
                col_image = create_col(image_files)
                images.append(col_image)
            
            if len(images) == 0:
                return Image.new('RGBA', (0, 0), (255, 255, 255, 0))
            
            height = 0
            width = 0
            for i in images:
                height = max(height, i.height)
                width += i.width
            combined_image = Image.new('RGBA', (width, height), (255, 255, 255, 0)) # White background
            
            curr_x = 0
            for i, img in enumerate(images):
                combined_image.paste(img, (curr_x, 0), img)
                curr_x += img.width
            
            return combined_image
                
        
        def append_rows(images: List[Image.Image]) -> Image.Image:
            height = 0
            width = 0
            for i in images:
                height += i.height
                width = max(width, i.width)
            combined_image = Image.new('RGBA', (width, height), (255, 255, 255, 0)) # White background
            
            curr_y = 0
            for i, img in enumerate(images):
                combined_image.paste(img, (0, curr_y), img)
                curr_y += img.height
                
            return combined_image
        

        main_deck = append_rows([
            # Do we need to sort columns?
            create_row(lambda x: parsed_draft_list.all_units_with_cost(x)),
            create_row(lambda x: parsed_draft_list.all_upgrades_and_events_with_cost(x)),
        ])

        
        image_paths = list(map(lambda x: x.asset_path, parsed_draft_list.first_leader_and_first_base))
        image_files = [Image.open(path) for path in image_paths]
            
        width = 0
        for i, img in enumerate(image_files):
            width += uniform_card_height
        combined_image_leader = Image.new('RGBA', (width, uniform_card_width), (0, 0, 0, 0)) # White background
        offset = 0
        for i, img in enumerate(image_files):
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((uniform_card_height, uniform_card_height), Image.Resampling.BICUBIC)
            combined_image_leader.paste(scaled_image, (offset, 0), scaled_image)
            offset += scaled_image.width


        combined_image = Image.new('RGBA', (max(main_deck.width, combined_image_leader.width), main_deck.height + combined_image_leader.height), (255, 255, 255, 0)) # White background

        

        combined_image.paste(combined_image_leader, (int(combined_image.width / 2 - combined_image_leader.width/ 2), 0), combined_image_leader)
        combined_image.paste(main_deck, (int(combined_image.width / 2 - main_deck.width/ 2), combined_image_leader.height), main_deck)

        return combined_image

        # return create_row(lambda x: parsed_draft_list.main_deck_with_cost(x))