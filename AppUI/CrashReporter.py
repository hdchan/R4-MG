import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt5.QtWidgets import QDialog

from R4UI import Label, VerticalBoxLayout

from .AppDependenciesInternalProviding import AppDependenciesInternalProviding


class CustomDialog(QDialog):
    def __init__(self, crash_message: str):
        super().__init__()
        self.setWindowTitle("Crash")

        VerticalBoxLayout([
            Label(crash_message)
        ]).set_layout_to_widget(self)

        # layout = QVBoxLayout()

        # self.label = QtWidgets.QLabel("Enter your name:")
        # layout.addWidget(self.label)

        # self.name_input = QtWidgets.QLineEdit()
        # layout.addWidget(self.name_input)

        # button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # button_box.accepted.connect(self.accept)
        # button_box.rejected.connect(self.reject)
        # layout.addWidget(button_box)


class CrashReporter:

    def __init__(self, application_dependencies_provider: AppDependenciesInternalProviding):
        # https://www.google.com/search?q=how+to+log+crashes+python+for+app+uncaught+exception&client=firefox-b-1-d&sca_esv=679517c3ba0a5d08&sxsrf=AE3TifM2i-CVy1Fu2aSTEM7fy4faAwAxNw%3A1760131746901&ei=onrpaObnNvK0ptQPweiGmAs&oq=how+to+log+crashes+python+for+app+uncaugh&gs_lp=Egxnd3Mtd2l6LXNlcnAiKWhvdyB0byBsb2cgY3Jhc2hlcyBweXRob24gZm9yIGFwcCB1bmNhdWdoKgIIATIFECEYoAEyBRAhGKABMgUQIRigATIFECEYoAEyBRAhGKABSL0XUI0CWKUQcAF4AZABAJgBdKAB7wWqAQM1LjO4AQPIAQD4AQGYAgmgAocGwgIKEAAYsAMY1gQYR8ICBRAhGKsCwgIFECEYnwWYAwCIBgGQBgSSBwM2LjOgB44vsgcDNS4zuAeFBsIHBTAuOC4xyAcO&sclient=gws-wiz-serp
    
        def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Don't log KeyboardInterrupt as a crash
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logger.critical(
                "Uncaught exception, application will terminate.",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
            application_dependencies_provider.router.show_error(Exception(exc_value))
            # Optionally, you can call the default excepthook as well
            # sys.__excepthook__(exc_type, exc_value, exc_traceback)

        max_log_size = 5 * 1024 * 1024  # 5 MB
        # Define the number of backup log files to keep
        backup_count = 5

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create a file handler
        Path(application_dependencies_provider.configuration_manager.configuration.logs_dir_path).mkdir(parents=True, exist_ok=True)
        log_file_path = application_dependencies_provider.configuration_manager.configuration.app_crash_log_path
        
        handler = RotatingFileHandler(
            log_file_path,
            mode='a',
            maxBytes=max_log_size,
            backupCount=backup_count,
            encoding='utf-8' # Specify encoding if needed
        )

        # Create a formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)
        sys.excepthook = handle_uncaught_exception
        logger.info("Application started.")