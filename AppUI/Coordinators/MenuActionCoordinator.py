import webbrowser

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QAction, QMenu, QMenuBar, QWidget

from AppCore.Config import *

from ..Assets import AssetProvider
from ..MainProgramViewController import MainProgramViewController
from ..Window import Window
from .AboutViewController import AboutViewController
from .SettingsViewController import SettingsViewController


class MenuActionCoordinator(QObject):
    def __init__(self,
                 window: Window,
                 main_program: MainProgramViewController,
                 configuration_manager: ConfigurationManager, 
                 asset_provider: AssetProvider):
        super().__init__()
        self.main_program = main_program
        self.configuration_manager = configuration_manager
        self.asset_provider = asset_provider
        self._menu_parent = window
        self.attachMenuBar(window)
        
        self.settings = None
        self.about = None
        
    @property
    def configuration(self) -> Configuration:
        return self.configuration_manager.configuration

    def attachMenuBar(self, parent: QWidget):
        self._menu_parent = parent
        menu_bar = QMenuBar(parent)
        menu_bar.setNativeMenuBar(False)

        # MARK: - File
        file_menu = QMenu("&File", parent)
        menu_bar.addMenu(file_menu)

        new_file_menu = QAction('New image file', parent)
        new_file_menu.triggered.connect(self.new_file_tapped)
        file_menu.addAction(new_file_menu)

        refresh_production_images = QAction('Refresh production images', parent)
        refresh_production_images.triggered.connect(self.did_tap_refresh_production_images)
        file_menu.addAction(refresh_production_images)
        
        
        open_production_dir = QAction('Reveal images in file explorer', parent)
        open_production_dir.triggered.connect(self.did_open_production_dir)
        file_menu.addAction(open_production_dir)
        
        # Actions
        action_menu = QMenu("&Action", parent)
        menu_bar.addMenu(action_menu)

        unstage_all_staging_resources = QAction('Unstage all staging resources', parent)
        unstage_all_staging_resources.triggered.connect(self.did_unstage_all_staging_resources)
        action_menu.addAction(unstage_all_staging_resources)

        clear_cache_dir = QAction('Clear cache', parent)
        clear_cache_dir.triggered.connect(self.did_clear_cache_dir)
        action_menu.addAction(clear_cache_dir)

        
        # MARK: - Settings
        settings_menu = QAction("Settings", parent)
        settings_menu.triggered.connect(self.did_tap_settings)
        file_menu.addAction(settings_menu)
        
        # MARK: - View
        view_menu = QMenu("&View", parent)
        menu_bar.addMenu(view_menu)
        
        show_resource_details = QAction('Show resource details', parent)
        show_resource_details.triggered.connect(self.did_toggle_show_resource_details)
        show_resource_details.setCheckable(True)
        show_resource_details.setChecked(self.configuration.show_resource_details)
        view_menu.addAction(show_resource_details)
        
        
        hide_image_preview = QAction('Hide image preview', parent)
        hide_image_preview.triggered.connect(self.did_toggle_hide_image_preview)
        hide_image_preview.setCheckable(True)
        hide_image_preview.setChecked(self.configuration.hide_image_preview)
        view_menu.addAction(hide_image_preview)


        card_title_detail = QMenu('Card title detail', parent)
        view_menu.addMenu(card_title_detail)

        card_title_detail_short = QAction('Short', parent)
        card_title_detail_short.triggered.connect(self.did_toggle_card_title_detail_short)
        card_title_detail_short.setCheckable(True)
        self.card_title_detail_short = card_title_detail_short
        card_title_detail.addAction(card_title_detail_short)

        card_title_detail_normal = QAction('Normal', parent)
        card_title_detail_normal.triggered.connect(self.did_toggle_card_title_detail_normal)
        card_title_detail_normal.setCheckable(True)
        self.card_title_detail_normal = card_title_detail_normal
        card_title_detail.addAction(card_title_detail_normal)

        card_title_detail_detailed = QAction('Detailed', parent)
        card_title_detail_detailed.triggered.connect(self.did_toggle_card_title_detail_detailed)
        card_title_detail_detailed.setCheckable(True)
        self.card_title_detail_detailed = card_title_detail_detailed
        card_title_detail.addAction(card_title_detail_detailed)

        self._sync_card_title_detail_checkmarks()

        
        # MARK: - About
        about_menu = QMenu("&Help", parent)
        menu_bar.addMenu(about_menu)

        check_update = QAction('Check for updates', parent)
        check_update.triggered.connect(self.open_update_page)
        about_menu.addAction(check_update)

        about = QAction(f"About", parent)
        about.triggered.connect(self.open_about_page)
        about_menu.addAction(about)

        # MARK: - Developer
        if self.configuration.is_developer_mode:
            developer_menu = QMenu("&Developer", parent)
            menu_bar.addMenu(developer_menu)

            open_configuration_dir = QAction('Reveal configuration in file explorer', parent)
            open_configuration_dir.triggered.connect(self.did_open_configuration_dir)
            developer_menu.addAction(open_configuration_dir)

            open_temp_dir = QAction('Reveal temp folder in file explorer', parent)
            open_temp_dir.triggered.connect(self.did_open_temp_dir)
            developer_menu.addAction(open_temp_dir)

            mock_data_mode = QAction('Mock data', parent)
            mock_data_mode.triggered.connect(self.did_toggle_mock_data_mode)
            mock_data_mode.setCheckable(True)
            mock_data_mode.setChecked(self.configuration.is_mock_data)
            developer_menu.addAction(mock_data_mode)
            
            delay_network_mode = QAction('Delay network call', parent)
            delay_network_mode.triggered.connect(self.did_toggle_delay_network_mode)
            delay_network_mode.setCheckable(True)
            delay_network_mode.setChecked(self.configuration.is_delay_network_mode)
            developer_menu.addAction(delay_network_mode)
            
            popout_production_image_mode = QAction('Popout production images', parent)
            popout_production_image_mode.triggered.connect(self.did_toggle_popout_production_images_mode)
            popout_production_image_mode.setCheckable(True)
            popout_production_image_mode.setChecked(self.configuration.is_popout_production_images_mode)
            developer_menu.addAction(popout_production_image_mode)
        
        # return menu_bar
        self._menu_parent.setMenuBar(menu_bar)

    def new_file_tapped(self):
        self.main_program.prompt_generate_new_file()

    def did_tap_refresh_production_images(self):
        self.main_program.load()

    def did_toggle_mock_data_mode(self, is_on: bool):
        self.configuration_manager.toggle_mock_data_mode(is_on).save()
        
    def did_toggle_delay_network_mode(self, is_on: bool):
        self.configuration_manager.toggle_delay_network_mode(is_on).save()
        
    def did_toggle_popout_production_images_mode(self, is_on: bool):
        self.configuration_manager.toggle_popout_production_images_mode(is_on).save()
    
    def did_toggle_show_resource_details(self, is_on: bool):
        self.configuration_manager.toggle_show_resource_details(is_on).save()
    
    def did_toggle_hide_image_preview(self, is_on: bool):
        self.configuration_manager.toggle_hide_image_preview(is_on).save()

    def did_toggle_card_title_detail_short(self, is_on: bool):
        self.configuration_manager.set_card_title_detail(Configuration.Settings.CardTitleDetail.SHORT).save()
        self._sync_card_title_detail_checkmarks()

    def did_toggle_card_title_detail_normal(self, is_on: bool):
        self.configuration_manager.set_card_title_detail(Configuration.Settings.CardTitleDetail.NORMAL).save()
        self._sync_card_title_detail_checkmarks()

    def did_toggle_card_title_detail_detailed(self, is_on: bool):
        self.configuration_manager.set_card_title_detail(Configuration.Settings.CardTitleDetail.DETAILED).save()
        self._sync_card_title_detail_checkmarks()

    def _sync_card_title_detail_checkmarks(self):
        preference = self.configuration.card_title_detail
        self.card_title_detail_short.setChecked(preference == Configuration.Settings.CardTitleDetail.SHORT)
        self.card_title_detail_normal.setChecked(preference == Configuration.Settings.CardTitleDetail.NORMAL)
        self.card_title_detail_detailed.setChecked(preference == Configuration.Settings.CardTitleDetail.DETAILED)
    
    def did_open_production_dir(self):
        self.main_program.open_production_dir()
        
    def did_open_configuration_dir(self):
        self.main_program.open_configuration_dir()

    def did_open_temp_dir(self):
        self.main_program.open_temp_dir()
        
    def did_tap_settings(self):
        def remove_ref():
            self.settings = None
        if self.settings is None or self.settings.isHidden():
            self.settings = SettingsViewController(self.configuration_manager)
            self.settings.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.settings.destroyed.connect(remove_ref)
            self.settings.show()
        if not self.settings.isHidden():
            self.settings.activateWindow()

    def did_unstage_all_staging_resources(self):
        self.main_program.confirm_unstage_all_resources()
            
    def open_update_page(self):
        webbrowser.open("https://github.com/hdchan/R4-MG/releases")
        
    def did_clear_cache_dir(self):
        self.main_program.confirm_clear_cache()
        
        
    def open_about_page(self):
        def remove_ref():
            self.about = None
        if self.about is None or self.about.isHidden():
            self.about = AboutViewController(self.configuration_manager, 
                                             self.asset_provider)
            self.about.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            # https://stackoverflow.com/a/65357051
            self.about.destroyed.connect(remove_ref)
            self.about.show()
        if not self.about.isHidden():
            self.about.activateWindow()
        
        