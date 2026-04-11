import datetime
from typing import Optional

class TransmissionProtocol:
    def __init__(self):
        self._predecessor: Optional['TransmissionProtocol'] = None
        self.date_time = datetime.datetime.now()

    @property
    def transmission_identifier(self) -> Optional[str]:
        return None

    @property
    def predecessor(self) -> Optional['TransmissionProtocol']:
        return self._predecessor
    
    @predecessor.setter
    def predecessor(self, value: 'TransmissionProtocol'):
        self._predecessor = value
    
    @property
    def seconds_since_predecessor(self):
        if self.predecessor is not None:
            return (self.date_time - self.predecessor.date_time).total_seconds()
        return None