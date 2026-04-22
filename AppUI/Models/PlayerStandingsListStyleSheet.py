from typing import Optional, Dict, Any

class PlayerStandingsListStyleSheet:
    def __init__(self,
                 container_padding_left: int, 
                 container_padding_top: int, 
                 container_padding_right: int, 
                 container_padding_bottom: int, 
                 container_background_color: str, 

                 cell_spacing: int,
                 cell_content_spacing: int,
                 cell_padding_left: int,
                 cell_padding_top: int,
                 cell_padding_right: int,
                 cell_padding_bottom: int,
                 cell_background_color: str, 

                 cell_font_color: str, 
                 cell_font_size: int, 
                 cell_font_path: Optional[str], 

                 rank_cell_font_color: str, 
                 rank_cell_font_size: int, 
                 rank_cell_font_path: Optional[str], 

                 window_header_padding_left: int, 
                 window_header_padding_top: int, 
                 window_header_padding_right: int, 
                 window_header_padding_bottom: int, 
                 window_header_background_color: str, 
                 window_header_font_color: str, 
                 window_header_font_size: int, 
                 window_header_font_path: Optional[str]):
        self.container_padding_left = container_padding_left
        self.container_padding_top = container_padding_top
        self.container_padding_right = container_padding_right
        self.container_padding_bottom = container_padding_bottom
        self.container_background_color = container_background_color

        self.cell_spacing = cell_spacing
        self.cell_content_spacing = cell_content_spacing
        self.cell_padding_left = cell_padding_left
        self.cell_padding_top = cell_padding_top
        self.cell_padding_right = cell_padding_right
        self.cell_padding_bottom = cell_padding_bottom
        self.cell_background_color = cell_background_color

        self.cell_font_color = cell_font_color
        self.cell_font_size = cell_font_size
        self.cell_font_path = cell_font_path

        self.rank_cell_font_color = rank_cell_font_color
        self.rank_cell_font_size = rank_cell_font_size
        self.rank_cell_font_path = rank_cell_font_path

        self.window_header_padding_left = window_header_padding_left 
        self.window_header_padding_top = window_header_padding_top 
        self.window_header_padding_right = window_header_padding_right  
        self.window_header_padding_bottom = window_header_padding_bottom 
        self.window_header_background_color = window_header_background_color 
        self.window_header_font_color = window_header_font_color 
        self.window_header_font_size = window_header_font_size 
        self.window_header_font_path = window_header_font_path 

    class Keys: 
        CONTAINER_PADDING_LEFT = 'container_padding_left'
        CONTAINER_PADDING_TOP = 'container_padding_top'
        CONTAINER_PADDING_RIGHT = 'container_padding_right'
        CONTAINER_PADDING_BOTTOM = 'container_padding_bottom'
        CONTAINER_BACKGROUND_COLOR = 'container_background_color'

        CELL_SPACING = 'cell_spacing'
        CELL_CONTENT_SPACING = 'cell_content_spacing'
        CELL_PADDING_LEFT = 'cell_padding_left'
        CELL_PADDING_TOP = 'cell_padding_top'
        CELL_PADDING_RIGHT = 'cell_padding_right'
        CELL_PADDING_BOTTOM = 'cell_padding_bottom'
        CELL_BACKGROUND_COLOR = 'cell_background_color'

        CELL_FONT_COLOR = 'cell_font_color'
        CELL_FONT_SIZE = 'cell_font_size'
        CELL_FONT_PATH = 'cell_font_path'

        RANK_CELL_FONT_COLOR = 'rank_cell_font_color'
        RANK_CELL_FONT_SIZE = 'rank_cell_font_size'
        RANK_CELL_FONT_PATH = 'rank_cell_font_path'

        WINDOW_HEADER_PADDING_LEFT = 'window_header_padding_left'
        WINDOW_HEADER_PADDING_TOP = 'window_header_padding_top'
        WINDOW_HEADER_PADDING_RIGHT = 'window_header_padding_right'
        WINDOW_HEADER_PADDING_BOTTOM = 'window_header_padding_bottom'
        WINDOW_HEADER_BACKGROUND_COLOR = 'window_header_background_color'
        WINDOW_HEADER_FONT_COLOR = 'window_header_font_color'
        WINDOW_HEADER_FONT_SIZE = 'window_header_font_size'
        WINDOW_HEADER_FONT_PATH = 'window_header_font_path'


    def to_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            self.Keys.CONTAINER_PADDING_LEFT: self.container_padding_left,
            self.Keys.CONTAINER_PADDING_TOP: self.container_padding_top,
            self.Keys.CONTAINER_PADDING_RIGHT: self.container_padding_right,
            self.Keys.CONTAINER_PADDING_BOTTOM: self.container_padding_bottom,
            self.Keys.CONTAINER_BACKGROUND_COLOR: self.container_background_color,

            self.Keys.CELL_SPACING: self.cell_spacing,
            self.Keys.CELL_CONTENT_SPACING: self.cell_content_spacing,
            self.Keys.CELL_PADDING_LEFT: self.cell_padding_left,
            self.Keys.CELL_PADDING_TOP: self.cell_padding_top,
            self.Keys.CELL_PADDING_RIGHT: self.cell_padding_right,
            self.Keys.CELL_PADDING_BOTTOM: self.cell_padding_bottom,
            self.Keys.CELL_BACKGROUND_COLOR: self.cell_background_color,

            self.Keys.CELL_FONT_COLOR: self.cell_font_color,
            self.Keys.CELL_FONT_SIZE: self.cell_font_size,
            self.Keys.CELL_FONT_PATH: self.cell_font_path,

            self.Keys.RANK_CELL_FONT_COLOR: self.rank_cell_font_color,
            self.Keys.RANK_CELL_FONT_SIZE: self.rank_cell_font_size,
            self.Keys.RANK_CELL_FONT_PATH: self.rank_cell_font_path,

            self.Keys.WINDOW_HEADER_PADDING_LEFT: self.window_header_padding_left,
            self.Keys.WINDOW_HEADER_PADDING_TOP: self.window_header_padding_top,
            self.Keys.WINDOW_HEADER_PADDING_RIGHT: self.window_header_padding_right,
            self.Keys.WINDOW_HEADER_PADDING_BOTTOM: self.window_header_padding_bottom,
            self.Keys.WINDOW_HEADER_BACKGROUND_COLOR: self.window_header_background_color,
            self.Keys.WINDOW_HEADER_FONT_COLOR: self.window_header_font_color,
            self.Keys.WINDOW_HEADER_FONT_SIZE: self.window_header_font_size,
            self.Keys.WINDOW_HEADER_FONT_PATH: self.window_header_font_path
        }
        return data
        
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        default = PlayerStandingsListStyleSheet.default_style()
        
        return cls(
            container_padding_left=json.get(cls.Keys.CONTAINER_PADDING_LEFT, default.container_padding_left),
            container_padding_top=json.get(cls.Keys.CONTAINER_PADDING_TOP, default.container_padding_top),
            container_padding_right=json.get(cls.Keys.CONTAINER_PADDING_RIGHT, default.container_padding_right),
            container_padding_bottom=json.get(cls.Keys.CONTAINER_PADDING_BOTTOM, default.container_padding_bottom),
            container_background_color=json.get(cls.Keys.CONTAINER_BACKGROUND_COLOR, default.container_background_color),

            cell_spacing=json.get(cls.Keys.CELL_SPACING, default.cell_spacing),
            cell_content_spacing=json.get(cls.Keys.CELL_CONTENT_SPACING, default.cell_content_spacing),
            cell_padding_left=json.get(cls.Keys.CELL_PADDING_LEFT, default.cell_padding_left),
            cell_padding_top=json.get(cls.Keys.CELL_PADDING_TOP, default.cell_padding_top),
            cell_padding_right=json.get(cls.Keys.CELL_PADDING_RIGHT, default.cell_padding_right),
            cell_padding_bottom=json.get(cls.Keys.CELL_PADDING_BOTTOM, default.cell_padding_bottom),
            cell_background_color=json.get(cls.Keys.CELL_BACKGROUND_COLOR, default.cell_background_color),

            cell_font_color=json.get(cls.Keys.CELL_FONT_COLOR, default.cell_font_color),
            cell_font_size=json.get(cls.Keys.CELL_FONT_SIZE, default.cell_font_size),
            cell_font_path=json.get(cls.Keys.CELL_FONT_PATH, default.cell_font_path),

            rank_cell_font_color=json.get(cls.Keys.RANK_CELL_FONT_COLOR, default.rank_cell_font_color),
            rank_cell_font_size=json.get(cls.Keys.RANK_CELL_FONT_SIZE, default.rank_cell_font_size),
            rank_cell_font_path=json.get(cls.Keys.RANK_CELL_FONT_PATH, default.rank_cell_font_path),

            window_header_padding_left=json.get(cls.Keys.WINDOW_HEADER_PADDING_LEFT, default.window_header_padding_left),
            window_header_padding_top=json.get(cls.Keys.WINDOW_HEADER_PADDING_TOP, default.window_header_padding_top),
            window_header_padding_right=json.get(cls.Keys.WINDOW_HEADER_PADDING_RIGHT, default.window_header_padding_right),
            window_header_padding_bottom=json.get(cls.Keys.WINDOW_HEADER_PADDING_BOTTOM, default.window_header_padding_bottom),
            window_header_background_color=json.get(cls.Keys.WINDOW_HEADER_BACKGROUND_COLOR, default.window_header_background_color),
            window_header_font_color=json.get(cls.Keys.WINDOW_HEADER_FONT_COLOR, default.window_header_font_color),
            window_header_font_size=json.get(cls.Keys.WINDOW_HEADER_FONT_SIZE, default.window_header_font_size),
            window_header_font_path=json.get(cls.Keys.WINDOW_HEADER_FONT_PATH, default.window_header_font_path),
        )
        
    @classmethod
    def default_style(cls):
        return cls(
            container_padding_left=10,
            container_padding_top=10,
            container_padding_right=10,
            container_padding_bottom=10,
            container_background_color='black',

            cell_spacing=10,
            cell_content_spacing=10,
            cell_padding_left=5,
            cell_padding_top=1,
            cell_padding_right=5,
            cell_padding_bottom=1,
            cell_background_color='black',

            cell_font_color='white',
            cell_font_size=16,
            cell_font_path=None,

            rank_cell_font_color='yellow',
            rank_cell_font_size=16,
            rank_cell_font_path=None,

            window_header_padding_left=10,
            window_header_padding_top=10,
            window_header_padding_right=10,
            window_header_padding_bottom=10,
            window_header_background_color='black',
            window_header_font_color='white',
            window_header_font_size=20,
            window_header_font_path=None,
        )
    
    def set_container_padding_left(self, value: int) -> None:
        self.container_padding_left = value
    
    def set_container_padding_top(self, value: int) -> None:
        self.container_padding_top = value
    
    def set_container_padding_right(self, value: int) -> None:
        self.container_padding_right = value
    
    def set_container_padding_bottom(self, value: int) -> None:
        self.container_padding_bottom = value
    
    def set_container_background_color(self, value: str) -> None:
        self.container_background_color = value
    
    def set_cell_spacing(self, value: int) -> None:
        self.cell_spacing = value
    
    def set_cell_content_spacing(self, value: int) -> None:
        self.cell_content_spacing = value
    
    def set_cell_padding_left(self, value: int) -> None:
        self.cell_padding_left = value
    
    def set_cell_padding_top(self, value: int) -> None:
        self.cell_padding_top = value
    
    def set_cell_padding_right(self, value: int) -> None:
        self.cell_padding_right = value
    
    def set_cell_padding_bottom(self, value: int) -> None:
        self.cell_padding_bottom = value
    
    def set_cell_background_color(self, value: str) -> None:
        self.cell_background_color = value
    

    def set_cell_font_color(self, value: str) -> None:
        self.cell_font_color = value
    
    def set_cell_font_size(self, value: int) -> None:
        self.cell_font_size = value
    
    def set_cell_font_path(self, value: Optional[str]) -> None:
        self.cell_font_path = value


    def set_rank_cell_font_color(self, value: str) -> None:
        self.rank_cell_font_color = value

    def set_rank_cell_font_size(self, value: int) -> None:
        self.rank_cell_font_size = value

    def set_rank_cell_font_path(self, value: Optional[str]) -> None:
        self.rank_cell_font_path = value


    def set_window_header_padding_left(self, value: int) -> None:
        self.window_header_padding_left = value
    
    def set_window_header_padding_top(self, value: int) -> None:
        self.window_header_padding_top = value

    def set_window_header_padding_right(self, value: int) -> None:
        self.window_header_padding_right = value

    def set_window_header_padding_bottom(self, value: int) -> None:
        self.window_header_padding_bottom = value
    
    def set_window_header_background_color(self, value: str) -> None:
        self.window_header_background_color = value
    
    def set_window_header_font_color(self, value: str) -> None:
        self.window_header_font_color = value
    
    def set_window_header_font_size(self, value: int) -> None:
        self.window_header_font_size = value
    
    def set_window_header_font_path(self, value: Optional[str]) -> None:
        self.window_header_font_path = value