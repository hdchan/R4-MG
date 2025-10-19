
import sys
from io import BytesIO
from typing import Callable, Hashable, List, Optional, Set, Tuple

from PIL import Image
from PIL.ImageFile import ImageFile
from PyQt5.QtCore import QMutex, QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from AppCore.Config import Configuration
from AppCore.Models import LocalCardResource

from ..Events.DeckListImageGeneratedEvent import DeckListImageGeneratedEvent
from ..Models import (DeckListImageGeneratorStyles, ParsedDeckList,
                      SWUTradingCardBackedLocalCardResource)
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .DeckListImageGeneratorProtocol import DeckListImageGeneratorProtocol
from .ScaledDeckListImageGeneratorStyles import \
    ScaledDeckListImageGeneratorStyles


class LegacyDeckListImageGenerator(DeckListImageGeneratorProtocol):
    
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._configuration_manager = swu_app_dependencies_provider.configuration_manager
        self._image_resource_processor_provider = swu_app_dependencies_provider.image_resource_processor_provider
        self._observation_tower = swu_app_dependencies_provider.observation_tower
        self._is_full_image = False
        self.pool = QThreadPool()
        self.mutex = QMutex()
        self.working_resources: Set[Hashable] = set()
        self._is_downloading_images = False

    @property
    def _core_configuration(self) -> Configuration:
        return self._configuration_manager.configuration.core_configuration

    @property
    def is_loading(self) -> bool:
        return len(self.working_resources) > 0 or self._is_downloading_images

    def _deck_list_image_generator_styles(self, scale_factor: float = 1) -> DeckListImageGeneratorStyles:
        return ScaledDeckListImageGeneratorStyles.from_non_scaled_styles(self._configuration_manager.configuration.deck_list_image_generator_styles, scale_factor)

    def _asset_path_for_resource(self, resource: LocalCardResource) -> str:
        if self._is_full_image or self._deck_list_image_generator_styles().is_full_image_preview:
            return resource.image_path
        return resource.image_preview_path

    def generate_image(self,
                       parsed_deck_list: ParsedDeckList,
                       is_export: bool, 
                       completion: Callable[[Optional[QPixmap], Optional[Image.Image]], None]):
        is_full_image = is_export
        def _completed():
            self._is_downloading_images = False
            self._generate_image(parsed_deck_list,
                                 is_full_image, 
                                 completion)
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resources_multi(parsed_deck_list.all_cards, _completed)
        self._is_downloading_images = True

    def _generate_image(self, 
                        parsed_deck_list: ParsedDeckList,
                        is_full_image: bool, 
                        completion: Callable[[Optional[QPixmap], Optional[Image.Image]], None]):
        print("Generating deck list image")
        self._is_full_image = is_full_image
        start_event = DeckListImageGeneratedEvent(DeckListImageGeneratedEvent.EventType.STARTED, 
                                                  parsed_deck_list)
        self._observation_tower.notify(start_event)

        def _finished(result: Tuple[Optional[QPixmap], Optional[Image.Image], ParsedDeckList]):
            pixmap, image, parsed_deck = result
            self.mutex.lock()
            self.working_resources.remove(parsed_deck)
            self.mutex.unlock()

            end_event = DeckListImageGeneratedEvent(DeckListImageGeneratedEvent.EventType.STARTED, 
                                                  parsed_deck_list)
            end_event.predecessor = start_event
            self._observation_tower.notify(end_event) 
            print(f"Image generation took: {end_event.seconds_since_predecessor}")
            completion(pixmap, image)

        def _generate_image() -> Tuple[Optional[QPixmap], Optional[Image.Image]]:
            image: Optional[Image.Image]
            if self._deck_list_image_generator_styles().is_leader_base_on_top:
                image = self.generate_cost_curve_with_horizontal_leader_base(parsed_deck_list)
            else:
                image = self.generate_cost_curve_with_vertical_leader_base(parsed_deck_list)

            pixmap: Optional[QPixmap] = None
            if image is not None:
                byte_array = BytesIO()
                image.save(byte_array, format="PNG")
                byte_array.seek(0)
                
                qimage = QImage.fromData(byte_array.getvalue())
                pixmap = QPixmap.fromImage(qimage)


            return pixmap, image
            
        self.mutex.lock()
        
        self.working_resources.add(parsed_deck_list)
        self.mutex.unlock()
        worker = Worker(_generate_image, parsed_deck_list)
        worker.signals.finished.connect(_finished)
        self.pool.start(worker)
        
    # MARK: - cost curve
    def _create_transparent_image(self, width: int, height: int, location: str = "") -> Image.Image:
        color = (0, 0, 0, 0)
        if self._core_configuration.is_developer_mode and self._deck_list_image_generator_styles().is_visual_debug:
            if location == 'leader-base':
                color = (255, 0, 0)
            if location == 'main-deck-col':
                color = (255, 0, 0)
            if location == 'main-deck-row':
                color = (0, 0, 255)
            if location == 'entire-deck':
                color = (128, 128, 128)
        return Image.new('RGBA', (width, height), color)
    
    # Assumes cards are horizontal
    def _create_leader_base_stacked_horizontal_image(self,
                                                     parsed_deck_list: ParsedDeckList,
                                                     uniform_card_width: int, 
                                                     uniform_card_height: int,
                                                     scale_factor: float) -> Image.Image:
        image_paths = list(map(self._asset_path_for_resource, parsed_deck_list.first_leader_and_first_base))
        if len(image_paths) == 0:
            return self._create_transparent_image(0, 0)
        leader_and_base_image_files = [Image.open(path) for path in image_paths]
            
        width = 0
        for (i, img) in enumerate(leader_and_base_image_files):
            width += uniform_card_width
            if i < len(leader_and_base_image_files) - 1:
                width += self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_between
        combined_image_leader = self._create_transparent_image(width, uniform_card_height, 'leader-base')
        offset = 0
        for (i, img) in enumerate(leader_and_base_image_files):
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((uniform_card_width, uniform_card_width), Image.Resampling.BICUBIC)
            combined_image_leader.paste(scaled_image, (offset, 0), scaled_image)
            offset += scaled_image.width
            if i < len(leader_and_base_image_files) - 1:
                offset += self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_between
        return combined_image_leader
    
    def _create_leader_base_stacked_vertical_image(self,
                                                   parsed_deck_list: ParsedDeckList,
                                                   uniform_card_width: int, 
                                                   uniform_card_height: int,
                                                   scale_factor: float) -> Image.Image:
        image_paths = list(map(self._asset_path_for_resource, parsed_deck_list.first_leader_and_first_base))
        if len(image_paths) == 0:
            return self._create_transparent_image(0, 0)
        leader_and_base_image_files = [Image.open(path) for path in image_paths]
            
        height = 0
        for (i, img) in enumerate(leader_and_base_image_files):
            height += uniform_card_height
            if i < len(leader_and_base_image_files) - 1:
                height += self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_between
        combined_image_leader = self._create_transparent_image(uniform_card_width, height, 'leader-base')
        offset = 0
        for (i, img) in enumerate(leader_and_base_image_files):
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((uniform_card_width, uniform_card_width), Image.Resampling.BICUBIC)
            combined_image_leader.paste(scaled_image, (0, offset), scaled_image)
            offset += scaled_image.height
            if i < len(leader_and_base_image_files) - 1:
                offset += self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_between
        return combined_image_leader
    
    def create_stack_col(self, 
                         images: List[ImageFile], 
                         uniform_card_width: int, 
                         uniform_card_height: int, 
                         scale_factor: float) -> Image.Image:
            if len(images) == 0:
                return self._create_transparent_image(uniform_card_width, uniform_card_height)
            height = 0
            for i, img in enumerate(images):
                if i == len(images) - 1:
                    # fully reveal top most card
                    height += uniform_card_height
                else:
                    # obscure bottom cards
                    height += int(uniform_card_height * self._deck_list_image_generator_styles(scale_factor).stacked_card_reveal_percentage)
            combined_image = self._create_transparent_image(uniform_card_width, height, 'main-deck-col')
            
            curr_y = 0
            for i, img in enumerate(images):
                scaled_image = img.copy().convert('RGBA')
                scaled_image.thumbnail((uniform_card_height, uniform_card_height), Image.Resampling.BICUBIC)
                combined_image.paste(scaled_image, (0, curr_y), scaled_image)
                curr_y += int(scaled_image.height * self._deck_list_image_generator_styles(scale_factor).stacked_card_reveal_percentage)
            
            return combined_image

    def _create_sideboard_stacked_vertical_image(self, 
                                                 parsed_deck_list: ParsedDeckList,
                                                 uniform_card_width: int,
                                                 uniform_card_height: int,
                                                 scale_factor: float):
        sideboard = parsed_deck_list.sideboard
        image_paths = list(map(self._asset_path_for_resource, sideboard))
        image_files = [Image.open(path) for path in image_paths]
        return self.create_stack_col(image_files, uniform_card_width, uniform_card_height, scale_factor)


    def _create_main_deck_cost_curve_image(self, 
                                           parsed_deck_list: ParsedDeckList,
                                           uniform_card_width: int,
                                           uniform_card_height: int, 
                                           scale_factor: float):
        
        def create_card_type_row(get_cards_with_cost: Callable[[int], List[SWUTradingCardBackedLocalCardResource]], 
        get_main_deck_cards_with_cost: Callable[[int], List[SWUTradingCardBackedLocalCardResource]]) -> Image.Image:
            col_images: List[Image.Image] = []
            row_image_paths: List[str] = []
            for c in parsed_deck_list.main_deck_cost_curve_values:
                main_deck_with_cost = get_main_deck_cards_with_cost(c)
                if len(main_deck_with_cost) == 0:
                    # closes gaps if there are not in the entire column
                    continue
                image_paths = list(map(self._asset_path_for_resource, get_cards_with_cost(c)))
                image_files = [Image.open(path) for path in image_paths]
                row_image_paths += image_paths
                col_image = self.create_stack_col(image_files, uniform_card_width, uniform_card_height, scale_factor)
                col_images.append(col_image)
            
            if len(row_image_paths) == 0:
                # if entire row is empty, then we don't want to have a sized row
                return self._create_transparent_image(0, 0)
            
            height = 0
            width = 0
            for i, img in enumerate(col_images):
                height = max(height, img.height)
                width += img.width
                if i < len(col_images) - 1:
                    # don't add padding after last col
                    width += self._deck_list_image_generator_styles(scale_factor).main_deck_column_spacing
            combined_image = self._create_transparent_image(width, height, 'main-deck-row')
            
            curr_x = 0
            for i, img in enumerate(col_images):
                combined_image.paste(img, (curr_x, 0), img)
                curr_x += img.width
                if i < len(col_images) - 1:
                    # don't add padding after last col
                    curr_x += self._deck_list_image_generator_styles(scale_factor).main_deck_column_spacing
            return combined_image
                
        
        def stack_rows(images: List[Image.Image]) -> Image.Image:
            height = 0
            width = 0
            for i, img in enumerate(images):
                height += img.height
                if i < len(images) - 1:
                    height += self._deck_list_image_generator_styles(scale_factor).main_deck_row_spacing
                width = max(width, img.width)
            combined_image = self._create_transparent_image(width, height)
            
            curr_y = 0
            for i, img in enumerate(images):
                combined_image.paste(img, (0, curr_y), img)
                curr_y += img.height
                if i < len(images) - 1:
                    curr_y += self._deck_list_image_generator_styles(scale_factor).main_deck_row_spacing
            return combined_image
        
        main_deck_image = stack_rows([
            create_card_type_row(lambda x: parsed_deck_list.all_units_with_cost(x, self._deck_list_image_generator_styles(scale_factor).is_sorted_alphabetically), lambda x: parsed_deck_list.main_deck_with_cost(x)),
            create_card_type_row(lambda x: parsed_deck_list.all_main_deck_upgrades_and_events_with_cost(x, self._deck_list_image_generator_styles(scale_factor).is_sorted_alphabetically), lambda x: parsed_deck_list.main_deck_with_cost(x)),
        ])
        
        return main_deck_image
    
    
    def _uniform_card_dimensions_non_scaled(self, parsed_deck_list: ParsedDeckList) -> Tuple[int, int]:
        uniform_card_height = sys.maxsize
        uniform_card_width = sys.maxsize
        
        # Obtain uniform height and width since images can vary in dimensions
        # We want to use the smallest width/height
        for r in parsed_deck_list.all_cards:
            img = Image.open(r.asset_path)
            # assuming height is taller than width
            height = max(img.width, img.height)
            width = min(img.width, img.height)

            uniform_card_height = min(uniform_card_height, height)
            uniform_card_width = min(uniform_card_width, width)
        return uniform_card_width, uniform_card_height

    def _uniform_card_dimensions(self, parsed_deck_list: ParsedDeckList) -> Tuple[int, int]:
        uniform_card_height = sys.maxsize
        uniform_card_width = sys.maxsize
        
        # Obtain uniform height and width since images can vary in dimensions
        # We want to use the smallest width/height
        for r in parsed_deck_list.all_cards:
            img = Image.open(self._asset_path_for_resource(r))
            # assuming height is taller than width
            height = max(img.width, img.height)
            width = min(img.width, img.height)

            uniform_card_height = min(uniform_card_height, height)
            uniform_card_width = min(uniform_card_width, width)
        return uniform_card_width, uniform_card_height
    
    def generate_cost_curve_with_vertical_leader_base(self, parsed_deck_list: ParsedDeckList) -> Optional[Image.Image]:
        if parsed_deck_list.has_cards == False:
            return None
        
        uniform_card_width, uniform_card_height = self._uniform_card_dimensions(parsed_deck_list)
        uniform_card_width_none_scaled, _ = self._uniform_card_dimensions_non_scaled(parsed_deck_list)
        scale_factor = uniform_card_width / uniform_card_width_none_scaled
        main_deck_image = self._create_main_deck_cost_curve_image(parsed_deck_list, uniform_card_width, uniform_card_height, scale_factor)
        leader_base_image = self._create_leader_base_stacked_vertical_image(parsed_deck_list, uniform_card_height, uniform_card_width, scale_factor)

        leader_base_main_deck_image = self._create_transparent_image(main_deck_image.width + leader_base_image.width + self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_left_relative_to_main_deck, 
                                                      max(main_deck_image.height, leader_base_image.height))
        leader_base_main_deck_image.paste(leader_base_image, 
                           (0, int(leader_base_main_deck_image.height / 2 - leader_base_image.height/ 2)), 
                           leader_base_image)
        leader_base_main_deck_image.paste(main_deck_image, 
                           (leader_base_image.width + self._deck_list_image_generator_styles(scale_factor).leader_base_spacing_left_relative_to_main_deck, int(leader_base_main_deck_image.height / 2 - leader_base_main_deck_image.height/ 2)), 
                           main_deck_image)
        
        has_sideboard = len(parsed_deck_list.sideboard) > 0

        if not self._deck_list_image_generator_styles(scale_factor).is_sideboard_enabled or not has_sideboard:
            sideboard_image = self._create_transparent_image(0, 0)
            sideboard_spacing = 0
        else:
            sideboard_image = self._create_sideboard_stacked_vertical_image(parsed_deck_list, uniform_card_width, uniform_card_height, scale_factor)
            sideboard_spacing = self._deck_list_image_generator_styles(scale_factor).sideboard_left_spacing_relative_to_main_deck
        result_image = self._create_transparent_image(leader_base_main_deck_image.width + sideboard_image.width + sideboard_spacing, 
                                                      max(leader_base_main_deck_image.height, sideboard_image.height), 'entire-deck')
        
        result_image.paste(leader_base_main_deck_image, 
                           (0, 0), 
                           leader_base_main_deck_image)
        result_image.paste(sideboard_image, 
                           (leader_base_main_deck_image.width + sideboard_spacing, 0), 
                           sideboard_image)

        return result_image
    
    def generate_cost_curve_with_horizontal_leader_base(self, parsed_deck_list: ParsedDeckList) -> Optional[Image.Image]:
        if parsed_deck_list.has_cards == False:
            return None
        
        uniform_card_width, uniform_card_height = self._uniform_card_dimensions(parsed_deck_list)
        uniform_card_width_none_scaled, _ = self._uniform_card_dimensions_non_scaled(parsed_deck_list)
        scale_factor = uniform_card_width / uniform_card_width_none_scaled
        main_deck_image = self._create_main_deck_cost_curve_image(parsed_deck_list, uniform_card_width, uniform_card_height, scale_factor)
        
        has_sideboard = len(parsed_deck_list.sideboard) > 0

        if not self._deck_list_image_generator_styles(scale_factor).is_sideboard_enabled or not has_sideboard:
            sideboard_image = self._create_transparent_image(0, 0)
            sideboard_spacing = 0
        else:
            sideboard_image = self._create_sideboard_stacked_vertical_image(parsed_deck_list, uniform_card_width, uniform_card_height, scale_factor)
            sideboard_spacing = self._deck_list_image_generator_styles(scale_factor).sideboard_left_spacing_relative_to_main_deck

        main_deck_sideboard_image = self._create_transparent_image(main_deck_image.width + sideboard_image.width + sideboard_spacing, 
                                                      max(main_deck_image.height, sideboard_image.height))
        
        main_deck_sideboard_image.paste(main_deck_image, 
                           (0, 0), 
                           main_deck_image)
        main_deck_sideboard_image.paste(sideboard_image, 
                           (main_deck_image.width + sideboard_spacing, 0), 
                           sideboard_image)
        


        # Leader base should probably be centered on main deck instead of all cards
        leader_base_image = self._create_leader_base_stacked_horizontal_image(parsed_deck_list,
                                                                              uniform_card_height,
                                                                              uniform_card_width, scale_factor)

        result_image = self._create_transparent_image(max(main_deck_sideboard_image.width, leader_base_image.width), 
                                                      main_deck_sideboard_image.height + leader_base_image.height + self._deck_list_image_generator_styles(scale_factor).main_deck_row_spacing, 'entire-deck')
        result_image.paste(leader_base_image, 
                           (int(result_image.width / 2 - leader_base_image.width/ 2), 0), 
                           leader_base_image)
        result_image.paste(main_deck_sideboard_image, 
                           (int(result_image.width / 2 - main_deck_sideboard_image.width/ 2), leader_base_image.height + self._deck_list_image_generator_styles(scale_factor).main_deck_row_spacing), 
                           main_deck_sideboard_image)

        return result_image
    

class WorkerSignals(QObject):
    finished = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, 
                 fn: Callable[[], Tuple[Optional[QPixmap], Optional[Image.Image]]], 
                 parsed_deck_list: ParsedDeckList):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self._fn = fn
        self._parsed_deck_list = parsed_deck_list

    def run(self):
        pixmap, image = self._fn()
        self.signals.finished.emit((pixmap, image, self._parsed_deck_list))