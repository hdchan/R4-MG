import os
import platform
import subprocess


class PlatformProtocol:
    def open_file(self, file_path: str) -> None:
        pass

    def open_file_path_and_select_file(self, file_path: str) -> None:
        pass

class PlatformServiceProvider:
    class Mac(PlatformProtocol):
        def open_file(self, file_path: str) -> None:
            os.system(f"open {file_path}")

        def open_file_path_and_select_file(self, file_path: str) -> None:
            subprocess.call(["open", "-R", f"{os.path.abspath(file_path)}"])

    class Windows(PlatformProtocol):
        def open_file(self, file_path: str) -> None:
            os.startfile(file_path) # type: ignore

        def open_file_path_and_select_file(self, file_path: str) -> None:
            subprocess.Popen(rf'explorer /select,"{os.path.abspath(file_path)}"')

    def __init__(self):
        self._mac = self.Mac()
        self._windows = self.Windows()

    def providePlatform(self) -> PlatformProtocol:
        if platform.system() == "Darwin":
            return self._mac
        elif platform.system() == "Windows":
            return self._windows
        raise Exception('Platform not recognized')