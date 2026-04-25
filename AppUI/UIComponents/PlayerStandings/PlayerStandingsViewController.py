from typing import List

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QFrame

from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import \
    DataSourcePlayerStandingsProtocol
from AppCore.DataSource.PlayerStandings.Events import PlayerStandingsDidUpdate
from AppCore.Models import PlayerStanding
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from AppUI.Models import PlayerStandingsListStyleSheet
from R4UI import (HorizontalBoxLayout, Label, RHorizontalExpandingSpacerWidget,
                  RVerticallyExpandingSpacer, RWidget, ScrollArea,
                  VerticalBoxLayout)


class PlayerStandingsListLineItemViewController(RWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 index: int):
        super().__init__()
        self._index = index
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_player_standings_provider = app_dependencies_provider.data_source_player_standings_provider

        self._setup_view()

    @property
    def _data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        return self._data_source_player_standings_provider.data_source_player_standing

    @property
    def _stylesheet(self) -> PlayerStandingsListStyleSheet:
        return self._app_dependencies_provider.app_ui_configuration_manager.configuration.player_standings_list_styles

    def _setup_view(self):
        standing: PlayerStanding = self._data_source_player_standing.standings[self._index]

        # Cell
        horizontal_layout = HorizontalBoxLayout([]).set_layout_to_widget(self)
        horizontal_layout.set_spacing(self._stylesheet.cell_content_spacing)
        horizontal_layout.set_content_margins(self._stylesheet.cell_padding_left,
                                              self._stylesheet.cell_padding_top,
                                              self._stylesheet.cell_padding_right,
                                              self._stylesheet.cell_padding_bottom)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(
            self._stylesheet.cell_background_color))

        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Rank Label
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText,
                         QColor(self._stylesheet.cell_font_color))
        rank_label = Label(f'{standing.rank}')
        # rank_label.setSizePolicy(QSizePolicy.Policy.Ignored,
        #                     QSizePolicy.Policy.Minimum)
        rank_label.setPalette(palette)
        # horizontal_layout.add_widget(rank_label)

        # Label
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText,
                         QColor(self._stylesheet.cell_font_color))
        label = Label(f'{standing.display_details}')
        # label.setSizePolicy(QSizePolicy.Policy.Ignored,
        #                     QSizePolicy.Policy.Preferred)
        label.setPalette(palette)
        # horizontal_layout.add_widget(label, 1)

        

        horizontal_layout.add_widgets([
            rank_label,
            label,
            RHorizontalExpandingSpacerWidget()
        ])

        custom_font_path = self._stylesheet.cell_font_path
        if custom_font_path is not None:
            font_id = QFontDatabase.addApplicationFont(custom_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font = QFont(
                font_families[0], self._stylesheet.cell_font_size)
            label.setFont(custom_font)
            rank_label.setFont(custom_font)
        else:
            current_font = label.font()
            current_font.setPointSize(self._stylesheet.cell_font_size)
            label.setFont(current_font)
            rank_label.setFont(current_font)


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
        return self._app_dependencies_provider.app_ui_configuration_manager.configuration.player_standings_list_styles

    def _setup_view(self):
        self._cells_container = VerticalBoxLayout().set_uniform_content_margins(0)

        self._cells_container_container = VerticalBoxLayout([
            self._cells_container
        ]).set_uniform_content_margins(0).add_spacer(RVerticallyExpandingSpacer())

        self._scroll_view = ScrollArea(self._cells_container_container)
        self._scroll_view.setFrameShape(QFrame.Shape.NoFrame)

        VerticalBoxLayout([
            self._scroll_view,
        ]).set_layout_to_widget(self).set_uniform_content_margins(0)

        self._sync_ui()

    def _sync_ui(self):
        cells: List[PlayerStandingsListLineItemViewController] = []
        for i, s in enumerate(self._data_source_player_standing.standings):
            cells.append(PlayerStandingsListLineItemViewController(
                self._app_dependencies_provider, i))
        self._cells_container.replace_all_widgets(cells)

        self._cells_container.set_content_margins(self._stylesheet.container_padding_left,
                                                  self._stylesheet.container_padding_top,
                                                  self._stylesheet.container_padding_right,
                                                  self._stylesheet.container_padding_bottom)

        self._cells_container.set_spacing(self._stylesheet.cell_spacing)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(
            self._stylesheet.container_background_color))  # Set background color
        self.setAutoFillBackground(True)  # Enable background filling
        self.setPalette(palette)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is PlayerStandingsDidUpdate or type(event) is ConfigurationUpdatedEvent:
            self._sync_ui()
