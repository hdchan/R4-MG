from typing import Dict, Any

class DeckListImageGeneratorStyles:
    def __init__(self,
                 sideboard_left_spacing_relative_to_main_deck: int, 
                 main_deck_column_spacing: int, 
                 main_deck_row_spacing: int, 
                 leader_base_spacing_between: int, 
                 leader_base_spacing_left_relative_to_main_deck: int, 
                 stacked_card_reveal_percentage: float, 
                 is_sideboard_enabled: bool, 
                 is_sorted_alphabetically: bool):
        self.sideboard_left_spacing_relative_to_main_deck = sideboard_left_spacing_relative_to_main_deck
        self.main_deck_column_spacing = main_deck_column_spacing
        self.main_deck_row_spacing = main_deck_row_spacing
        self.leader_base_spacing_between = leader_base_spacing_between
        self.leader_base_spacing_left_relative_to_main_deck = leader_base_spacing_left_relative_to_main_deck
        self.stacked_card_reveal_percentage = stacked_card_reveal_percentage
        self.is_sideboard_enabled = is_sideboard_enabled
        self.is_sorted_alphabetically = is_sorted_alphabetically

    class Keys: 
        SIDEBOARD_LEFT_SPACING_RELATIVE_TO_MAIN_DECK = 'sideboard_left_spacing_relative_to_main_deck'
        MAIN_DECK_COLUMN_SPACING = 'main_deck_column_spacing'
        MAIN_DECK_ROW_SPACING = 'main_deck_row_spacing'
        LEADER_BASE_SPACING_BETWEEN = 'leader_base_spacing_between'
        LEADER_BASE_SPACING_LEFT_RELATIVE_TO_MAIN_DECK = 'leader_base_spacing_left_relative_to_main_deck'
        STACKED_CARD_REVEAL_PERCENTAGE = 'stacked_card_reveal_percentage'
        IS_SIDEBOARD_ENABLED = 'is_sideboard_enabled'
        IS_SORTED_ALPHABETICALLY = 'is_sorted_alphabetically'

    def to_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            self.Keys.SIDEBOARD_LEFT_SPACING_RELATIVE_TO_MAIN_DECK: self.sideboard_left_spacing_relative_to_main_deck,
            self.Keys.MAIN_DECK_COLUMN_SPACING: self.main_deck_column_spacing,
            self.Keys.MAIN_DECK_ROW_SPACING: self.main_deck_row_spacing,
            self.Keys.LEADER_BASE_SPACING_BETWEEN: self.leader_base_spacing_between,
            self.Keys.LEADER_BASE_SPACING_LEFT_RELATIVE_TO_MAIN_DECK: self.leader_base_spacing_left_relative_to_main_deck,
            self.Keys.STACKED_CARD_REVEAL_PERCENTAGE: self.stacked_card_reveal_percentage,
            self.Keys.IS_SIDEBOARD_ENABLED: self.is_sideboard_enabled,
            self.Keys.IS_SORTED_ALPHABETICALLY: self.is_sorted_alphabetically
        }
        return data
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        default = DeckListImageGeneratorStyles.default_style()

        return cls(
            sideboard_left_spacing_relative_to_main_deck=json.get(cls.Keys.SIDEBOARD_LEFT_SPACING_RELATIVE_TO_MAIN_DECK, default.sideboard_left_spacing_relative_to_main_deck),
            main_deck_column_spacing=json.get(cls.Keys.MAIN_DECK_COLUMN_SPACING, default.main_deck_column_spacing),
            main_deck_row_spacing=json.get(cls.Keys.MAIN_DECK_ROW_SPACING, default.main_deck_row_spacing),
            leader_base_spacing_between=json.get(cls.Keys.LEADER_BASE_SPACING_BETWEEN, default.leader_base_spacing_between),
            leader_base_spacing_left_relative_to_main_deck=json.get(cls.Keys.LEADER_BASE_SPACING_LEFT_RELATIVE_TO_MAIN_DECK, default.leader_base_spacing_left_relative_to_main_deck),
            stacked_card_reveal_percentage=json.get(cls.Keys.STACKED_CARD_REVEAL_PERCENTAGE, default.stacked_card_reveal_percentage),
            is_sideboard_enabled=json.get(cls.Keys.IS_SIDEBOARD_ENABLED, default.is_sideboard_enabled),
            is_sorted_alphabetically=json.get(cls.Keys.IS_SORTED_ALPHABETICALLY, default.is_sorted_alphabetically),
        )
    
    @classmethod
    def default_style(cls):
        return cls(
            sideboard_left_spacing_relative_to_main_deck=80,
            main_deck_column_spacing=10,
            main_deck_row_spacing=40,
            leader_base_spacing_between=10,
            leader_base_spacing_left_relative_to_main_deck=80,
            stacked_card_reveal_percentage=0.15,
            is_sideboard_enabled=True,
            is_sorted_alphabetically=False,
        )