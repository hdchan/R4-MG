from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import (QAction, QInputDialog, QMenu, QMenuBar,
                             QMessageBox, QWidget)

from AppCore.Config.ConfigurationManager import ConfigurationManager
from AppCore.Image.ImageResourceDeployer import ImageResourceDeployer

from ..MainProgramViewController import MainProgramViewController
from ..Window import Window

class MenuActionCoordinator(QObject):
    def __init__(self,
                 window: Window,
                 main_program: MainProgramViewController, 
                 resource_deployer: ImageResourceDeployer,
                 configuration_manager: ConfigurationManager):
        super().__init__()
        self.main_program = main_program
        self.resource_deployer = resource_deployer
        self.configuration_manager = configuration_manager
        self.configuration = configuration_manager.configuration
        self._menu_parent = window
        self.attachMenuBar(window)

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

        performance_mode = QAction('🚗💨', parent)
        performance_mode.triggered.connect(self.did_toggle_performance_mode)
        performance_mode.setCheckable(True)
        performance_mode.setChecked(self.configuration.is_performance_mode)
        fileMenu.addAction(performance_mode)


        # MARK: - About
        about_menu = QMenu("&About", parent)
        menuBar.addMenu(about_menu)

        version_info = QAction(f"v.{self.configuration.app_ui_version}", parent)
        version_info.setEnabled(False)
        about_menu.addAction(version_info)

        # MARK: - Developer
        if self.configuration.is_developer_mode:
            developer_menu = QMenu("&Developer", parent)
            menuBar.addMenu(developer_menu)

            mock_data_mode = QAction('Mock data', parent)
            mock_data_mode.triggered.connect(self.did_toggle_mock_data_mode)
            mock_data_mode.setCheckable(True)
            mock_data_mode.setChecked(self.configuration.is_mock_data)
            developer_menu.addAction(mock_data_mode)
            
            delay_network_mode = QAction('Delay network call', parent)
            delay_network_mode.triggered.connect(self.did_toggle_delay_network_mode)
            delay_network_mode.setCheckable(True)
            delay_network_mode.setChecked(self.configuration.is_delay_network_mode)
            developer_menu.addAction((delay_network_mode))
        
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
        self.resource_deployer.generate_new_file(file_name)
        self.main_program.load()

    def did_tap_refresh_production_images(self):
        self.main_program.load()

    def did_toggle_performance_mode(self, is_on: bool):
        self.configuration_manager.toggle_performance_mode(is_on)

    def did_toggle_mock_data_mode(self, is_on: bool):
        self.configuration_manager.toggle_mock_data_mode(is_on)
        
    def did_toggle_delay_network_mode(self, is_on: bool):
        self.configuration_manager.toggle_delay_network_mode(is_on)
