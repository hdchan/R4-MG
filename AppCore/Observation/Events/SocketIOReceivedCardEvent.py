from typing import Any, Dict

from ..TransmissionProtocol import TransmissionProtocol


class SocketIOReceivedCardEvent(TransmissionProtocol):
    def __init__(self, data: Dict[str, Any]):
        self.data = data
