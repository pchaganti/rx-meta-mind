from .config_loader import Config

# Initialize a global config instance
# This allows easy access to config values from anywhere in the application
settings = Config()

__all__ = [
    "settings",
    "Config"
]