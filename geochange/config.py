# @generated [partially] Gemini: helped with safe yaml work and comments
"""Configuration loader for the GeoChange application"""
from pathlib import Path
import yaml

# Absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Loads the YAML configuration file and returns it as a dictionary"""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# Global variable containing the loaded config to be used by other modules
SETTINGS = load_config()
