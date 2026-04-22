
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QSizePolicy

from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsProtocol,
)
from AppCore.DataSource.PlayerStandings.Events import PlayerStandingsDidUpdate
from AppCore.Models import PlayerStanding
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol
from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppCore.Utilities import FontUtilities
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration.AppUIConfiguration import AppUIConfigurationManager
from AppUI.Models import PlayerStandingsListStyleSheet
from R4UI import (
    GridLayout,
    Label,
    RVerticallyExpandingSpacer,
    RWidget,
    ScrollArea,
    VerticalBoxLayout,
)


class PlayerStandingsViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_player_standings_provider = app_dependencies_provider.data_source_player_standings_provider

        app_dependencies_provider.observation_tower.subscribe_multi(
            self, [PlayerStandingsDidUpdate, ConfigurationUpdatedEvent])

        self._setup_view()

    @property
    def _data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        return self._data_source_player_standings_provider.data_source_player_standing

    @property
    def _stylesheet(self) -> PlayerStandingsListStyleSheet:
        return self._app_ui_configuration_manager.configuration.player_standings_list_styles
    
    @property
    def _app_ui_configuration_manager(self) -> AppUIConfigurationManager:
        return self._app_dependencies_provider.app_ui_configuration_manager

    def _setup_view(self):
        self._cells_container = GridLayout().set_uniform_content_margins(0)
        self._cells_container.set_column_stretch(
            1, 1)  # Column 1 is prioritized

        self._window_header_label = Label()
        self._window_header_container = VerticalBoxLayout([
            self._window_header_label
        ]).set_alignment_center_h()

        self._cells_container_container = VerticalBoxLayout([
            self._window_header_container,
            self._cells_container
        ]).set_uniform_content_margins(0).add_spacer(RVerticallyExpandingSpacer())

        self._scroll_view = ScrollArea(self._cells_container_container).set_vertical_scroll_bar_policy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_view.setFrameShape(QFrame.Shape.NoFrame)

        VerticalBoxLayout([
            self._scroll_view,
        ]).set_layout_to_widget(self).set_uniform_content_margins(0)

        self._sync_ui()

    def _sync_ui(self):
        self._cells_container.clear_widgets()

        self._window_header_label.set_text(self._app_ui_configuration_manager.configuration.player_standings_header_text)

        for i, s in enumerate(self._data_source_player_standing.standings):
            standing: PlayerStanding = self._data_source_player_standing.standings[i]

            name_label = Label(standing.display_details)
            # name_label.setScaledContents(True)
            name_label.setSizePolicy(
                QSizePolicy.Ignored, QSizePolicy.Preferred)

            # Or set a tiny minimum width so it doesn't block the window from shrinking
            name_label.setMinimumWidth(1)

            match_label = Label(
                f'{standing.match_wins}-{standing.match_loses}')
            game_label = Label(f'{standing.game_wins}-{standing.game_loses}')

            FontUtilities.apply_font_style(name_label,
                                           self._stylesheet.cell_font_path,
                                           self._stylesheet.cell_font_size,
                                           self._stylesheet.cell_font_color)

            FontUtilities.apply_font_style(match_label,
                                           self._stylesheet.cell_font_path,
                                           self._stylesheet.cell_font_size,
                                           self._stylesheet.cell_font_color)

            FontUtilities.apply_font_style(game_label,
                                           self._stylesheet.cell_font_path,
                                           self._stylesheet.cell_font_size,
                                           self._stylesheet.cell_font_color)

            rank_label = Label(f'{standing.rank}')
            FontUtilities.apply_font_style(rank_label,
                                           self._stylesheet.rank_cell_font_path,
                                           self._stylesheet.rank_cell_font_size,
                                           self._stylesheet.rank_cell_font_color)

            self._cells_container.add_widgets([
                (rank_label, (i, 0)),
                (name_label, (i, 1)),
                # (match_label, (i, 2)),
                # (game_label, (i, 3)),
            ])

        self._cells_container.set_content_margins(self._stylesheet.container_padding_left,
                                                  self._stylesheet.container_padding_top,
                                                  self._stylesheet.container_padding_right,
                                                  self._stylesheet.container_padding_bottom)

        self._cells_container.set_vertical_spacing(
            self._stylesheet.cell_spacing)
        self._cells_container.set_horizontal_spacing(
            self._stylesheet.cell_content_spacing)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(
            self._stylesheet.container_background_color))  # Set background color
        self.setAutoFillBackground(True)  # Enable background filling
        self.setPalette(palette)

        # Window header
        self._window_header_container.set_content_margins(self._stylesheet.window_header_padding_left,
                                                          self._stylesheet.window_header_padding_top,
                                                          self._stylesheet.window_header_padding_right,
                                                          self._stylesheet.window_header_padding_bottom)

        palette = self._window_header_container.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(
            self._stylesheet.window_header_background_color))

        self._window_header_container.setAutoFillBackground(True)
        self._window_header_container.setPalette(palette)

        # Label
        FontUtilities.apply_font_style(self._window_header_label,
                                       self._stylesheet.window_header_font_path,
                                       self._stylesheet.window_header_font_size,
                                       self._stylesheet.window_header_font_color)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is PlayerStandingsDidUpdate or type(event) is ConfigurationUpdatedEvent:
            self._sync_ui()
