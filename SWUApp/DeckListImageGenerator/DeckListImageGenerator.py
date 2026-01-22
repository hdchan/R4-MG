
from io import BytesIO
from typing import Callable, List, Optional, Set, Dict
import concurrent.futures
from PIL import Image
from PIL.ImageFile import ImageFile
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QObject, Signal
from AppCore.Config import Configuration
from AppCore.Models import LocalCardResource

from ..Models import (DeckListImageGeneratorStyles, ParsedDeckList,
                      SWUTradingCardBackedLocalCardResource)
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .DeckListImageGeneratorProtocol import DeckListImageGeneratorProtocol
from .BaseDeckListImageGenerator import BaseDeckListImageGenerator
from .ScaledDeckListImageGeneratorStyles import \
    ScaledDeckListImageGeneratorStyles


class ImagePropertiesContext:
    def __init__(self, 
                 max_width: int, 
                 max_height: int, 
                 scale_factor: float, 
                 unscaled_styles: DeckListImageGeneratorStyles, 
                 is_export: bool):
        self._max_width = max_width
        self._max_height = max_height
        self._scale_factor = scale_factor
        self._is_export = is_export
        self.main_top = 0
        self.main_left = 0
        
        self._unscaled_styles = unscaled_styles
        self._scaled_styles = ScaledDeckListImageGeneratorStyles.from_non_scaled_styles(unscaled_styles, scale_factor)

    @property
    def _is_preview(self) -> bool:
        return not self._scaled_styles.is_full_image_preview and not self._is_export

    @property
    def max_width(self) -> int:
        if self._is_preview:
            return int(self._max_width * self._scale_factor)
        return self._max_width
    
    @property
    def max_height(self) -> int:
        if self._is_preview:
            return int(self._max_height * self._scale_factor)
        return self._max_height

    @property
    def styles(self) -> DeckListImageGeneratorStyles:
        if self._is_preview:
            return self._scaled_styles
        else:
            return self._unscaled_styles

    @property
    def max_dimension(self) -> int:
        return max(self.max_height, self.max_width)
    
    def image_path_for_resource(self, local_resource: LocalCardResource) -> str:
        if self._is_preview:
            return local_resource.image_preview_path
        else:
            return local_resource.image_path

# https://stackoverflow.com/a/64504108
class TaskManager(QObject):
    finished = Signal(object)

    def __init__(self, parent=None, max_workers=None):
        super().__init__(parent)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    @property
    def executor(self):
        return self._executor

    def submit(self, fn, *args, **kwargs):
        future = self.executor.submit(fn, *args, **kwargs)
        future.add_done_callback(self._internal_done_callback)

    def _internal_done_callback(self, future):
        data = future.result()
        self.finished.emit(data)

class DeckListImageGenerator(BaseDeckListImageGenerator, DeckListImageGeneratorProtocol):

    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._configuration_manager = swu_app_dependencies_provider.configuration_manager
        self._asset_provider = swu_app_dependencies_provider.asset_provider
        self._is_loading = False
        self._manager = TaskManager(max_workers=1)
        self._manager.finished.connect(self.update_gui_fields)
        self._is_downloading_images = False
        self._image_resource_processor_provider = swu_app_dependencies_provider.image_resource_processor_provider

    def update_gui_fields(self, data):
        self._is_loading = False
        data[1](data[0][0], data[0][1])

    @property
    def _core_configuration(self) -> Configuration:
        return self._configuration_manager.configuration.core_configuration
    
    @property
    def _is_visual_debug(self) -> bool:
        return self._configuration_manager.configuration.deck_list_image_generator_styles.is_visual_debug

    @property
    def is_loading(self) -> bool:
        return self._is_loading or self._is_downloading_images

    def generate_image(self,
                       parsed_deck_list: ParsedDeckList,
                       is_export: bool, 
                       completion: Callable[[Optional[QPixmap], Optional[Image.Image]], None]):
        
        def measure():
            context = self._compute_context_for_non_leader_base(parsed_deck_list, is_export)

            if context.styles.layout_type == DeckListImageGeneratorStyles.LayoutType.GRID:
                result = self._generate_deck_grid(parsed_deck_list, context)
            elif context.styles.layout_type == DeckListImageGeneratorStyles.LayoutType.COST_CURVE:
                result = self._generate_cost_curve(parsed_deck_list, context)
            else:
                raise Exception("No such layout")

            byte_array = BytesIO()
            result.save(byte_array, format="PNG")
            byte_array.seek(0)
            
            qimage = QImage.fromData(byte_array.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            return ((pixmap, qimage), completion)
        
        def _completed():
            self._is_downloading_images = False
            self._is_loading = True
            self._manager.submit(measure)
            
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resources_multi(parsed_deck_list.all_cards, _completed)
        self._is_downloading_images = True

    def _generate_leader_base(self, 
                              result: Image.Image,
                              parsed_deck_list: ParsedDeckList,
                              context: ImagePropertiesContext) -> Image.Image:
        leader_base_mapped: List[ImageFile] = list(map(lambda x: Image.open(context.image_path_for_resource(x)), parsed_deck_list.first_leader_and_first_base))
        if context.styles.is_leader_base_on_top:
            leader_base_image = self.stitch_image_columns(leader_base_mapped, 
                                                          column_spacing=context.styles.leader_base_spacing_between, 
                                                          location='leader-base')
            context.main_top = leader_base_image.height + context.styles.leader_base_spacing_left_relative_to_main_deck
            result = self.stitch_image_rows([leader_base_image, result], h_alignment=self.HAlignment.CENTER, row_spacing=context.styles.leader_base_spacing_left_relative_to_main_deck)
        else:
            leader_base_image = self.stitch_image_rows(leader_base_mapped, 
                                                       row_spacing=context.styles.leader_base_spacing_between, 
                                                       location='leader-base')
            context.main_left = leader_base_image.width + context.styles.leader_base_spacing_left_relative_to_main_deck
            result = self.stitch_image_columns([leader_base_image, result], v_alignment=self.VAlignment.CENTER, column_spacing=context.styles.leader_base_spacing_left_relative_to_main_deck)
        return result

    def _generate_cost_curve(self,
                             parsed_deck_list: ParsedDeckList, 
                             context: ImagePropertiesContext) -> Image.Image:
        cost_curve_values = parsed_deck_list.main_deck_cost_curve_values
        unit_card_stack_cols: List[Image.Image] = []
        non_unit_card_stack_cols: List[Image.Image] = []

        for v in cost_curve_values:
            def create(cards: List[SWUTradingCardBackedLocalCardResource]):
                mapped = list(map(lambda x: Image.open(context.image_path_for_resource(x)), cards))
                card_stack = self._create_overlapping_cards(mapped, context, location='deck')
                return card_stack
            all_units_resources = parsed_deck_list.all_main_deck_units_with_cost(v, context.styles.is_sorted_alphabetically)
            unit_card_stack_cols.append(create(all_units_resources))

            all_non_units_resources = parsed_deck_list.all_main_deck_upgrades_and_events_with_cost(v, context.styles.is_sorted_alphabetically)
            non_unit_card_stack_cols.append(create(all_non_units_resources))

        result = self.stitch_image_rows([
            self.stitch_image_columns(unit_card_stack_cols, column_spacing=context.styles.main_deck_column_spacing),
            self.stitch_image_columns(non_unit_card_stack_cols, column_spacing=context.styles.main_deck_column_spacing)
        ], row_spacing=context.styles.main_deck_row_spacing)

        result = self._generate_leader_base(result, parsed_deck_list, context)

        if context.styles.is_sideboard_enabled:
            sideboard_col_mapped = list(map(lambda x: Image.open(context.image_path_for_resource(x)), parsed_deck_list.sideboard))
            sideboard_card_stack = self._create_overlapping_cards(sideboard_col_mapped, context, fill_empty=False, location='sideboard')

            spacer = self.create_canvas_image(0, context.main_top)
            sideboard_card_stack = self.stitch_image_rows([spacer, sideboard_card_stack])

            result = self.stitch_image_columns([
                result,
                sideboard_card_stack
            ], v_alignment=self.VAlignment.TOP,
              column_spacing=context.styles.sideboard_left_spacing_relative_to_main_deck)

        return result

    def _add_quantity_count(self, image: Image.Image, quantity: int) -> Image.Image:
        quantity_image = Image.open(self._asset_provider.image.card_quantity(quantity))
        scaled_quantity_image = quantity_image.copy().convert('RGBA')
        scale = 0.25
        scaled_quantity_image.thumbnail((image.width * scale, image.height * scale), Image.Resampling.BICUBIC)

        result = self.create_canvas_image(image.width, image.height + scaled_quantity_image.height // 2)
        result.paste(image, (0, 0), image)
        result.paste(scaled_quantity_image, (image.width // 2 - scaled_quantity_image.width // 2, image.height - scaled_quantity_image.height // 2), scaled_quantity_image)
        return result

    def _generate_deck_grid(self,
                             parsed_deck_list: ParsedDeckList, 
                             context: ImagePropertiesContext) -> Image.Image:
        main_deck_images: List[Image.Image] = []
        for c in parsed_deck_list.main_deck_cost_curve_values:
            resources = set(parsed_deck_list.main_deck_with_cost(c, context.styles.is_sorted_alphabetically))
            for r in resources:
                quantity = parsed_deck_list.card_count_main_deck(r)
                image = self._add_quantity_count(Image.open(context.image_path_for_resource(r)), quantity)
                main_deck_images.append(image)
        result = self.stitch_image_grid_right_to_down(main_deck_images, 
                                                      context.styles.grid_width,
                                                      column_spacing=context.styles.main_deck_column_spacing, 
                                                      row_spacing=context.styles.main_deck_row_spacing, 
                                                      location='deck')

        
        result = self._generate_leader_base(result, parsed_deck_list, context)

        if context.styles.is_sideboard_enabled:
            sideboard_images: List[Image.Image] = []
            for c in parsed_deck_list.sideboard_cost_curve_values:
                resources_set: Set[SWUTradingCardBackedLocalCardResource] = set()
                resources_with_cost = parsed_deck_list.sideboard_with_cost(c, context.styles.is_sorted_alphabetically)
                for r in resources_with_cost:
                    if r in resources_set:
                        continue
                    resources_set.add(r)
                    quantity = parsed_deck_list.card_count_sideboard(r)
                    image = self._add_quantity_count(Image.open(context.image_path_for_resource(r)), quantity)
                    sideboard_images.append(image)
            sideboard_grid = self.stitch_image_grid_right_to_down(sideboard_images, 
                                                                  context.styles.grid_width_sideboard, 
                                                                  column_spacing=context.styles.main_deck_column_spacing, 
                                                                  row_spacing=context.styles.main_deck_row_spacing,
                                                                  location='sideboard')
            spacer = self.create_canvas_image(context.main_left, 0)
            sideboard_grid = self.stitch_image_columns([spacer, sideboard_grid])
            result = self.stitch_image_rows([result, sideboard_grid], 
                                            h_alignment=self.HAlignment.LEFT,
                                            row_spacing=context.styles.sideboard_left_spacing_relative_to_main_deck)

        return result

    def _compute_context_for_non_leader_base(self, parsed_deck_list: ParsedDeckList, is_export: bool) -> ImagePropertiesContext:
        non_leader_and_base_cards = parsed_deck_list.all_cards_excluding_leader_base()
        unscaled_styles = self._configuration_manager.configuration.deck_list_image_generator_styles
        return self._compute_uniform_image_properties(non_leader_and_base_cards, unscaled_styles, is_export)

    def _compute_uniform_image_properties(self, 
                                          local_resources: List[LocalCardResource], 
                                          unscaled_styles: DeckListImageGeneratorStyles, 
                                          is_export: bool) -> ImagePropertiesContext:
        image_paths: List[ImageFile] = list(map(lambda x: Image.open(x.image_path), local_resources))
        max_width, max_height = self.uniform_card_dimensions(image_paths)
        image_preview_paths: List[ImageFile] = list(map(lambda x: Image.open(x.image_preview_path), local_resources))
        max_preview_width, _ = self.uniform_card_dimensions(image_preview_paths)
        return ImagePropertiesContext(max_width, max_height, max_preview_width / max_width, unscaled_styles, is_export)

    def create_canvas_image(self, 
                            width: int,
                            height: int, 
                            location: str = "") -> Image.Image:
        color_value = (0, 0, 0, 0)
        if self._core_configuration.is_developer_mode and self._is_visual_debug:
            if location == 'leader-base':
                color_value = 'green'
            if location == 'deck':
                color_value = 'red'
            if location == 'sideboard':
                color_value = 'green'
            if location == 'stitch-columns':
                color_value = 'grey'
            if location == 'stitch-rows':
                color_value = 'blue'
        return Image.new('RGBA', (width, height), color_value)

    def _create_overlapping_cards(self, 
                                  images: List[ImageFile],
                                  context: ImagePropertiesContext, 
                                  fill_empty: bool = True, 
                                  location: str = "deck") -> Image.Image:
        if len(images) == 0:
            if fill_empty:
                return self.create_canvas_image(context.max_width, context.max_height, location)
            return self.create_canvas_image(0, 0, location)
        height = 0
        for i, img in enumerate(images):
            if i == len(images) - 1:
                # fully reveal top most card
                height += context.max_height
            else:
                # obscure bottom cards
                height += int(context.max_height * context.styles.stacked_card_reveal_percentage)
        combined_image = self.create_canvas_image(context.max_width, height, location)
        
        curr_y = 0
        for i, img in enumerate(images):
            scaled_image = img.copy().convert('RGBA')
            scaled_image.thumbnail((context.max_dimension, context.max_dimension), Image.Resampling.BICUBIC)
            combined_image.paste(scaled_image, (0, curr_y), scaled_image)
            curr_y += int(context.max_height * context.styles.stacked_card_reveal_percentage)
        
        return combined_image