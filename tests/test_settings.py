"""Tests for the Settings module."""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json
import tempfile
import shutil

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import Settings


class TestSettings(unittest.TestCase):
    """Test cases for Settings class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Mock logger to avoid logging during tests
        self.logger_patcher = patch('src.config.settings.logging.getLogger')
        self.mock_logger = self.logger_patcher.start()
        self.mock_logger.return_value = MagicMock()

    def tearDown(self):
        """Clean up after tests."""
        # Stop logger patcher
        self.logger_patcher.stop()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_init_with_defaults(self):
        """Test initialization with default settings."""
        # Use a non-existent file
        settings = Settings(config_file=os.path.join(self.temp_dir, "nonexistent.json"))
        
        # Verify defaults were loaded
        self.assertEqual(settings.get("pir_sensor", "pin"), 17)
        self.assertEqual(settings.get("camera", "resolution"), [1920, 1080])
        self.assertEqual(settings.get("storage", "base_dir"), "photos")

    def test_init_with_config_file(self):
        """Test initialization with an existing config file."""
        # Create a test config file
        test_config = {
            "pir_sensor": {
                "pin": 18,
                "trigger_cooldown": 10
            },
            "camera": {
                "resolution": [800, 600]
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Initialize settings with the test file
        settings = Settings(config_file=self.config_file)
        
        # Verify settings from file were loaded
        self.assertEqual(settings.get("pir_sensor", "pin"), 18)
        self.assertEqual(settings.get("pir_sensor", "trigger_cooldown"), 10)
        self.assertEqual(settings.get("camera", "resolution"), [800, 600])
        
        # Verify default values for settings not in file
        self.assertEqual(settings.get("storage", "base_dir"), "photos")

    def test_get_section(self):
        """Test getting an entire section."""
        settings = Settings(config_file=os.path.join(self.temp_dir, "nonexistent.json"))
        
        # Get the entire camera section
        camera_section = settings.get("camera")
        
        # Verify the section contains all expected keys
        self.assertIsInstance(camera_section, dict)
        self.assertIn("resolution", camera_section)
        self.assertIn("rotation", camera_section)
        self.assertEqual(camera_section["resolution"], [1920, 1080])

    def test_get_invalid_section(self):
        """Test getting an invalid section."""
        settings = Settings(config_file=os.path.join(self.temp_dir, "nonexistent.json"))
        
        # Try to get a non-existent section
        result = settings.get("nonexistent_section")
        
        # Should return None for invalid section
        self.assertIsNone(result)

    def test_get_invalid_key(self):
        """Test getting an invalid key."""
        settings = Settings(config_file=os.path.join(self.temp_dir, "nonexistent.json"))
        
        # Try to get a non-existent key
        result = settings.get("camera", "nonexistent_key")
        
        # Should return None for invalid key
        self.assertIsNone(result)

    def test_set_existing_key(self):
        """Test setting an existing key."""
        settings = Settings(config_file=self.config_file)
        
        # Set an existing key
        settings.set("camera", "resolution", [640, 480])
        
        # Verify the key was updated
        self.assertEqual(settings.get("camera", "resolution"), [640, 480])
        
        # Verify the file was updated
        with open(self.config_file, 'r') as f:
            saved_settings = json.load(f)
            self.assertEqual(saved_settings["camera"]["resolution"], [640, 480])

    def test_set_new_key(self):
        """Test setting a new key."""
        settings = Settings(config_file=self.config_file)
        
        # Set a new key
        settings.set("camera", "new_key", "new_value")
        
        # Verify the key was added
        self.assertEqual(settings.get("camera", "new_key"), "new_value")
        
        # Verify the file was updated
        with open(self.config_file, 'r') as f:
            saved_settings = json.load(f)
            self.assertEqual(saved_settings["camera"]["new_key"], "new_value")

    def test_set_new_section(self):
        """Test setting a key in a new section."""
        settings = Settings(config_file=self.config_file)
        
        # Set a key in a new section
        settings.set("new_section", "new_key", "new_value")
        
        # Verify the section and key were added
        self.assertEqual(settings.get("new_section", "new_key"), "new_value")
        
        # Verify the file was updated
        with open(self.config_file, 'r') as f:
            saved_settings = json.load(f)
            self.assertEqual(saved_settings["new_section"]["new_key"], "new_value")

    def test_get_all(self):
        """Test getting all settings."""
        settings = Settings(config_file=os.path.join(self.temp_dir, "nonexistent.json"))
        
        # Get all settings
        all_settings = settings.get_all()
        
        # Verify it's a complete dictionary
        self.assertIsInstance(all_settings, dict)
        self.assertIn("pir_sensor", all_settings)
        self.assertIn("camera", all_settings)
        self.assertIn("storage", all_settings)
        self.assertIn("uploader", all_settings)
        self.assertIn("inference", all_settings)


if __name__ == '__main__':
    unittest.main() 