"""Configuration settings module."""
import os
import json
import logging


class Settings:
    """Class to handle application configuration settings."""

    DEFAULT_SETTINGS = {
        "pir_sensor": {
            "pin": 17,
            "trigger_cooldown": 5  # seconds
        },
        "camera": {
            "resolution": [1920, 1080],
            "rotation": 0,
            "focus_distance_inches": 13.5  # Focus distance in inches (8 inches to infinity)
        },
        "storage": {
            "base_dir": "photos",
            "max_photos": 1000
        },
        "uploader": {
            "service": "s3",
            "bucket": "bird-photos",
            "auto_upload": True
        },
        "inference": {
            "model_path": "models/bird_detector.onnx",
            "confidence_threshold": 0.5,
            "auto_classify": True
        }
    }

    def __init__(self, config_file="config.json"):
        """Initialize settings from config file or defaults.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.settings = {}
        self.logger = logging.getLogger(__name__)
        self.load()
        
    def load(self):
        """Load settings from file or use defaults if file doesn't exist."""
        self.logger.info(f"Loading settings from {self.config_file}")
        
        # Start with default settings
        self.settings = self.DEFAULT_SETTINGS.copy()
        
        # Override with file settings if available
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_settings = json.load(f)
                
                # Update settings with file values
                self._update_nested_dict(self.settings, file_settings)
                self.logger.info("Settings loaded from file")
            except Exception as e:
                self.logger.error(f"Error loading settings from file: {e}")
                self.logger.info("Using default settings")
        else:
            self.logger.info(f"Configuration file {self.config_file} not found. Using default settings.")
            # Save the default settings to create the file
            self.save()
    
    def _update_nested_dict(self, d, u):
        """Update a nested dictionary recursively.
        
        Args:
            d (dict): Original dictionary to update
            u (dict): Dictionary with updated values
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        
    def save(self):
        """Save current settings to file."""
        self.logger.info(f"Saving settings to {self.config_file}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
        
    def get(self, section, key=None):
        """Get a setting value.
        
        Args:
            section (str): Settings section name
            key (str, optional): Setting key name. If None, returns entire section
            
        Returns:
            The setting value or section dictionary
        """
        if section not in self.settings:
            self.logger.warning(f"Section '{section}' not found in settings")
            return None
            
        if key is None:
            return self.settings[section]
            
        if key not in self.settings[section]:
            self.logger.warning(f"Key '{key}' not found in section '{section}'")
            return None
            
        return self.settings[section][key]
        
    def set(self, section, key, value):
        """Set a setting value.
        
        Args:
            section (str): Settings section name
            key (str): Setting key name
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Create section if it doesn't exist
        if section not in self.settings:
            self.settings[section] = {}
            
        # Set the value
        self.settings[section][key] = value
        
        # Save the updated settings
        self.save()
        
        return True
        
    def get_all(self):
        """Get all settings.
        
        Returns:
            dict: Copy of all settings
        """
        return self.settings.copy() 