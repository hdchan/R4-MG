import concurrent.futures
import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets


def measure():
    time.sleep(5)
    return {"key": "value"}


class TaskManager(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, max_workers=None):
        super().__init__(parent)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    @property
    def executor(self):
        return self._executor

    def submit(self, fn, *args, **kwargs):
        future = self.executor.submit(fn, *args, **kwargs)
        future.add_done_callback(self._internal_done_callback)

    def _internal_done_callback(self, future):
        data = future.result()
        self.finished.emit(data)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.model = QtGui.QStandardItemModel()
        self.view = QtWidgets.QListView()
        self.view.setModel(self.model)

        self.button = QtWidgets.QPushButton("launch")

        self._manager = TaskManager(max_workers=1)
        self._manager.finished.connect(self.update_gui_fields)

        self.button.clicked.connect(self.perform_measurement)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QVBoxLayout(central_widget)
        lay.addWidget(self.view)
        lay.addWidget(self.button)

    def perform_measurement(self):
        self._manager.submit(measure)

    def update_gui_fields(self, data):
        self.model.appendRow(QtGui.QStandardItem(data["key"]))


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())