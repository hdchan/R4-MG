
from typing import List, Optional, Callable, Tuple
from enum import Enum
from PIL import Image
from PIL.ImageFile import ImageFile
import sys
from ..Models import SWUTradingCardBackedLocalCardResource, ParsedDeckList, ParsedDeckListProviding


class DraftListImageGenerator:

    STACKED_CARD_REVEAL_PERCENTAGE = 0.15
    SIDEBOARD_LEFT_SPACING = 80
    MAIN_DECK_COLUMN_SPACING = 10
    MAIN_DECK_ROWS_SPACING = 40
    LEADER_BASE_SPACING = 10

    class Option(str, Enum):
        COST_CURVE_LEADER_BASE_HORIZONTAL = "Cost curve - top, horizontal leader/base"
        COST_CURVE_LEADER_BASE_VERTICAL = "Cost curve - left, vertical leader/base"
        # alphabet order option
        # hide sideboard option
        # spacing between general /row  COLS: 10, ROWS: 40
    
    def __init__(self, parsed_deck_provider: ParsedDeckListProviding):
        self._parsed_deck_list_provider = parsed_deck_provider
        self._is_sideboard_enabled = True
        self._is_alphabetical = False
        self._option = self.Option.COST_CURVE_LEADER_BASE_VERTICAL

    @property
    def is_sideboard_enabled(self) -> bool:
        return self._is_sideboard_enabled

    def set_is_sideboard_enabled(self, is_enabled: bool):
        self._is_sideboard_enabled = is_enabled

    @property
    def is_alphabetical(self) -> bool:
        return self._is_alphabetical
    
    def set_is_alphabetical(self, value: bool):
        self._is_alphabetical = value

    def set_option(self, option: 'DraftListImageGenerator.Option'):
        self._option = option

    @property
    def _parsed_deck_list(self) -> ParsedDeckList:
        return self._parsed_deck_list_provider.parsed_deck

    def generate_image(self) -> Optional[Image.Image]:
        if self._option == DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_HORIZONTAL:
            return self.generate_cost_curve_with_horizontal_leader_base()
        if self._option == DraftListImageGenerator.Option.COST_CURVE_LEADER_BASE_VERTICAL:
            return self.generate_cost_curve_with_vertical_leader_base()
        
    # MARK: - cost curve
    # sideboard images (optional)
    def _create_transparent_image(self, width: int, height: int) -> Image.Image:
        return Image.new('RGBA', (width, height), (255, 255, 255, 0))
    
    # Assumes cards are horizontal
    def _create_leader_base_stacked_horizontal_image(self, 
                                                     uniform_card_width: int, 
                                                     uniform_card_height: int) -> Image.Image:
        image_paths = list(map(lambda x: x.asset_path, self._parsed_deck_list.first_leader_and_first_base))
        if len(image_paths) == 0:
            return self._create_transparent_image(0, 0)
        leader_and_base_image_files = [Image.open(path) for path in image_paths]
            
        width = 0
        for img in leader_and_base_image_files:
            width += uniform_card_width + self.LEADER_BASE_SPACING
        combined_image_leader = self._create_transparent_image(width, uniform_card_height)
        offset = 0
        for img in leader_and_base_image_files:
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((uniform_card_width, uniform_card_width), Image.Resampling.BICUBIC)
            combined_image_leader.paste(scaled_image, (offset, 0), scaled_image)
            offset += scaled_image.width + self.LEADER_BASE_SPACING
        return combined_image_leader
    
    def _create_leader_base_stacked_vertical_image(self,
                                                     
                                                     uniform_card_width: int, 
                                                     uniform_card_height: int) -> Image.Image:
        image_paths = list(map(lambda x: x.asset_path, self._parsed_deck_list.first_leader_and_first_base))
        if len(image_paths) == 0:
            return self._create_transparent_image(0, 0)
        leader_and_base_image_files = [Image.open(path) for path in image_paths]
            
        height = 0
        for img in leader_and_base_image_files:
            height += uniform_card_height + self.LEADER_BASE_SPACING
        combined_image_leader = self._create_transparent_image(uniform_card_width, height)
        offset = 0
        for img in leader_and_base_image_files:
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((uniform_card_width, uniform_card_width), Image.Resampling.BICUBIC)
            combined_image_leader.paste(scaled_image, (0, offset), scaled_image)
            offset += scaled_image.height + self.LEADER_BASE_SPACING
        return combined_image_leader
    
    def create_cost_stack_col(self, images: List[ImageFile], uniform_card_width: int, uniform_card_height: int) -> Image.Image:
            if len(images) == 0:
                return self._create_transparent_image(uniform_card_width, uniform_card_height)
            height = 0
            for i, img in enumerate(images):
                if i == len(images) - 1:
                    # fully reveal top most card
                    height += uniform_card_height
                else:
                    # obscure bottom cards
                    height += int(uniform_card_height * self.STACKED_CARD_REVEAL_PERCENTAGE)
            combined_image = self._create_transparent_image(uniform_card_width, height)
            
            curr_y = 0
            for i, img in enumerate(images):
                scaled_image = img.copy().convert('RGBA')
                scaled_image.thumbnail((uniform_card_height, uniform_card_height), Image.Resampling.BICUBIC)
                combined_image.paste(scaled_image, (0, curr_y), scaled_image)
                curr_y += int(scaled_image.height * self.STACKED_CARD_REVEAL_PERCENTAGE)
            
            return combined_image

    def _create_sideboard_stacked_vertical_image(self, 
                                                 uniform_card_width: int,
                                                 uniform_card_height: int):
        sideboard = self._parsed_deck_list.sideboard
        image_paths = list(map(lambda x: x.asset_path, sideboard))
        image_files = [Image.open(path) for path in image_paths]
        return self.create_cost_stack_col(image_files, uniform_card_width, uniform_card_height)


    def _create_main_deck_cost_curve_image(self, 
                                           uniform_card_width: int,
                                           uniform_card_height: int):
        
        def create_card_type_row(get_cards_with_cost: Callable[[int], List[SWUTradingCardBackedLocalCardResource]], 
        get_main_deck_cards_with_cost: Callable[[int], List[SWUTradingCardBackedLocalCardResource]]) -> Image.Image:
            images: List[Image.Image] = []
            row_image_paths: List[str] = []
            for c in self._parsed_deck_list.cost_curve_values:
                main_deck_with_cost = get_main_deck_cards_with_cost(c)
                if len(main_deck_with_cost) == 0:
                    # closes gaps if there are not in the entire column
                    continue
                image_paths = list(map(lambda x: x.asset_path, get_cards_with_cost(c)))
                image_files = [Image.open(path) for path in image_paths]
                row_image_paths += image_paths
                col_image = self.create_cost_stack_col(image_files, uniform_card_width, uniform_card_height)
                images.append(col_image)
            
            if len(row_image_paths) == 0:
                # if entire row is empty, then we don't want to have a sized row
                return self._create_transparent_image(0, 0)
            
            height = 0
            width = 0
            for i in images:
                height = max(height, i.height)
                width += i.width + self.MAIN_DECK_COLUMN_SPACING
            combined_image = self._create_transparent_image(width, height)
            
            curr_x = 0
            for i, img in enumerate(images):
                combined_image.paste(img, (curr_x, 0), img)
                curr_x += img.width + self.MAIN_DECK_COLUMN_SPACING
            
            return combined_image
                
        
        def stack_rows(images: List[Image.Image]) -> Image.Image:
            height = 0
            width = 0
            for i in images:
                height += i.height + self.MAIN_DECK_ROWS_SPACING
                width = max(width, i.width)
            combined_image = self._create_transparent_image(width, height)
            
            curr_y = 0
            for i, img in enumerate(images):
                combined_image.paste(img, (0, curr_y), img)
                curr_y += img.height + self.MAIN_DECK_ROWS_SPACING
                
            return combined_image
        
        main_deck_image = stack_rows([
            create_card_type_row(lambda x: self._parsed_deck_list.all_units_with_cost(x, self._is_alphabetical), lambda x: self._parsed_deck_list.main_deck_with_cost(x)),
            create_card_type_row(lambda x: self._parsed_deck_list.all_upgrades_and_events_with_cost(x, self._is_alphabetical), lambda x: self._parsed_deck_list.main_deck_with_cost(x)),
        ])
        
        return main_deck_image
    
    def _uniform_card_dimensions(self) -> Tuple[int, int]:
        uniform_card_height = sys.maxsize
        uniform_card_width = sys.maxsize
        
        # Obtain uniform height and width since images can vary in dimensions
        # We want to use the smallest width/height
        for r in self._parsed_deck_list.all_cards:
            img = Image.open(r.asset_path)
            # assuming height is taller than width
            height = max(img.width, img.height)
            width = min(img.width, img.height)

            uniform_card_height = min(uniform_card_height, height)
            uniform_card_width = min(uniform_card_width, width)
        return uniform_card_width, uniform_card_height
    
    def generate_cost_curve_with_vertical_leader_base(self) -> Optional[Image.Image]:
        if self._parsed_deck_list.has_cards == False:
            return None
        
        uniform_card_width, uniform_card_height = self._uniform_card_dimensions()
        main_deck_image = self._create_main_deck_cost_curve_image(uniform_card_width, uniform_card_height)
        leader_base_image = self._create_leader_base_stacked_vertical_image(uniform_card_height, uniform_card_width)

        leader_base_main_deck_image = self._create_transparent_image(main_deck_image.width + leader_base_image.width + self.MAIN_DECK_COLUMN_SPACING, 
                                                      max(main_deck_image.height, leader_base_image.height))
        leader_base_main_deck_image.paste(leader_base_image, 
                           (0, int(leader_base_main_deck_image.height / 2 - leader_base_image.height/ 2)), 
                           leader_base_image)
        leader_base_main_deck_image.paste(main_deck_image, 
                           (leader_base_image.width + self.MAIN_DECK_COLUMN_SPACING, int(leader_base_main_deck_image.height / 2 - leader_base_main_deck_image.height/ 2)), 
                           main_deck_image)
        
        if not self._is_sideboard_enabled:
            sideboard_image = self._create_transparent_image(0, 0)
            sideboard_spacing = 0
        else:
            sideboard_image = self._create_sideboard_stacked_vertical_image(uniform_card_width, uniform_card_height)
            sideboard_spacing = self.SIDEBOARD_LEFT_SPACING
        result_image = self._create_transparent_image(leader_base_main_deck_image.width + sideboard_image.width + sideboard_spacing, 
                                                      max(leader_base_main_deck_image.height, sideboard_image.height))
        
        result_image.paste(leader_base_main_deck_image, 
                           (0, 0), 
                           leader_base_main_deck_image)
        result_image.paste(sideboard_image, 
                           (leader_base_main_deck_image.width + sideboard_spacing, 0), 
                           sideboard_image)

        return result_image
    
    def generate_cost_curve_with_horizontal_leader_base(self) -> Optional[Image.Image]:
        if self._parsed_deck_list.has_cards == False:
            return None
        
        uniform_card_width, uniform_card_height = self._uniform_card_dimensions()
        main_deck_image = self._create_main_deck_cost_curve_image(uniform_card_width, uniform_card_height)
        
        if not self._is_sideboard_enabled:
            sideboard_image = self._create_transparent_image(0, 0)
            sideboard_spacing = 0
        else:
            sideboard_image = self._create_sideboard_stacked_vertical_image(uniform_card_width, uniform_card_height)
            sideboard_spacing = self.SIDEBOARD_LEFT_SPACING

        main_deck_sideboard_image = self._create_transparent_image(main_deck_image.width + sideboard_image.width + sideboard_spacing, 
                                                      max(main_deck_image.height, sideboard_image.height))
        
        main_deck_sideboard_image.paste(main_deck_image, 
                           (0, 0), 
                           main_deck_image)
        main_deck_sideboard_image.paste(sideboard_image, 
                           (main_deck_image.width + sideboard_spacing, 0), 
                           sideboard_image)
        


        # Leader base should probably be centered on main deck instead of all cards
        leader_base_image = self._create_leader_base_stacked_horizontal_image(uniform_card_height,
                                                                              uniform_card_width)

        result_image = self._create_transparent_image(max(main_deck_sideboard_image.width, leader_base_image.width), 
                                                      main_deck_sideboard_image.height + leader_base_image.height + self.MAIN_DECK_ROWS_SPACING)
        result_image.paste(leader_base_image, 
                           (int(result_image.width / 2 - leader_base_image.width/ 2), 0), 
                           leader_base_image)
        result_image.paste(main_deck_sideboard_image, 
                           (int(result_image.width / 2 - main_deck_sideboard_image.width/ 2), leader_base_image.height + self.MAIN_DECK_ROWS_SPACING), 
                           main_deck_sideboard_image)

        return result_image