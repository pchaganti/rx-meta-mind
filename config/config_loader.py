import os
import importlib.util
from typing import Any, Optional, Dict

# Define a path to a default configuration file (e.g., app_config.py)
DEFAULT_CONFIG_FILENAME = "app_config.py"
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG_FILENAME)

class Config:
    """
    A simple configuration loader class.
    It loads settings from a Python file (e.g., app_config.py).
    """
    def __init__(self, config_file_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self.config_file_path = config_file_path or CONFIG_FILE_PATH
        self._load_config()

    def _load_config(self):
        """Loads configuration from the specified Python file."""
        if not os.path.exists(self.config_file_path):
            print(f"Warning: Configuration file not found at {self.config_file_path}. Using default empty config.")
            self._create_default_config_file_if_not_exists()

        try:
            spec = importlib.util.spec_from_file_location("app_config", self.config_file_path)
            if spec and spec.loader:
                app_config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app_config)
                
                for key in dir(app_config):
                    if key.isupper():
                        self._config[key] = getattr(app_config, key)
            else:
                print(f"Error: Could not load configuration spec from {self.config_file_path}")
        except Exception as e:
            print(f"Error loading configuration from {self.config_file_path}: {e}")

    def _create_default_config_file_if_not_exists(self):
        """Creates a default/template app_config.py if it doesn't exist."""
        if not os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                print(f"Created a default configuration file at: {self.config_file_path}")
                print("Please review and update it with your actual settings (e.g., API keys).")
            except IOError as e:
                print(f"Error creating default configuration file {self.config_file_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value."""
        return self._config.get(key, default)

    def __getattr__(self, name: str) -> Any:
        """
        Allows accessing config values like attributes (e.g., config.OPENAI_API_KEY).
        """
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}' (not found in config)")

    def __repr__(self) -> str:
        return f"Config(loaded_from='{self.config_file_path}', keys={list(self._config.keys())})"