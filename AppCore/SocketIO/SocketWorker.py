from typing import Any, Optional

from PySide6.QtCore import QThread, Signal
from socketio import Client


class SocketWorker(QThread):
    connected = Signal()
    disconnected = Signal()
    add_card = Signal(dict)
    error = Signal(str)

    def __init__(self, ):
        super().__init__()
        self._url: Optional[str] = None
        self._sio: Optional[Client] = None

    def set_url(self, url: str):
        self._url = url

    @property
    def is_connected(self) -> bool:
        if self._sio is not None:
            return self._sio.connected
        return False

    def run(self):
        self._sio = Client()
        @self._sio.event
        def connect():
            self.connected.emit()

        @self._sio.event
        def disconnect():
            self.disconnected.emit()

        @self._sio.event
        def connect_error(data):
            self.error.emit(str(data))

        @self._sio.on('add-card')
        def _on_message(data):
            self.add_card.emit({'type': 'add-card', 'data': data})

        try:
            # python-socketio will perform the handshake and upgrade to websocket
            self._sio.connect(self._url, transports=['websocket'])
            # Blocks here until disconnect()
            self._sio.wait()
        except Exception as exc:
            self.error.emit(str(exc))

    def emit(self, event: str, data: Any) -> None:
        if self._sio and getattr(self._sio, 'connected', False):
            try:
                self._sio.emit(event, data)
            except Exception as exc:
                self.error.emit(str(exc))

    def stop(self) -> None:
        try:
            if self._sio:
                self._sio.disconnect()
        except Exception:
            pass
        self.quit()
        self.wait()