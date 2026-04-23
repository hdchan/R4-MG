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
                 cell_aspect_image_size: int,
                 cell_font_path: Optional[str]):
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
            self.Keys.CELL_ASPECT_IMAGE_SIZE: self.cell_aspect_image_size,
            self.Keys.INTERVAL_CELL_STYLES: list(map(lambda x: x.to_data(), self.interval_cell_styles)),
            self.Keys.CELL_FONT_PATH: self.cell_font_path,
            self.Keys.CELL_HEADER_PADDING_LEFT: self.cell_header_padding_left,
            self.Keys.CELL_HEADER_PADDING_TOP: self.cell_header_padding_top,
            self.Keys.CELL_HEADER_PADDING_RIGHT: self.cell_header_padding_right,
            self.Keys.CELL_HEADER_PADDING_BOTTOM: self.cell_header_padding_bottom,
            self.Keys.CELL_HEADER_BACKGROUND_COLOR: self.cell_header_background_color,
            self.Keys.CELL_HEADER_FONT_COLOR: self.cell_header_font_color,
            self.Keys.CELL_HEADER_FONT_SIZE: self.cell_header_font_size,
            self.Keys.CELL_HEADER_FONT_PATH: self.cell_header_font_path,
            self.Keys.CELL_HEADER_SPACING: self.cell_header_spacing
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
            cell_aspect_image_size=json.get(cls.Keys.CELL_ASPECT_IMAGE_SIZE, default.cell_aspect_image_size),
            cell_font_path=json.get(cls.Keys.CELL_FONT_PATH, default.cell_font_path)
        )
        
    @classmethod
    def default_style(cls):
        return cls(
            container_padding_left=1,
            container_padding_top=1,
            container_padding_right=1,
            container_padding_bottom=1,
            container_background_color='white',
            cell_spacing=2,
            cell_content_spacing=1,
            cell_padding_left=5,
            cell_padding_top=1,
            cell_padding_right=5,
            cell_padding_bottom=1,
            cell_background_color='grey',
            cell_font_color='white',
            cell_font_size=9,
            cell_aspect_image_size=20,
            cell_font_path=None
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