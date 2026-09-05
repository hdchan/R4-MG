from PySide6.QtCore import QTimer

class Debouncer:
    def __init__(self):
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._args = None
        self._kwargs = None
        self._timer.timeout.connect(self._run_fn)
        self._internal_fn = None

    def _run_fn(self):
        if self._internal_fn is not None:
            self._internal_fn()
        self._internal_fn = None

    def trigger_fn(self, runnable_fn, timeout_ms: int = 1000):
        self._timer.stop()
        self._internal_fn = runnable_fn
        self._timer.start(timeout_ms)
