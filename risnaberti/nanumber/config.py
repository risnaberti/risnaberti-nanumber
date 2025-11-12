# nanumber/config.py
from pydantic import BaseSettings
from typing import Dict, Optional
import yaml
from pathlib import Path

class NanumberSettings(BaseSettings):
    default_pad: int = 4
    default_pad_char: str = "0"
    db_url: Optional[str] = None   # e.g., sqlite:///./nanumber.db or postgresql://...
    templates_file: Optional[str] = None

    class Config:
        env_prefix = "NANUMBER_"
        env_file = ".env"

def load_templates(path: Optional[str]):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return yaml.safe_load(f) or {}

def get_settings() -> NanumberSettings:
    return NanumberSettings()
