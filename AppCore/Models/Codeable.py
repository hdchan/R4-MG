from typing import Any, Dict

class Encodable:
    def to_data(self) -> Dict[str, Any]:
        raise Exception

# class Decodable:
    # def from_json(self):