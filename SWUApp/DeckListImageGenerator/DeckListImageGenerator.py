
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
import asyncio
import threading
from concurrent.futures import ProcessPoolExecutor
import sys
from enum import Enum

# def DLIG_create_canvas_image(self,
#                             width: int,
#                             height: int,
#                             location: str = "") -> Image.Image:
#         color_value = (0, 0, 0, 0)
#         return Image.new('RGBA', (width, height), color_value)

def DLIG_create_canvas_image(width: int,
                            height: int, 
                            location: str = "",
                            is_debug: bool = False) -> Image.Image:
        color_value = (0, 0, 0, 0)
        if is_debug:
            if location == 'leader-base':
                color_value = 'green' # type: ignore
            if location == 'deck':
                color_value = 'red' # type: ignore
            if location == 'sideboard':
                color_value = 'green' # type: ignore
            if location == 'stitch-columns':
                color_value = 'grey' # type: ignore
            if location == 'stitch-rows':
                color_value = 'blue' # type: ignore
        return Image.new('RGBA', (width, height), color_value)

def DLIG_uniform_card_dimensions(image_paths: list[ImageFile]) -> tuple[int, int]:
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

class DLIG_VAlignment(int, Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2

class DLIG_HAlignment(int, Enum):
    LEFT = 3
    CENTER = 4
    RIGHT = 5

def DLIG_stitch_image_columns(images: list[Image.Image],
                            v_alignment: DLIG_VAlignment = DLIG_VAlignment.TOP,
                            column_spacing: int = 0, 
                            location: str = "stitch-columns", 
                            is_debug: bool = False) -> Image.Image:
    width = 0
    height = 0
    for i, img in enumerate(images):
        height = max(height, img.height)
        width += img.width
        if i < len(images) - 1:
            width += column_spacing
    combined_image = DLIG_create_canvas_image(width, height, location, is_debug)
    curr_x = 0
    for i, img in enumerate(images):
        if v_alignment == DLIG_VAlignment.CENTER:
            y = int(combined_image.height / 2 - img.height / 2)
            combined_image.paste(img, (curr_x, y), img)
        elif v_alignment == DLIG_VAlignment.BOTTOM:
            y = combined_image.height - img.height
            combined_image.paste(img, (curr_x, y), img)
        else:
            combined_image.paste(img, (curr_x, 0), img)
        curr_x += img.width
        if i < len(images) - 1:
            curr_x += column_spacing
    return combined_image

def DLIG_stitch_image_rows(images: list[Image.Image],
                        h_alignment: DLIG_HAlignment = DLIG_HAlignment.LEFT,
                        row_spacing: int = 0, 
                        location: str = "stitch-rows",
                        is_debug: bool = False) -> Image.Image:
    width = 0
    height = 0
    for i, img in enumerate(images):
        width = max(width, img.width)
        height += img.height
        if i < len(images) - 1:
            height += row_spacing
    
    combined_image = DLIG_create_canvas_image(width, height, location, is_debug)
    curr_y = 0
    for i, img in enumerate(images):
        if h_alignment == DLIG_HAlignment.CENTER:
            x = int(combined_image.width / 2 - img.width / 2)
            combined_image.paste(img, (x, curr_y), img)
        elif h_alignment == DLIG_HAlignment.RIGHT:
            x = combined_image.width - img.width
            combined_image.paste(img, (x, curr_y), img)
        else:
            combined_image.paste(img, (0, curr_y), img)
        curr_y += img.height
        if i < len(images) - 1:
            curr_y += row_spacing
    return combined_image

def DLIG_stitch_image_grid_right_to_down(images: list[Image.Image],
                                    grid_width: int,
                                    v_alignment: DLIG_VAlignment = DLIG_VAlignment.TOP, 
                                    column_spacing: int = 0, 
                                    h_alignment: DLIG_HAlignment = DLIG_HAlignment.LEFT,
                                    row_spacing: int = 0, 
                                    location: str = "stitch-grid", 
                                    is_debug: bool = False):
    sanitized_grid_width = max(grid_width, 1)
    rows: list[Image.Image] = []
    current_row: list[Image.Image] = []
    for i, img in enumerate(images):
        current_row.append(img)
        if (i + 1) % sanitized_grid_width == 0:
            row = DLIG_stitch_image_columns(current_row, v_alignment, column_spacing, location, is_debug)
            rows.append(row)
            current_row = []
        
    if len(current_row) > 0:
        row = DLIG_stitch_image_columns(current_row, v_alignment, column_spacing, location, is_debug)
        rows.append(row)
    return DLIG_stitch_image_rows(rows, h_alignment, row_spacing, location, is_debug)

class ImagePropertiesContext:
    def __init__(self, 
                 max_width: int, 
                 max_height: int, 
                 scale_factor: float, 
                 unscaled_styles: DeckListImageGeneratorStyles, 
                 is_export: bool, 
                 is_debug: bool):
        self._max_width = max_width
        self._max_height = max_height
        self._scale_factor = scale_factor
        self._is_export = is_export
        self._is_debug = is_debug
        self.main_top = 0
        self.main_left = 0
        
        self._unscaled_styles = unscaled_styles
        self._scaled_styles = ScaledDeckListImageGeneratorStyles.from_non_scaled_styles(unscaled_styles, scale_factor)

    @property
    def is_debug(self) -> bool:
        return self._is_debug

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

def DLIG_scale_image_to_context(image: Image.Image, context: ImagePropertiesContext) -> Image.Image:
        scaled_image = image.copy().convert('RGBA')
        scaled_image.thumbnail((context.max_dimension, context.max_dimension), Image.Resampling.BICUBIC)
        return scaled_image

def DLIG_create_overlapping_cards(images: List[ImageFile],
                                  context: ImagePropertiesContext, 
                                  fill_empty: bool = True, 
                                  location: str = "deck") -> Image.Image:
        if len(images) == 0:
            if fill_empty:
                return DLIG_create_canvas_image(context.max_width, context.max_height, location, context.is_debug)
            return DLIG_create_canvas_image(0, 0, location, context.is_debug)
        height = 0
        for i, img in enumerate(images):
            if i == len(images) - 1:
                # fully reveal top most card
                height += context.max_height
            else:
                # obscure bottom cards
                height += int(context.max_height * context.styles.stacked_card_reveal_percentage)
        combined_image = DLIG_create_canvas_image(context.max_width, height, location, context.is_debug)
        
        curr_y = 0
        for i, image in enumerate(images):
            scaled_image = DLIG_scale_image_to_context(image=image, context=context)
            combined_image.paste(scaled_image, (0, curr_y), scaled_image)
            curr_y += int(context.max_height * context.styles.stacked_card_reveal_percentage)
        
        return combined_image

def DLIG_compute_context_for_deck(parsed_deck_list: ParsedDeckList, is_export: bool, unscaled_styles: DeckListImageGeneratorStyles, is_debug: bool = False) -> ImagePropertiesContext:
        leader_and_base_cards = parsed_deck_list.first_leader_and_first_base
        leader_base_image_paths: list[ImageFile] = list(map(lambda x: Image.open(x.image_path), leader_and_base_cards))
        leader_base_max_height, leader_base_max_width = DLIG_uniform_card_dimensions(leader_base_image_paths) # Assuming leader and base are 90deg rotated

        rest_of_deck_cards = parsed_deck_list.all_cards_excluding_leader_base()
        image_paths: list[ImageFile] = list(map(lambda x: Image.open(x.image_path), rest_of_deck_cards))
        rest_of_deck_max_width, rest_of_deck_max_height = DLIG_uniform_card_dimensions(image_paths)


        leader_and_base_image_preview_paths: list[ImageFile] = list(map(lambda x: Image.open(x.image_preview_path), leader_and_base_cards))
        _, leader_and_base_max_preview_height = DLIG_uniform_card_dimensions(leader_and_base_image_preview_paths)

        rest_of_deck_image_preview_paths: list[ImageFile] = list(map(lambda x: Image.open(x.image_preview_path), rest_of_deck_cards))
        rest_of_deck_max_preview_width, _ = DLIG_uniform_card_dimensions(rest_of_deck_image_preview_paths)

        max_width = min(leader_base_max_height, rest_of_deck_max_width)
        max_height = min(leader_base_max_width, rest_of_deck_max_height)
        max_preview_width = min(leader_and_base_max_preview_height, rest_of_deck_max_preview_width)

        
        return ImagePropertiesContext(max_width, max_height, max_preview_width / max_width, unscaled_styles, is_export, is_debug)

def DLIG_generate_leader_base(result: Image.Image,
                              parsed_deck_list: ParsedDeckList,
                              context: ImagePropertiesContext) -> Image.Image:
        
        def scaled_leader_base(x: ImageFile):
            image =  Image.open(context.image_path_for_resource(x))
            scaled_image = DLIG_scale_image_to_context(image=image, context=context)
            return scaled_image

        leader_base_mapped: list[ImageFile] = list(map(scaled_leader_base, parsed_deck_list.first_leader_and_first_base))
        
        if context.styles.is_leader_base_on_top:
            leader_base_image = DLIG_stitch_image_columns(leader_base_mapped, 
                                                          column_spacing=context.styles.leader_base_spacing_between, 
                                                          location='leader-base', 
                                                          is_debug=context.is_debug)
            context.main_top = leader_base_image.height + context.styles.leader_base_spacing_left_relative_to_main_deck
            result = DLIG_stitch_image_rows([leader_base_image, result], h_alignment=DLIG_HAlignment.CENTER, row_spacing=context.styles.leader_base_spacing_left_relative_to_main_deck, is_debug=context.is_debug)
        else:
            leader_base_image = DLIG_stitch_image_rows(leader_base_mapped, 
                                                       row_spacing=context.styles.leader_base_spacing_between, 
                                                       location='leader-base', 
                                                       is_debug=context.is_debug)
            context.main_left = leader_base_image.width + context.styles.leader_base_spacing_left_relative_to_main_deck
            result = DLIG_stitch_image_columns([leader_base_image, result], v_alignment=DLIG_VAlignment.CENTER, column_spacing=context.styles.leader_base_spacing_left_relative_to_main_deck, is_debug=context.is_debug)
        return result

def DLIG_add_quantity_count(image: Image.Image, quantity_image: Image.Image) -> Image.Image:
        # quantity_image = Image.open(self._asset_provider.image.card_quantity(quantity))
        scaled_quantity_image = quantity_image.copy().convert('RGBA')
        scale = 0.25
        scaled_quantity_image.thumbnail((image.width * scale, image.height * scale), Image.Resampling.BICUBIC)

        result = DLIG_create_canvas_image(image.width, image.height + scaled_quantity_image.height // 2)
        result.paste(image, (0, 0), image)
        result.paste(scaled_quantity_image, (image.width // 2 - scaled_quantity_image.width // 2, image.height - scaled_quantity_image.height // 2), scaled_quantity_image)
        return result

def DLIG_generate_cost_curve(parsed_deck_list: ParsedDeckList, 
                             context: ImagePropertiesContext) -> Image.Image:
        cost_curve_values = parsed_deck_list.main_deck_cost_curve_values
        unit_card_stack_cols: list[Image.Image] = []
        non_unit_card_stack_cols: list[Image.Image] = []

        result = DLIG_create_canvas_image(0, 0)

        if context.styles.is_main_deck_enabled:
            for v in cost_curve_values:
                def create(cards: list[SWUTradingCardBackedLocalCardResource]):
                    mapped = list(map(lambda x: Image.open(context.image_path_for_resource(x)), cards))
                    card_stack = DLIG_create_overlapping_cards(mapped, context, location='deck')
                    return card_stack
                all_units_resources = parsed_deck_list.all_main_deck_units_with_cost(v, context.styles.is_sorted_alphabetically)
                unit_card_stack_cols.append(create(all_units_resources))

                all_non_units_resources = parsed_deck_list.all_main_deck_upgrades_and_events_with_cost(v, context.styles.is_sorted_alphabetically)
                non_unit_card_stack_cols.append(create(all_non_units_resources))

            result = DLIG_stitch_image_rows([
                DLIG_stitch_image_columns(unit_card_stack_cols, column_spacing=context.styles.main_deck_column_spacing, is_debug=context.is_debug),
                DLIG_stitch_image_columns(non_unit_card_stack_cols, column_spacing=context.styles.main_deck_column_spacing, is_debug=context.is_debug)
            ], row_spacing=context.styles.main_deck_row_spacing)

        if context.styles.is_leader_base_enabled:
            result = DLIG_generate_leader_base(result, parsed_deck_list, context)

        if context.styles.is_sideboard_enabled:
            sideboard_col_mapped = list(map(lambda x: Image.open(context.image_path_for_resource(x)), parsed_deck_list.sideboard))
            sideboard_card_stack = DLIG_create_overlapping_cards(sideboard_col_mapped, context, fill_empty=False, location='sideboard')

            spacer = DLIG_create_canvas_image(0, context.main_top)
            sideboard_card_stack = DLIG_stitch_image_rows([spacer, sideboard_card_stack], is_debug=context.is_debug)

            result = DLIG_stitch_image_columns([
                result,
                sideboard_card_stack
            ], v_alignment=DLIG_VAlignment.TOP,
              column_spacing=context.styles.sideboard_left_spacing_relative_to_main_deck, is_debug=context.is_debug)

        return result

# https://stackoverflow.com/a/64504108
class TaskManager(QObject):
    finished = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task = None
        
        # 1. Create a dedicated event loop for this manager
        self._loop = asyncio.new_event_loop()
        
        # 2. Run the loop indefinitely in a background thread
        self._thread = threading.Thread(
            target=self._loop.run_forever, 
            name="TaskManagerLoop", 
            daemon=True
        )
        self._thread.start()

    def submit(self, fn, *args, **kwargs):
        # 3. Cancel the existing task if it's currently running
        if self.task is not None and not self.task.done():
            # Use call_soon_threadsafe to interact with the background loop safely
            self._loop.call_soon_threadsafe(self.task.cancel)

        # 4. Invoke the async function with args to get the coroutine object
        coro = fn(*args, **kwargs)

        # 5. Safely schedule the coroutine onto the running background loop
        # This replaces asyncio.create_task()
        self.task = asyncio.run_coroutine_threadsafe(coro, self._loop)

        # 6. Attach the done callback
        self.task.add_done_callback(self._internal_done_callback)

    def _internal_done_callback(self, future):
        try:
            if future.cancelled():
                print("Task was successfully cancelled.")
                return
                
            data = future.result()
            
            # 7. Qt Signals are thread-safe! 
            # Emitting this here safely passes the data back to the UI thread.
            self.finished.emit(data)
            
        except Exception as e:
            print(f"Task encountered an error: {e}")

class ImageProcessor(QObject):
    finished = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Spin up a true multi-core process pool
        self._pool = ProcessPoolExecutor(max_workers=2)
        self._current_future = None
        self._current_job_id = 0

    def submit(self, fn):
        # 1. Increment Job ID. This acts as our "Cancellation Token"
        self._current_job_id += 1
        assigned_job_id = self._current_job_id
        # coro = fn(*args, **kwargs)
        # 2. Submit the heavy PIL task directly to the Process Pool
        future = self._pool.submit(fn)
        self._current_future = future

        # 3. Use a lightweight native thread to wait for this specific process
        # This keeps the main Qt UI thread completely unblocked!
        threading.Thread(
            target=self._wait_for_process, 
            args=(future, assigned_job_id), 
            daemon=True
        ).start()

    def _wait_for_process(self, future, assigned_job_id):
        try:
            # Block this background thread until the OS process finishes grinding pixels
            result_bytes = future.result()
            
            # 4. CANCELLATION CHECK:
            # If self._current_job_id has changed, it means the user submitted a 
            # new image while we were working. Discard this old result immediately!
            if assigned_job_id != self._current_job_id:
                print(f"Discarding stale job #{assigned_job_id}. Latest is #{self._current_job_id}")
                return

            # 5. Safe return to UI via Qt Signals
            self.finished.emit(result_bytes)

        except Exception as e:
            print(f"Image process failed: {e}")

class DeckListImageGenerator(DeckListImageGeneratorProtocol):

    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._configuration_manager = swu_app_dependencies_provider.configuration_manager
        self._asset_provider = swu_app_dependencies_provider.asset_provider
        self._is_loading = False
        self._manager = ImageProcessor()
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
        async def measure():
            try:
                unscaled_styles = self._configuration_manager.configuration.deck_list_image_generator_styles
                context = DLIG_compute_context_for_deck(parsed_deck_list, is_export, unscaled_styles, self._is_debug)

                if context.styles.layout_type == DeckListImageGeneratorStyles.LayoutType.GRID:
                    result = self._generate_deck_grid(parsed_deck_list, context)
                elif context.styles.layout_type == DeckListImageGeneratorStyles.LayoutType.COST_CURVE:
                    result = DLIG_generate_cost_curve(parsed_deck_list, context)
                else:
                    raise Exception("No such layout")

                byte_array = BytesIO()
                result.save(byte_array, format="PNG")
                byte_array.seek(0)
                
                qimage = QImage.fromData(byte_array.getvalue())
                pixmap = QPixmap.fromImage(qimage)
                return ((pixmap, qimage), completion)
            except Exception as e:
                raise ValueError(e) 
        
        def _completed():
            self._is_downloading_images = False
            self._is_loading = True
            self._manager.submit(measure)
            
        self._image_resource_processor_provider.image_resource_processor.async_store_local_resources_multi(parsed_deck_list.all_cards, _completed)
        self._is_downloading_images = True

    def _generate_deck_grid(self,
                             parsed_deck_list: ParsedDeckList, 
                             context: ImagePropertiesContext) -> Image.Image:

        def scale_and_add_quantity(r: SWUTradingCardBackedLocalCardResource, quantity: int) -> Image.Image:
            image = Image.open(context.image_path_for_resource(r))
            scaled_image = DLIG_scale_image_to_context(image=image, context=context)
            quantity_image = Image.open(self._asset_provider.image.card_quantity(quantity))
            image_with_quantity = DLIG_add_quantity_count(scaled_image, quantity_image)
            return image_with_quantity

        result = DLIG_create_canvas_image(0, 0)

        if context.styles.is_main_deck_enabled:
            main_deck_images: List[Image.Image] = []
            for c in parsed_deck_list.main_deck_cost_curve_values:
                resources = set(parsed_deck_list.main_deck_with_cost(c, context.styles.is_sorted_alphabetically))
                for r in resources:
                    quantity = parsed_deck_list.card_count_main_deck(r)
                    image_with_quantity = scale_and_add_quantity(r, quantity)
                    main_deck_images.append(image_with_quantity)
            result = DLIG_stitch_image_grid_right_to_down(main_deck_images, 
                                                        context.styles.grid_width,
                                                        column_spacing=context.styles.main_deck_column_spacing, 
                                                        row_spacing=context.styles.main_deck_row_spacing, 
                                                        location='deck', 
                                                        is_debug=context.is_debug)

        if context.styles.is_leader_base_enabled:
            result = DLIG_generate_leader_base(result, parsed_deck_list, context)

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
                    image_with_quantity = scale_and_add_quantity(r, quantity)
                    sideboard_images.append(image_with_quantity)
            sideboard_grid = DLIG_stitch_image_grid_right_to_down(sideboard_images, 
                                                                  context.styles.grid_width_sideboard, 
                                                                  column_spacing=context.styles.main_deck_column_spacing, 
                                                                  row_spacing=context.styles.main_deck_row_spacing,
                                                                  location='sideboard', 
                                                                  is_debug=context.is_debug)
            spacer = DLIG_create_canvas_image(context.main_left, 0)
            sideboard_grid = DLIG_stitch_image_columns([spacer, sideboard_grid])
            result = DLIG_stitch_image_rows([result, sideboard_grid], 
                                            h_alignment=DLIG_HAlignment.LEFT,
                                            row_spacing=context.styles.sideboard_left_spacing_relative_to_main_deck)

        return result

    @property
    def _is_debug(self) -> bool:
        return self._core_configuration.is_developer_mode and self._is_visual_debug