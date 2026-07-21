import yaml
from typing import Dict, Any

class ExperimentProfile:
    def __init__(self, yaml_path: str):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    @property
    def name(self): 
        return self.config.get("profile_name", "default")
    
    @property
    def limits(self): 
        return self.config.get("limits", {})
        
    @property
    def backpressure(self): 
        return self.config.get("backpressure", {})
        
    @property
    def retry(self):
        return self.config.get("retry", {})
    
    @property
    def features(self):
        return {
            "quality": self.config.get("quality", {}).get("enabled", True),
            "semantic_safety": self.config.get("safety", {}).get("semantic", True)
        }
