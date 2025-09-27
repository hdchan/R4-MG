from typing import Any, Dict, Optional, List

class DraftListCellStyleSheet():
    def __init__(self, 
                 cell_font_color: str, 
                 cell_background_color: str):
        self.cell_font_color = cell_font_color
        self.cell_background_color = cell_background_color

    class Keys:
        CELL_FONT_COLOR = 'cell_font_color'
        CELL_BACKGROUND_COLOR = 'cell_background_color'
        
    def to_data(self) -> Dict[str, Any]:
        """Convert the cell style sheet properties to a dictionary format"""
        return {
            self.Keys.CELL_FONT_COLOR: self.cell_font_color,
            self.Keys.CELL_BACKGROUND_COLOR: self.cell_background_color
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        """Create a cell style sheet instance from JSON data"""
        default_style = DraftListCellStyleSheet.default_style()
        return cls(
            cell_font_color=json.get(cls.Keys.CELL_FONT_COLOR, default_style.cell_font_color),
            cell_background_color=json.get(cls.Keys.CELL_BACKGROUND_COLOR, default_style.cell_background_color)
        )
        
    @classmethod
    def default_style(cls):
        """Create a style sheet instance from JSON data"""
        return cls(
            cell_font_color='white',
            cell_background_color='grey'
        )

class DraftListStyleSheet():
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
                 interval_cell_styles: list[DraftListCellStyleSheet],
                 is_list_aggregated: bool,
                 container_background_image_path: Optional[str], 
                 cell_font_path: Optional[str],
                 cell_header_padding_left: int,
                 cell_header_padding_top: int,
                 cell_header_padding_right: int,
                 cell_header_padding_bottom: int,
                 cell_header_background_color: str,
                 cell_header_font_color: str,
                 cell_header_font_size: int,
                 cell_header_font_path: Optional[str], 
                 cell_header_spacing: int):
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
        self.cell_aspect_image_size = cell_aspect_image_size
        self.interval_cell_styles = interval_cell_styles
        self.is_list_aggregated = is_list_aggregated
        self.container_background_image_path = container_background_image_path
        self.cell_font_path = cell_font_path
        self.cell_header_padding_left = cell_header_padding_left
        self.cell_header_padding_top = cell_header_padding_top
        self.cell_header_padding_right = cell_header_padding_right
        self.cell_header_padding_bottom = cell_header_padding_bottom
        self.cell_header_background_color = cell_header_background_color
        self.cell_header_font_color = cell_header_font_color
        self.cell_header_font_size = cell_header_font_size
        self.cell_header_font_path = cell_header_font_path
        self.cell_header_spacing = cell_header_spacing
        
    class Keys: 
        CONTAINER_PADDING_LEFT = 'container_padding_left'
        CONTAINER_PADDING_TOP = 'container_padding_top'
        CONTAINER_PADDING_RIGHT = 'container_padding_right'
        CONTAINER_PADDING_BOTTOM = 'container_padding_bottom'
        CONTAINER_BACKGROUND_COLOR = 'container_background_color'
        CONTAINER_BACKGROUND_IMAGE_PATH = 'container_background_image_path'
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
        CELL_ASPECT_IMAGE_SIZE = 'cell_aspect_image_size'
        INTERVAL_CELL_STYLES = 'interval_cell_styles'
        IS_LIST_AGGREGATED = 'is_list_aggregated'
        CELL_HEADER_PADDING_LEFT = 'cell_header_padding_left'
        CELL_HEADER_PADDING_TOP = 'cell_header_padding_top'
        CELL_HEADER_PADDING_RIGHT = 'cell_header_padding_right'
        CELL_HEADER_PADDING_BOTTOM = 'cell_header_padding_bottom'
        CELL_HEADER_BACKGROUND_COLOR = 'cell_header_background_color'
        CELL_HEADER_FONT_COLOR = 'cell_header_font_color'
        CELL_HEADER_FONT_SIZE = 'cell_header_font_size'
        CELL_HEADER_FONT_PATH = 'cell_header_font_path'
        CELL_HEADER_SPACING = 'cell_header_spacing'
        
    def to_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            self.Keys.CONTAINER_PADDING_LEFT: self.container_padding_left,
            self.Keys.CONTAINER_PADDING_TOP: self.container_padding_top,
            self.Keys.CONTAINER_PADDING_RIGHT: self.container_padding_right,
            self.Keys.CONTAINER_PADDING_BOTTOM: self.container_padding_bottom,
            self.Keys.CONTAINER_BACKGROUND_COLOR: self.container_background_color,
            self.Keys.CONTAINER_BACKGROUND_IMAGE_PATH: self.container_background_image_path,
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
            self.Keys.IS_LIST_AGGREGATED: self.is_list_aggregated,
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
        default = DraftListStyleSheet.default_style()
        
        interval_cell_styles: List[DraftListCellStyleSheet] = []
        retrieved_interval_cell_styles = json.get(cls.Keys.INTERVAL_CELL_STYLES, [])
        for c in retrieved_interval_cell_styles:
            interval_cell_styles.append(DraftListCellStyleSheet.from_json(c))
        
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
            interval_cell_styles=interval_cell_styles,
            is_list_aggregated=json.get(cls.Keys.IS_LIST_AGGREGATED, default.is_list_aggregated),
            container_background_image_path=json.get(cls.Keys.CONTAINER_BACKGROUND_IMAGE_PATH, default.container_background_image_path),
            cell_font_path=json.get(cls.Keys.CELL_FONT_PATH, default.cell_font_path),
            cell_header_padding_left=json.get(cls.Keys.CELL_HEADER_PADDING_LEFT, default.cell_header_padding_left),
            cell_header_padding_top=json.get(cls.Keys.CELL_HEADER_PADDING_TOP, default.cell_header_padding_top),
            cell_header_padding_right=json.get(cls.Keys.CELL_HEADER_PADDING_RIGHT, default.cell_header_padding_right),
            cell_header_padding_bottom=json.get(cls.Keys.CELL_HEADER_PADDING_BOTTOM, default.cell_header_padding_bottom),
            cell_header_background_color=json.get(cls.Keys.CELL_HEADER_BACKGROUND_COLOR, default.cell_header_background_color),
            cell_header_font_color=json.get(cls.Keys.CELL_HEADER_FONT_COLOR, default.cell_header_font_color),
            cell_header_font_size=json.get(cls.Keys.CELL_HEADER_FONT_SIZE, default.cell_header_font_size),
            cell_header_font_path=json.get(cls.Keys.CELL_HEADER_FONT_PATH, default.cell_header_font_path),
            cell_header_spacing=json.get(cls.Keys.CELL_HEADER_SPACING, default.cell_header_spacing)
        )
        
    @classmethod
    def default_style(cls):
        """Create a style sheet instance with default values"""
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
            interval_cell_styles=[],
            is_list_aggregated=False,
            container_background_image_path=None,
            cell_font_path=None,
            cell_header_padding_left=5,
            cell_header_padding_top=5,
            cell_header_padding_right=5,
            cell_header_padding_bottom=5,
            cell_header_background_color='black',
            cell_header_font_color='white',
            cell_header_font_size=12,
            cell_header_font_path=None,
            cell_header_spacing=5,
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
        
    def set_container_background_image_path(self, value: Optional[str]) -> None:
        self.container_background_image_path = value
    
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
    
    def set_cell_aspect_image_size(self, value: int) -> None:
        self.cell_aspect_image_size = value
    
    def set_is_list_aggregated(self, value: bool) -> None:
        """Set whether the list should be displayed in aggregated form"""
        self.is_list_aggregated = value
    
    def get_modulo_interval_cell_style(self, index: int) -> Optional[DraftListCellStyleSheet]:
        the_index = index % (len(self.interval_cell_styles) + 1)
        return self.get_interval_cell_style(the_index)
    
    def get_interval_cell_style(self, index: int) -> Optional[DraftListCellStyleSheet]:
        if index >= 0 and index < self.cell_interval_count:
            if index == 0:
                return DraftListCellStyleSheet(self.cell_font_color, self.cell_background_color)
            else:
                return self.interval_cell_styles[index - 1]
        return None
    
    def remove_all_interval_cell_styles(self):
        self.interval_cell_styles = []
    
    def add_interval_cell_style(self):
        self.interval_cell_styles.append(DraftListCellStyleSheet.default_style())

    def remove_interval_cell_style(self):
        self.interval_cell_styles.pop()
        
    def set_interval_cell_font_color(self, index: int, value: str):
        if index >= 0 and index < self.cell_interval_count:
            if index == 0:
                self.set_cell_font_color(value)
            else:
                self.interval_cell_styles[index - 1].cell_font_color = value
            
    def set_interval_cell_background_color(self, index: int, value: str):
        if index >= 0 and index < self.cell_interval_count:
            if index == 0:
                self.set_cell_background_color(value)
            else:
                self.interval_cell_styles[index - 1].cell_background_color = value
            
    @property
    def cell_interval_count(self) -> int:
        return len(self.interval_cell_styles) + 1
    
    def set_cell_header_padding_left(self, value: int) -> None:
        """Set the left padding for header cells"""
        self.cell_header_padding_left = value

    def set_cell_header_padding_top(self, value: int) -> None:
        """Set the top padding for header cells"""
        self.cell_header_padding_top = value

    def set_cell_header_padding_right(self, value: int) -> None:
        """Set the right padding for header cells"""
        self.cell_header_padding_right = value

    def set_cell_header_padding_bottom(self, value: int) -> None:
        """Set the bottom padding for header cells"""
        self.cell_header_padding_bottom = value

    def set_cell_header_background_color(self, value: str) -> None:
        """Set the background color for header cells"""
        self.cell_header_background_color = value

    def set_cell_header_font_color(self, value: str) -> None:
        """Set the font color for header cells"""
        self.cell_header_font_color = value

    def set_cell_header_font_size(self, value: int) -> None:
        """Set the font size for header cells"""
        self.cell_header_font_size = value

    def set_cell_header_font_path(self, value: Optional[str]) -> None:
        """Set the font path for header cells"""
        self.cell_header_font_path = value
        
    def set_cell_header_spacing(self, value: int) -> None:
        """Set the font path for header cells"""
        self.cell_header_spacing = value