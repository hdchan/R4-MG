
from typing import Optional

from PySide6.QtCore import QTimer

from R4UI import (HorizontalLabeledInputRow, LineEditFloat, LineEditInt,
                  PushButton, RCheckBox, RVerticallyExpandingSpacer, RWidget,
                  ScrollArea, VerticalBoxLayout, RObjectComboBox)

from ..Config.SWUAppConfiguration import SWUAppConfigurationManager
from ..DeckListImageGenerator.DeckListImageGeneratorProtocol import (
    DeckListImageGeneratorProtocol, DeckListImageGeneratorProviding)
from ..Models.DeckListImageGeneratorStyles import DeckListImageGeneratorStyles

class DraftListImagePreviewInspectorPanelViewControllerDelegate:
    def option_did_update(self) -> None:
        pass

    def regenerate_was_clicked(self) -> None:
        pass

class DraftListImagePreviewInspectorPanelViewController(RWidget):
    def __init__(self, 
                 image_generator_provider: DeckListImageGeneratorProviding, 
                 delegate: DraftListImagePreviewInspectorPanelViewControllerDelegate, 
                 configuration_manager: SWUAppConfigurationManager):
        super().__init__()
        self._image_generator_provider = image_generator_provider
        self._configuration_manager = configuration_manager
        self.delegate: Optional[DraftListImagePreviewInspectorPanelViewControllerDelegate] = delegate
        self._deck_list_image_generator_styles = configuration_manager.configuration.deck_list_image_generator_styles

        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self._save_config_and_notify)
        self.debounce_time = 1000

        self._setup_view()
    
    @property
    def _image_generator(self) -> DeckListImageGeneratorProtocol:
        return self._image_generator_provider.image_generator

    def _start_save_timer(self):
        self._save_async_timer.stop()
        self._save_async_timer.start(self.debounce_time)

    def _save_config_and_notify(self):
        deck_list_styles = self._configuration_manager.configuration.deck_list_image_generator_styles
        
        deck_list_styles.is_leader_base_on_top = self._deck_list_image_generator_styles.is_leader_base_on_top
        deck_list_styles.sideboard_left_spacing_relative_to_main_deck = self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck
        deck_list_styles.main_deck_column_spacing = self._deck_list_image_generator_styles.main_deck_column_spacing
        deck_list_styles.main_deck_row_spacing = self._deck_list_image_generator_styles.main_deck_row_spacing
        deck_list_styles.leader_base_spacing_between = self._deck_list_image_generator_styles.leader_base_spacing_between
        deck_list_styles.leader_base_spacing_left_relative_to_main_deck = self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck
        deck_list_styles.stacked_card_reveal_percentage = self._deck_list_image_generator_styles.stacked_card_reveal_percentage
        deck_list_styles.is_sideboard_enabled = self._deck_list_image_generator_styles.is_sideboard_enabled
        deck_list_styles.is_sorted_alphabetically = self._deck_list_image_generator_styles.is_sorted_alphabetically
        deck_list_styles.layout_type = self._deck_list_image_generator_styles.layout_type

        deck_list_styles.is_full_image_preview = self._deck_list_image_generator_styles.is_full_image_preview
        deck_list_styles.is_auto_generate_preview = self._deck_list_image_generator_styles.is_auto_generate_preview
        deck_list_styles.is_visual_debug = self._deck_list_image_generator_styles.is_visual_debug
        deck_list_styles.grid_width = self._deck_list_image_generator_styles.grid_width
        deck_list_styles.grid_width_sideboard = self._deck_list_image_generator_styles.grid_width_sideboard

        self._configuration_manager.save_deck_list_image_generator_styles(deck_list_styles)
        self._notify_delegate()

    def _notify_delegate(self):
        if self.delegate is not None:
            self.delegate.option_did_update()


    def _is_leader_base_on_top_updated(self, val: bool):
        self._deck_list_image_generator_styles.is_leader_base_on_top = val
        self._start_save_timer()

    def _sideboard_left_spacing_relative_to_main_deck_updated(self, val: int):
        self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck = val
        self._start_save_timer()

    def _main_deck_column_spacing_updated(self, val: int):
        self._deck_list_image_generator_styles.main_deck_column_spacing = val
        self._start_save_timer()

    def _main_deck_row_spacing_updated(self, val: int):
        self._deck_list_image_generator_styles.main_deck_row_spacing = val
        self._start_save_timer()

    def _leader_base_spacing_between_updated(self, val: int):
        self._deck_list_image_generator_styles.leader_base_spacing_between = val
        self._start_save_timer()

    def _leader_base_spacing_left_relative_to_main_deck_updated(self, val: int):
        self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck = val
        self._start_save_timer()

    def _sideboard_box_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_sideboard_enabled = val
        self._start_save_timer()

    def _alphabetical_box_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_sorted_alphabetically = val
        self._start_save_timer()

    def _visual_debug_box_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_visual_debug = val
        self._start_save_timer()

    def _full_image_preview_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_full_image_preview = val
        self._start_save_timer()

    def _auto_generate_preview_changed(self, val: bool):
        self._deck_list_image_generator_styles.is_auto_generate_preview = val
        self._start_save_timer()

    def _stacked_card_reveal_percentage_updated(self, val: float):
        self._deck_list_image_generator_styles.stacked_card_reveal_percentage = val
        self._start_save_timer()

    def _layout_type_updated(self):
        self._deck_list_image_generator_styles.layout_type = self._layout_type_dropdown.current_data
        self._start_save_timer()

    def _grid_width_updated(self, val: int):
        self._deck_list_image_generator_styles.grid_width = val
        self._start_save_timer()

    def _grid_width_sideboard_updated(self, val: int):
        self._deck_list_image_generator_styles.grid_width_sideboard = val
        self._start_save_timer()

    def _setup_view(self):
        self._layout_type_dropdown = RObjectComboBox([
            (DeckListImageGeneratorStyles.LayoutType.COST_CURVE.value, DeckListImageGeneratorStyles.LayoutType.COST_CURVE),
            (DeckListImageGeneratorStyles.LayoutType.GRID.value, DeckListImageGeneratorStyles.LayoutType.GRID)
        ])
        self._layout_type_dropdown.setCurrentText(self._deck_list_image_generator_styles.layout_type.value)
        self._layout_type_dropdown.currentIndexChanged.connect(self._layout_type_updated)

        vertical_layout = VerticalBoxLayout([
            HorizontalLabeledInputRow("Layout type", self._layout_type_dropdown),

            HorizontalLabeledInputRow("Leader and Base on top (OFF = left side)", RCheckBox(self._is_leader_base_on_top_updated, self._deck_list_image_generator_styles.is_leader_base_on_top)),

            HorizontalLabeledInputRow("Show sideboard", RCheckBox(self._sideboard_box_changed, self._deck_list_image_generator_styles.is_sideboard_enabled)),

            HorizontalLabeledInputRow("Sort alphabetically", RCheckBox(self._alphabetical_box_changed, self._deck_list_image_generator_styles.is_sorted_alphabetically)),

            HorizontalLabeledInputRow("Sideboard spacing relative to main deck", 
                                      LineEditInt(self._deck_list_image_generator_styles.sideboard_left_spacing_relative_to_main_deck, 
                                                  self._sideboard_left_spacing_relative_to_main_deck_updated)),

            HorizontalLabeledInputRow("Main deck column spacing", 
                                      LineEditInt(self._deck_list_image_generator_styles.main_deck_column_spacing, 
                                                  self._main_deck_column_spacing_updated)),

            HorizontalLabeledInputRow("Main deck row spacing", 
                                      LineEditInt(self._deck_list_image_generator_styles.main_deck_row_spacing, 
                                                  self._main_deck_row_spacing_updated)),

            HorizontalLabeledInputRow("Leader Base spacing between each other", 
                                      LineEditInt(self._deck_list_image_generator_styles.leader_base_spacing_between, 
                                                  self._leader_base_spacing_between_updated)),

            HorizontalLabeledInputRow("Leader Base spacing relative to main deck", 
                                      LineEditInt(self._deck_list_image_generator_styles.leader_base_spacing_left_relative_to_main_deck, 
                                                  self._leader_base_spacing_left_relative_to_main_deck_updated)),

            HorizontalLabeledInputRow("Stacked card reveal percentage", 
                                      LineEditFloat(self._deck_list_image_generator_styles.stacked_card_reveal_percentage, 
                                                  self._stacked_card_reveal_percentage_updated)),
            
            HorizontalLabeledInputRow("Grid width main deck", 
                                      LineEditInt(self._deck_list_image_generator_styles.grid_width, 
                                                  self._grid_width_updated)),

            HorizontalLabeledInputRow("Grid width sideboard", 
                                      LineEditInt(self._deck_list_image_generator_styles.grid_width_sideboard, 
                                                  self._grid_width_sideboard_updated)),

            HorizontalLabeledInputRow("Full image preview (⚠️: This will increase image generation duration and memory usage)", RCheckBox(self._full_image_preview_changed, self._deck_list_image_generator_styles.is_full_image_preview)).set_word_wrap(True),

            HorizontalLabeledInputRow("Auto generate preview (⚠️: This will increase CPU usage)", RCheckBox(self._auto_generate_preview_changed, self._deck_list_image_generator_styles.is_auto_generate_preview))
        ]).add_spacer(RVerticallyExpandingSpacer())

        self.regenerate_button = PushButton("Regenerate", self._handle_regenerate)

        VerticalBoxLayout([
            ScrollArea(vertical_layout),
            self.regenerate_button
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)

        if self._configuration_manager.configuration.core_configuration.is_developer_mode:
            vertical_layout.add_widget(HorizontalLabeledInputRow("Visual debug", RCheckBox(self._visual_debug_box_changed, self._deck_list_image_generator_styles.is_visual_debug)),)

    def _handle_regenerate(self):
        if self.delegate is not None:
            self.delegate.regenerate_was_clicked()