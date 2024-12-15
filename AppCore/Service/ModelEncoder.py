import json
from typing import Any, Dict


class ModelEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Dict[str, Any]:
        try:
            return o.to_data()
        except:
            return super().default(o)