from pathlib import Path
import json
from typing import Optional
from ..config import Config, ModelConfig

DEFAULT_CONFIG = {
    "model": {
        "model_name": "llama3.2",
        "temperature": 0.1,
        "max_tokens": None,
        "context_window": 10000,
        "overlap": 200
    },
    "language": "de",
    "output_dir": "outputs",
    "verbose": False
}

def create_default_config(path: Path):
    """Create a default configuration file"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)

def load_or_create_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration or create default if none exists"""
    if config_path is None:
        config_path = Path.home() / ".transcript-summarizer" / "config.json"
        
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        create_default_config(config_path)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return Config(**config_data) 