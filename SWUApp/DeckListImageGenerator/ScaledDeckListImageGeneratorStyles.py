
from ..Models import DeckListImageGeneratorStyles


class ScaledDeckListImageGeneratorStyles(DeckListImageGeneratorStyles):
    @classmethod
    def from_non_scaled_styles(cls, other: DeckListImageGeneratorStyles, scale_factor: float):
        return cls(
            sideboard_left_spacing_relative_to_main_deck = int(other.sideboard_left_spacing_relative_to_main_deck * scale_factor),
            main_deck_column_spacing = int(other.main_deck_column_spacing * scale_factor), 
            main_deck_row_spacing = int(other.main_deck_row_spacing * scale_factor), 
            leader_base_spacing_between = int(other.leader_base_spacing_between * scale_factor), 
            leader_base_spacing_left_relative_to_main_deck = int(other.leader_base_spacing_left_relative_to_main_deck * scale_factor), 
            stacked_card_reveal_percentage = other.stacked_card_reveal_percentage, 
            is_sideboard_enabled = other.is_sideboard_enabled, 
            is_sorted_alphabetically = other.is_sorted_alphabetically, 
            is_leader_base_on_top = other.is_leader_base_on_top, 
            is_visual_debug = other.is_visual_debug, 
            is_full_image_preview = other.is_full_image_preview,
            is_auto_generate_preview = other.is_auto_generate_preview,
            layout_type = other.layout_type,
            grid_width = other.grid_width,
            grid_width_sideboard = other.grid_width_sideboard
        )