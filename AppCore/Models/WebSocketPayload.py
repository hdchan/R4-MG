import jsonpickle
from typing import Any

class WebSocketPayload:

    @staticmethod
    def decode(pick_string: str):
        return jsonpickle.decode(pick_string)

    def __init__(self, action: str, metadata: dict[str, Any] = {}):
        self.action = action
        self.metadata = metadata

    @property
    def encoded_self(self) -> str:
        return jsonpickle.encode(self)