import json
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar
from pathlib import Path

T = TypeVar("T")



class DataSerializer:
    
    class ModelEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Dict[str, Any]:
            try:
                return o.to_data()
            except:
                return super().default(o)
    
    def save_buffer_data(self, file_path: str, buffer_data: Any):
        self.save_json_data(file_path, json.load(buffer_data))
    
    def save_json_data(self, file_path: str, json_data: Any):
        # Ensure parent dir is created
        Path(Path(file_path).parent).mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump(json_data, f, cls=self.ModelEncoder)
            
    def load(self, file_path: str) -> Optional[Any]:
        my_file = Path(file_path)
        if my_file.is_file():
            with open(file_path, "r") as f:
                try:
                    loaded = json.load(f)
                    return loaded
                except:
                    return None