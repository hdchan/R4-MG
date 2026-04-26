

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.Configuration import MutableAppUIConfiguration
from AppUI.Models.PlayerStandingsListStyleSheet import \
    PlayerStandingsListStyleSheet
from R4UI import (GridLayout, HorizontalBoxLayout, HorizontalLabeledInputRow,
                  Label, LineEditInt, LineEditText, PushButton, RBoldLabel,
                  RHeaderLabel, ScrollArea, VerticalBoxLayout,
                  VerticalGroupBox)

from .SettingsContainerChildProtocol import SettingsContainerChildProtocol


class PlayerStandingsListSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._router = app_dependencies_provider.router
        self._mutable_app_ui_configuration = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        self._stylesheet = self._mutable_app_ui_configuration.player_standings_list_styles

        self._setup_view()

    def _setup_view(self):
        # Window Header
        self._window_header_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_window_header_padding_left)
        self._window_header_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_window_header_padding_top)
        self._window_header_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_window_header_padding_right)
        self._window_header_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_window_header_padding_bottom)
        self._window_header_background_color = LineEditText(triggered_fn=self._stylesheet.set_window_header_background_color)
        self._window_header_font_color = LineEditText(triggered_fn=self._stylesheet.set_window_header_font_color)
        self._window_header_font_size = LineEditInt(triggered_fn=self._stylesheet.set_window_header_font_size)
        self._window_header_font_label = Label()

        self._container_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_left)
        self._container_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_top)
        self._container_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_right)
        self._container_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_container_padding_bottom)

        # Container styling
        self._container_background_color = LineEditText(triggered_fn=self._stylesheet.set_container_background_color)

        # Cell styling
        self._cell_spacing = LineEditInt(triggered_fn=self._stylesheet.set_cell_spacing)
        self._cell_content_spacing = LineEditInt(triggered_fn=self._stylesheet.set_cell_content_spacing)
        

        self._cell_background_color = LineEditText(triggered_fn=self._stylesheet.set_cell_background_color)

        self._cell_font_size = LineEditInt(triggered_fn=self._stylesheet.set_cell_font_size)
        self._cell_font_color = LineEditText(triggered_fn=self._stylesheet.set_cell_font_color)
        self._cell_font_label = Label()

        self._rank_cell_font_size = LineEditInt(triggered_fn=self._stylesheet.set_rank_cell_font_size)
        self._rank_cell_font_color = LineEditText(triggered_fn=self._stylesheet.set_rank_cell_font_color)
        self._rank_cell_font_label = Label()

        self._cell_padding_left = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_left)
        self._cell_padding_top = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_top)
        self._cell_padding_right = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_right)
        self._cell_padding_bottom = LineEditInt(triggered_fn=self._stylesheet.set_cell_padding_bottom)

        VerticalBoxLayout([
            ScrollArea(
                VerticalBoxLayout([
                    VerticalGroupBox([
                        RHeaderLabel("Window Header"),
                        VerticalGroupBox([
                            RBoldLabel("Padding"),
                            GridLayout([
                                (HorizontalLabeledInputRow("Left", self._window_header_padding_left), (1, 0)),
                                (HorizontalLabeledInputRow("Top", self._window_header_padding_top), (0, 1)),
                                (HorizontalLabeledInputRow("Right", self._window_header_padding_right), (1, 2)),
                                (HorizontalLabeledInputRow("Bottom", self._window_header_padding_bottom), (2, 1))
                            ]),
                        ]),

                        HorizontalLabeledInputRow("Background Color", self._window_header_background_color),

                        VerticalGroupBox([
                            HorizontalBoxLayout([
                                HorizontalLabeledInputRow("Font size", self._window_header_font_size),
                                HorizontalLabeledInputRow("Font color", self._window_header_font_color),
                            ]),
                            VerticalBoxLayout([
                                self._window_header_font_label,
                                PushButton("Set font ",self._edit_window_header_font),
                                PushButton("Remove font",self._remove_window_header_font)
                            ]),
                        ])
                    ]),
                    VerticalGroupBox([
                        RHeaderLabel("Cell Container"),
                        VerticalGroupBox([
                            RBoldLabel("Padding"),
                            GridLayout([
                                (HorizontalLabeledInputRow("Left", self._container_padding_left), (1, 0)),
                                (HorizontalLabeledInputRow("Top", self._container_padding_top), (0, 1)),
                                (HorizontalLabeledInputRow("Right", self._container_padding_right), (1, 2)),
                                (HorizontalLabeledInputRow("Bottom", self._container_padding_bottom), (2, 1))
                            ]),
                        ]),

                        HorizontalLabeledInputRow("Background Color", self._container_background_color),

                    ]),

                    VerticalGroupBox([
                        RHeaderLabel("Cells Items - Global"),

                        VerticalGroupBox([
                            RBoldLabel("Padding"),
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

                            

                            HorizontalLabeledInputRow("Background color", self._cell_background_color),
                        ]),

                        VerticalGroupBox([
                            HorizontalBoxLayout([
                                HorizontalLabeledInputRow("Font size", self._cell_font_size),
                                HorizontalLabeledInputRow("Font color", self._cell_font_color),
                            ]),
                            VerticalBoxLayout([
                                self._cell_font_label,
                                PushButton("Set font ",self._edit_cell_font),
                                PushButton("Remove font",self._remove_cell_font)
                            ]),
                        ])

                    ]),

                    VerticalGroupBox([
                        RHeaderLabel("Rank Column"),

                        VerticalGroupBox([
                            HorizontalBoxLayout([
                                HorizontalLabeledInputRow("Font size", self._rank_cell_font_size),
                                HorizontalLabeledInputRow("Font color", self._rank_cell_font_color),
                            ]),
                            VerticalBoxLayout([
                                self._rank_cell_font_label,
                                PushButton("Set font ",self._edit_rank_cell_font),
                                PushButton("Remove font",self._remove_rank_cell_font)
                            ]),
                        ])
                    ])
                ])
            ),

            HorizontalBoxLayout([
                PushButton("Reset",self._reset_styles),
            ])
        ]).set_layout_to_widget(self)

        self._sync_ui()

    def _sync_ui(self):
        # Container padding
        self._container_padding_left.set_value(self._stylesheet.container_padding_left)
        self._container_padding_top.set_value(self._stylesheet.container_padding_top)
        self._container_padding_right.set_value(self._stylesheet.container_padding_right)
        self._container_padding_bottom.set_value(self._stylesheet.container_padding_bottom)

        # Container styling
        self._container_background_color.set_value(self._stylesheet.container_background_color)


        # Window header
        self._window_header_padding_left.set_value(self._stylesheet.window_header_padding_left)
        self._window_header_padding_top.set_value(self._stylesheet.window_header_padding_top)
        self._window_header_padding_right.set_value(self._stylesheet.window_header_padding_right)
        self._window_header_padding_bottom.set_value(self._stylesheet.window_header_padding_bottom)
        self._window_header_background_color.set_value(self._stylesheet.window_header_background_color)
        self._window_header_font_color.set_value(self._stylesheet.window_header_font_color)
        self._window_header_font_size.set_value(self._stylesheet.window_header_font_size)
        self._window_header_font_label.setText(self._stylesheet.window_header_font_path if self._stylesheet.window_header_font_path is not None else "No font selected")

        # Cell padding
        self._cell_padding_left.set_value(self._stylesheet.cell_padding_left)
        self._cell_padding_top.set_value(self._stylesheet.cell_padding_top)
        self._cell_padding_right.set_value(self._stylesheet.cell_padding_right)
        self._cell_padding_bottom.set_value(self._stylesheet.cell_padding_bottom)

        # Cell styling
        self._cell_spacing.set_value(self._stylesheet.cell_spacing)
        self._cell_content_spacing.set_value(self._stylesheet.cell_content_spacing)
        self._cell_background_color.set_value(self._stylesheet.cell_background_color)

        self._cell_font_size.set_value(self._stylesheet.cell_font_size)
        self._cell_font_color.set_value(self._stylesheet.cell_font_color)
        self._cell_font_label.setText(self._stylesheet.cell_font_path if self._stylesheet.cell_font_path is not None else "No font selected")

        self._rank_cell_font_size.set_value(self._stylesheet.rank_cell_font_size)
        self._rank_cell_font_color.set_value(self._stylesheet.rank_cell_font_color)
        self._rank_cell_font_label.setText(self._stylesheet.rank_cell_font_path if self._stylesheet.rank_cell_font_path is not None else "No font selected")

    def _edit_window_header_font(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select font",
                                                   None,
                                                   "Font files (*.ttf *.otf *.woff *.woff2);;All Files (*)")
        if file_path:
            self._stylesheet.set_window_header_font_path(file_path)
            self._sync_ui()

    def _remove_window_header_font(self):
        self._stylesheet.set_window_header_font_path(None)
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

    def _edit_rank_cell_font(self):
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select font",
                                                   None,
                                                   "Font files (*.ttf *.otf *.woff *.woff2);;All Files (*)")
        if file_path:
            self._stylesheet.set_rank_cell_font_path(file_path)
            self._sync_ui()

    def _remove_rank_cell_font(self):
        self._stylesheet.set_rank_cell_font_path(None)
        self._sync_ui()

    def _reset_styles(self):
        if self._router.prompt_accept("Reset styles?", "Are you sure you want to reset styles?"):
            self._stylesheet = PlayerStandingsListStyleSheet.default_style()
            self._sync_ui()

    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        new_player_list_styles = mutable_app_ui_configuration.player_standings_list_styles

        # Window header padding
        new_player_list_styles.set_window_header_padding_left(self._stylesheet.window_header_padding_left)
        new_player_list_styles.set_window_header_padding_top(self._stylesheet.window_header_padding_top)
        new_player_list_styles.set_window_header_padding_right(self._stylesheet.window_header_padding_right)
        new_player_list_styles.set_window_header_padding_bottom(self._stylesheet.window_header_padding_bottom)
        new_player_list_styles.set_window_header_background_color(self._stylesheet.window_header_background_color)
        new_player_list_styles.set_window_header_font_color(self._stylesheet.window_header_font_color)
        new_player_list_styles.set_window_header_font_size(self._stylesheet.window_header_font_size)
        new_player_list_styles.set_window_header_font_path(self._stylesheet.window_header_font_path)

        # Container padding
        new_player_list_styles.set_container_padding_left(self._stylesheet.container_padding_left)
        new_player_list_styles.set_container_padding_top(self._stylesheet.container_padding_top)
        new_player_list_styles.set_container_padding_right(self._stylesheet.container_padding_right)
        new_player_list_styles.set_container_padding_bottom(self._stylesheet.container_padding_bottom)

        # Container styling
        new_player_list_styles.set_container_background_color(self._stylesheet.container_background_color)

        # Cell padding
        new_player_list_styles.set_cell_padding_left(self._stylesheet.cell_padding_left)
        new_player_list_styles.set_cell_padding_top(self._stylesheet.cell_padding_top)
        new_player_list_styles.set_cell_padding_right(self._stylesheet.cell_padding_right)
        new_player_list_styles.set_cell_padding_bottom(self._stylesheet.cell_padding_bottom)

        # Cell styling
        new_player_list_styles.set_cell_spacing(self._stylesheet.cell_spacing)
        new_player_list_styles.set_cell_content_spacing(self._stylesheet.cell_content_spacing)
        new_player_list_styles.set_cell_background_color(self._stylesheet.cell_background_color)

        new_player_list_styles.set_cell_font_size(self._stylesheet.cell_font_size)
        new_player_list_styles.set_cell_font_color(self._stylesheet.cell_font_color)
        new_player_list_styles.set_cell_font_path(self._stylesheet.cell_font_path)

        new_player_list_styles.set_rank_cell_font_size(self._stylesheet.rank_cell_font_size)
        new_player_list_styles.set_rank_cell_font_color(self._stylesheet.rank_cell_font_color)
        new_player_list_styles.set_rank_cell_font_path(self._stylesheet.rank_cell_font_path)

        mutable_app_ui_configuration.set_player_standings_list_styles(new_player_list_styles)

        return mutable_app_ui_configuration
