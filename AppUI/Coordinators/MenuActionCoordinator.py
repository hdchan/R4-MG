import webbrowser

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import (QAction, QInputDialog, QMenu, QMenuBar,
                             QMessageBox, QWidget)

from AppCore import ApplicationCore
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
                 app_core: ApplicationCore,
                 configuration_manager: ConfigurationManager, 
                 asset_provider: AssetProvider):
        super().__init__()
        self.app_core = app_core
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
        menuBar = QMenuBar(parent)
        menuBar.setNativeMenuBar(False)

        # MARK: - File
        fileMenu = QMenu("&File", parent)
        menuBar.addMenu(fileMenu)

        new_file_menu = QAction('New image file', parent)
        new_file_menu.triggered.connect(self.new_file_tapped)
        fileMenu.addAction(new_file_menu)

        refresh_production_images = QAction('Refresh production images', parent)
        refresh_production_images.triggered.connect(self.did_tap_refresh_production_images)
        fileMenu.addAction(refresh_production_images)
        
        
        open_production_dir = QAction('Reveal images in file explorer', parent)
        open_production_dir.triggered.connect(self.did_open_production_dir)
        fileMenu.addAction(open_production_dir)
        
        clear_cache_dir = QAction('Clear cache', parent)
        clear_cache_dir.triggered.connect(self.did_clear_cache_dir)
        # fileMenu.addAction(clear_cache_dir)

        
        # MARK: - Settings
        settings_menu = QAction("Settings", parent)
        settings_menu.triggered.connect(self.did_tap_settings)
        fileMenu.addAction(settings_menu)
        
        # MARK: - About
        about_menu = QMenu("&Help", parent)
        menuBar.addMenu(about_menu)

        version = QAction(f"v.{self.configuration.app_ui_version}", parent)
        version.setEnabled(False)
        about_menu.addAction(version)

        check_update = QAction('Check for updates', parent)
        check_update.triggered.connect(self.open_update_page)
        about_menu.addAction(check_update)

        about = QAction(f"About", parent)
        about.triggered.connect(self.open_about_page)
        about_menu.addAction(about)

        # MARK: - Developer
        if self.configuration.is_developer_mode:
            developer_menu = QMenu("&Developer", parent)
            menuBar.addMenu(developer_menu)

            open_configuration_dir = QAction('Reveal configuration in file explorer', parent)
            open_configuration_dir.triggered.connect(self.did_open_configuration_dir)
            developer_menu.addAction(open_configuration_dir)

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
        
        # return menuBar
        self._menu_parent.setMenuBar(menuBar)

    def new_file_tapped(self):
        text, ok = QInputDialog.getText(self._menu_parent, 'Create new image file', 'Enter file name:')
        if ok:
            try:
                self.did_input_new_file_name(text)
            except Exception as error:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Warning)
                msgBox.setText(str(error))
                msgBox.setWindowTitle("Error")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
                msgBox.exec()

    def did_input_new_file_name(self, file_name: str):
        self.app_core.generate_new_file(file_name)
        self.main_program.load()

    def did_tap_refresh_production_images(self):
        self.main_program.load()

    def did_toggle_mock_data_mode(self, is_on: bool):
        self.configuration_manager.toggle_mock_data_mode(is_on).save()
        
    def did_toggle_delay_network_mode(self, is_on: bool):
        self.configuration_manager.toggle_delay_network_mode(is_on).save()
        
    def did_toggle_popout_production_images_mode(self, is_on: bool):
        self.configuration_manager.toggle_popout_production_images_mode(is_on).save()
        
    def did_open_production_dir(self):
        self.app_core.open_production_dir()
        
    def did_open_configuration_dir(self):
        self.app_core.open_configuration_dir()
        
    def did_tap_settings(self):
        if self.settings is None or self.settings.isHidden():
            self.settings = SettingsViewController(self.configuration_manager)
            self.settings.show()
        if not self.settings.isHidden():
            self.settings.activateWindow()
            
    def open_update_page(self):
        webbrowser.open("https://github.com/hdchan/R4-MG/releases")
        
    def did_clear_cache_dir(self):
        self.app_core.clear_cache()
        
    def open_about_page(self):
        if self.about is None or self.about.isHidden():
            self.about = AboutViewController(self.configuration_manager, 
                                             self.asset_provider)
            self.about.show()
        if not self.about.isHidden():
            self.about.activateWindow()
        
        