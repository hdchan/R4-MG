from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QLabel

from AppCore.Config import Configuration
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration import MutableAppUIConfiguration
from .SettingsContainerChildProtocol import SettingsContainerChildProtocol
from R4UI import (BoldLabel, ComboBox, GridLayout, HeaderLabel,
                    HorizontalBoxLayout, HorizontalLabeledInputRow,
                    LineEditInt, LineEditText, PushButton, ScrollArea,
                    VerticalBoxLayout, VerticalGroupBox)

from AppUI.Models.DraftListStyleSheet import DraftListStyleSheet


class CellStyleWrapper(VerticalGroupBox):
    def __init__(self, index: int, 
                 stylesheet: DraftListStyleSheet, 
                 trash_fn: Callable[[int], None]):
        super().__init__()
        self._index = index
        self._stylesheet = stylesheet
        self._trash_fn = trash_fn
        cell_style = self._stylesheet.get_interval_cell_style(self._index)
        
        
        trash_button = PushButton("Remove", self._trash)
        trash_button.setEnabled(self._index == self._stylesheet.cell_interval_count - 1)
        trash_button.setVisible(index > 0)
        
        if cell_style is not None:
            self.add_widgets([
                HorizontalBoxLayout([
                    BoldLabel(f'Cell item - {self._index + 1}'),
                    trash_button
                    ]),
                
                HorizontalLabeledInputRow(
                    "Background color",
                    LineEditText(
                        cell_style.cell_background_color, 
                        lambda x: self._stylesheet.set_interval_cell_background_color(index, x)
                        )
                    ),
                
                HorizontalLabeledInputRow(
                    "Font color",
                    LineEditText(
                        cell_style.cell_font_color, 
                        lambda x: self._stylesheet.set_interval_cell_font_color(index, x)
                        )
                    ),
                ])
            
    def _trash(self):
        self._trash_fn(self._index)



class DraftListSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._router = app_dependencies_provider.router
        self._mutable_app_ui_configuration = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        self._stylesheet = self._mutable_app_ui_configuration.draft_list_styles
        
        self._setup_view()
    
    
    def _setup_view(self):
        
        self._cell_configuration_list = VerticalGroupBox()
        self._container_background_image_label = QLabel()
        self._cell_font_label = QLabel()
        self._cell_header_font_label = QLabel()
        self._add_card_mode_combo_box = ComboBox([
                            "Off",
                            "Stage",
                            "Stage & Publish"
                        ])
        self._add_card_mode_combo_box.setCurrentIndex(self._mutable_app_ui_configuration.core_configuration.draft_list_add_card_mode)
        
        self._container_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_left)
        self._container_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_top)
        self._container_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_right)
        self._container_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_bottom)
        
        self._cell_header_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_padding_left)
        self._cell_header_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_padding_top)
        self._cell_header_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_padding_right)
        self._cell_header_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_padding_bottom)
        
        self._cell_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_left)
        self._cell_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_top)
        self._cell_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_right)
        self._cell_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_bottom)

        # Container styling
        self._container_background_color = LineEditText(triggered_fn=self._stylesheet.set_container_background_color)

        # Cell header styling
        self._cell_header_background_color = LineEditText(triggered_fn=self._stylesheet.set_cell_header_background_color)
        self._cell_header_spacing = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_spacing)
        self._cell_header_font_size = LineEditInt(triggered_fn=self._stylesheet.set_cell_header_font_size)
        self._cell_header_font_color = LineEditText(triggered_fn=self._stylesheet.set_cell_header_font_color)

        # Cell styling
        self._cell_spacing = LineEditInt(triggered_fn=self._stylesheet.set_cell_spacing)
        self._cell_content_spacing = LineEditInt(triggered_fn=self._stylesheet.set_cell_content_spacing)
        self._cell_font_size = LineEditInt(triggered_fn=self._stylesheet.set_cell_font_size)
        self._cell_aspect_image_size = LineEditInt(triggered_fn=self._stylesheet.set_cell_aspect_image_size)

        # Cell background styling
        self._cell_background_color = LineEditText(triggered_fn=self._stylesheet.set_cell_background_color)
        self._cell_font_color = LineEditText(triggered_fn=self._stylesheet.set_cell_font_color)
        
        self._cell_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_left)
        self._cell_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_top)
        self._cell_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_right)
        self._cell_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_bottom)

        VerticalBoxLayout([
            ScrollArea(
                VerticalBoxLayout([
                    VerticalGroupBox([
                        HeaderLabel("Add card mode"),
                        self._add_card_mode_combo_box
                    ]),
                    VerticalGroupBox([
                        HeaderLabel("Container"),
                        VerticalGroupBox([
                            BoldLabel("Padding"),
                            GridLayout([
                                (HorizontalLabeledInputRow("Left", self._container_padding_left), (1, 0)),
                                (HorizontalLabeledInputRow("Top", self._container_padding_top), (0, 1)),
                                (HorizontalLabeledInputRow("Right", self._container_padding_right), (1, 2)),
                                (HorizontalLabeledInputRow("Bottom", self._container_padding_bottom), (2, 1))
                                ]),
                            ]),
                        
                            HorizontalLabeledInputRow(
                                "Background Color",
                                self._container_background_color
                                ),
                            
                        ]),
                    
                    VerticalGroupBox([
                        HeaderLabel("Cell Header"),
                        
                        VerticalGroupBox([
                            BoldLabel("Padding"),
                            GridLayout([
                                (HorizontalLabeledInputRow("Left", self._cell_header_padding_left), (1, 0)),
                                (HorizontalLabeledInputRow("Top", self._cell_header_padding_top), (0, 1)),
                                (HorizontalLabeledInputRow("Right", self._cell_header_padding_right), (1, 2)),
                                (HorizontalLabeledInputRow("Bottom", self._cell_header_padding_bottom), (2, 1))
                                ]),
                            ]),
                        
                            HorizontalLabeledInputRow(
                                    "Background color",
                                    self._cell_header_background_color
                                    ),
                        
                            HorizontalLabeledInputRow(
                                "Spacing",
                                self._cell_header_spacing
                                ),
                            
                        VerticalGroupBox([
                            BoldLabel("Text"),
                            HorizontalLabeledInputRow("Font size", self._cell_header_font_size),
                            HorizontalLabeledInputRow("Font color", self._cell_header_font_color
                                ),
                            VerticalGroupBox([
                        
                                VerticalBoxLayout([
                                    self._cell_header_font_label,
                                    PushButton("Set cell header font ", self._edit_cell_header_font),
                                    PushButton("Remove cell header font",self._remove_cell_header_font)
                                    ]),
                                ])
                            ])
                        ]),
                    
                    VerticalGroupBox([
                        HeaderLabel("Cells Items - Global"),
                        
                        VerticalGroupBox([
                            BoldLabel("Padding"),
                            GridLayout([
                                (HorizontalLabeledInputRow("Left", self._cell_padding_left), (1, 0)),
                                (HorizontalLabeledInputRow("Top", self._cell_padding_top), (0, 1)),
                                (HorizontalLabeledInputRow("Right", self._cell_padding_right), (1, 2)),
                                (HorizontalLabeledInputRow("Bottom", self._cell_padding_bottom), (2, 1))
                                ]),
                            
                            
                            ]),
                        
                        VerticalGroupBox([
                            HorizontalBoxLayout([
                                HorizontalLabeledInputRow("Spacing", self._cell_spacing),
                                HorizontalLabeledInputRow("Content spacing", self._cell_content_spacing),
                                ]),
                            
                            HorizontalBoxLayout([
                                HorizontalLabeledInputRow("Font size", self._cell_font_size),
                                
                                HorizontalLabeledInputRow("Aspect image size", self._cell_aspect_image_size), 
                                ]),
                            ]),
                        
                            VerticalGroupBox([
                            
                                VerticalBoxLayout([
                                    self._cell_font_label,
                                    PushButton("Set cell font ", self._edit_cell_font),
                                    PushButton("Remove cell font", self._remove_cell_font)
                                    ]),
                                ])
                        
                    ]),
                    self._cell_configuration_list,
                    PushButton("Add Cell Interval", self._add_new_cell_configuration)
                ])),
                
                HorizontalBoxLayout([
                    PushButton(
                        "Reset", 
                        self._reset_styles
                        ),
                ])
            
            ]).set_layout_to_widget(self)
        
        self._sync_ui()
    
    def _load_cell_interval_configuration(self):
        self._cell_configuration_list.replace_all_widgets([HeaderLabel("Cell Items - Intervals")])
        for current_index in range(self._stylesheet.cell_interval_count):
            self._cell_configuration_list.add_widgets([
                CellStyleWrapper(current_index,
                                 self._stylesheet, 
                                 self._trash)
                ])
    
    def _add_new_cell_configuration(self):
        self._stylesheet.add_interval_cell_style()
        self._sync_ui()
    
    def _reset_styles_checked(self, state: Qt.CheckState):
        pass
    
    def _trash(self, index: int):
        self._stylesheet.remove_interval_cell_style()
        self._sync_ui()
    
    def _sync_ui(self):
        # Container padding
        self._container_padding_left.set_value(self._stylesheet.container_padding_left)
        self._container_padding_top.set_value(self._stylesheet.container_padding_top)
        self._container_padding_right.set_value(self._stylesheet.container_padding_right)
        self._container_padding_bottom.set_value(self._stylesheet.container_padding_bottom)
        
        # Container styling
        self._container_background_color.set_value(self._stylesheet.container_background_color)
        
        # Header cell padding
        self._cell_header_padding_left.set_value(self._stylesheet.cell_header_padding_left)
        self._cell_header_padding_top.set_value(self._stylesheet.cell_header_padding_top)
        self._cell_header_padding_right.set_value(self._stylesheet.cell_header_padding_right)
        self._cell_header_padding_bottom.set_value(self._stylesheet.cell_header_padding_bottom)
        
        # Header cell styling
        self._cell_header_background_color.set_value(self._stylesheet.cell_header_background_color)
        self._cell_header_spacing.set_value(self._stylesheet.cell_header_spacing)
        self._cell_header_font_size.set_value(self._stylesheet.cell_header_font_size)
        self._cell_header_font_color.set_value(self._stylesheet.cell_header_font_color)
        
        # Cell padding
        self._cell_padding_left.set_value(self._stylesheet.cell_padding_left)
        self._cell_padding_top.set_value(self._stylesheet.cell_padding_top)
        self._cell_padding_right.set_value(self._stylesheet.cell_padding_right)
        self._cell_padding_bottom.set_value(self._stylesheet.cell_padding_bottom)
        
        # Cell styling
        self._cell_spacing.set_value(self._stylesheet.cell_spacing)
        self._cell_content_spacing.set_value(self._stylesheet.cell_content_spacing)
        self._cell_font_size.set_value(self._stylesheet.cell_font_size)
        self._cell_aspect_image_size.set_value(self._stylesheet.cell_aspect_image_size)
        self._cell_background_color.set_value(self._stylesheet.cell_background_color)
        self._cell_font_color.set_value(self._stylesheet.cell_font_color)

        # Labels
        self._container_background_image_label.setText(self._stylesheet.container_background_image_path if self._stylesheet.container_background_image_path is not None else "No image selected")
        self._cell_font_label.setText(self._stylesheet.cell_font_path if self._stylesheet.cell_font_path is not None else "No font selected")
        self._cell_header_font_label.setText(self._stylesheet.cell_header_font_path if self._stylesheet.cell_header_font_path is not None else "No font selected")
        
        # Cell interval configuration
        self._load_cell_interval_configuration()
    
    def _edit_background_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                     "Select image", 
                                                     None, 
                                                     "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if file_path:
            self._stylesheet.set_container_background_image_path(file_path)
            self._sync_ui()
            
    def _remove_background_image(self):
        self._stylesheet.set_container_background_image_path(None)
        self._sync_ui()
        
    def _edit_cell_font(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                     "Select font", 
                                                     None, 
                                                     "Font files (*.ttf *.otf *.woff *.woff2);;All Files (*)")
        if file_path:
            self._stylesheet.set_cell_font_path(file_path)
            self._sync_ui()
            
    def _remove_cell_font(self):
        self._stylesheet.set_cell_font_path(None)
        self._sync_ui()
        
    def _edit_cell_header_font(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                     "Select font", 
                                                     None, 
                                                     "Font files (*.ttf *.otf *.woff *.woff2);;All Files (*)")
        if file_path:
            self._stylesheet.set_cell_header_font_path(file_path)
            self._sync_ui()
            
    def _remove_cell_header_font(self):
        self._stylesheet.set_cell_header_font_path(None)
        self._sync_ui()
        
    
    def _reset_styles(self):
        if self._router.prompt_accept("Reset styles?", "Are you sure you want to reset styles?"):
            self._stylesheet = DraftListStyleSheet.default_style()
            self._sync_ui()
        
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        new_draft_list_styles = mutable_app_ui_configuration.draft_list_styles
        
        # Container padding
        new_draft_list_styles.set_container_padding_left(self._stylesheet.container_padding_left)
        new_draft_list_styles.set_container_padding_top(self._stylesheet.container_padding_top)
        new_draft_list_styles.set_container_padding_right(self._stylesheet.container_padding_right)
        new_draft_list_styles.set_container_padding_bottom(self._stylesheet.container_padding_bottom)
        
        # Container styling
        new_draft_list_styles.set_container_background_color(self._stylesheet.container_background_color)
        new_draft_list_styles.set_container_background_image_path(self._stylesheet.container_background_image_path)
        
        # Header cell padding
        new_draft_list_styles.set_cell_header_padding_left(self._stylesheet.cell_header_padding_left)
        new_draft_list_styles.set_cell_header_padding_top(self._stylesheet.cell_header_padding_top)
        new_draft_list_styles.set_cell_header_padding_right(self._stylesheet.cell_header_padding_right)
        new_draft_list_styles.set_cell_header_padding_bottom(self._stylesheet.cell_header_padding_bottom)
        
        # Header cell styling
        new_draft_list_styles.set_cell_header_background_color(self._stylesheet.cell_header_background_color)
        new_draft_list_styles.set_cell_header_spacing(self._stylesheet.cell_header_spacing)
        new_draft_list_styles.set_cell_header_font_size(self._stylesheet.cell_header_font_size)
        new_draft_list_styles.set_cell_header_font_color(self._stylesheet.cell_header_font_color)
        new_draft_list_styles.set_cell_header_font_path(self._stylesheet.cell_header_font_path)
        
        # Cell padding
        new_draft_list_styles.set_cell_padding_left(self._stylesheet.cell_padding_left)
        new_draft_list_styles.set_cell_padding_top(self._stylesheet.cell_padding_top)
        new_draft_list_styles.set_cell_padding_right(self._stylesheet.cell_padding_right)
        new_draft_list_styles.set_cell_padding_bottom(self._stylesheet.cell_padding_bottom)
        
        # Cell styling
        new_draft_list_styles.set_cell_spacing(self._stylesheet.cell_spacing)
        new_draft_list_styles.set_cell_content_spacing(self._stylesheet.cell_content_spacing)
        new_draft_list_styles.set_cell_font_size(self._stylesheet.cell_font_size)
        new_draft_list_styles.set_cell_aspect_image_size(self._stylesheet.cell_aspect_image_size)
        new_draft_list_styles.set_cell_background_color(self._stylesheet.cell_background_color)
        new_draft_list_styles.set_cell_font_color(self._stylesheet.cell_font_color)
        new_draft_list_styles.set_cell_font_path(self._stylesheet.cell_font_path)
        
        # Apply interval cell styles
        new_draft_list_styles.remove_all_interval_cell_styles()
        for i in range(self._stylesheet.cell_interval_count):
            if style := self._stylesheet.get_interval_cell_style(i):
                if i > 0: # TODO: rework interval styling calls and the rest of this page
                    new_draft_list_styles.add_interval_cell_style()
                new_draft_list_styles.set_interval_cell_background_color(i, style.cell_background_color)
                new_draft_list_styles.set_interval_cell_font_color(i, style.cell_font_color)
        
        mutable_app_ui_configuration.set_draft_list_styles(new_draft_list_styles)
        mutable_app_ui_configuration.core_mutable_configuration.set_draft_list_add_card_mode(
            Configuration.Settings.DraftListAddCardMode(self._add_card_mode_combo_box.currentIndex())
        )
        
        return mutable_app_ui_configuration