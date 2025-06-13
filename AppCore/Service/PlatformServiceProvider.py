import os
import platform
import shutil
import subprocess

from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import *


class PlatformServiceProtocol:

    def __init__(self, 
               configuration_manager: ConfigurationManager,
               observation_tower: ObservationTower):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def open_file(self, file_path: str) -> None:
        pass

    def open_file_directory_and_select_file(self, file_path: str) -> None:
        pass
    
    def clear_cache(self):
        shutil.rmtree(self._configuration.cache_dir_path)
        self._observation_tower.notify(CacheClearedEvent())


class PlatformServiceProvider:
    class Mac(PlatformServiceProtocol):
        def open_file(self, file_path: str) -> None:
            os.system(f"open {file_path}")

        def open_file_directory_and_select_file(self, file_path: str) -> None:
            subprocess.call(["open", "-R", f"{os.path.abspath(file_path)}"])

    class Windows(PlatformServiceProtocol):
        def open_file(self, file_path: str) -> None:
            os.startfile(file_path) # type: ignore

        def open_file_directory_and_select_file(self, file_path: str) -> None:
            subprocess.Popen(rf'explorer /select,"{os.path.abspath(file_path)}"')

    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 observation_tower: ObservationTower):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._mac = self.Mac(configuration_manager, observation_tower)
        self._windows = self.Windows(configuration_manager, observation_tower)

    @property
    def platform_service(self) -> PlatformServiceProtocol:
        if platform.system() == "Darwin":
            return self._mac
        elif platform.system() == "Windows":
            return self._windows
        raise Exception('Platform not recognized')