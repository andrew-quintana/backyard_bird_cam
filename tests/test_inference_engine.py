"""Tests for the InferenceEngine module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inference.inference_engine import InferenceEngine


class TestInferenceEngine(unittest.TestCase):
    """Test cases for InferenceEngine class."""

    @patch('src.inference.inference_engine.InferenceEngine.setup')
    def setUp(self, mock_setup):
        """Set up test fixtures."""
        self.model_path = 'models/bird_detector.onnx'
        self.confidence_threshold = 0.6
        self.engine = InferenceEngine(self.model_path, self.confidence_threshold)
        mock_setup.assert_called_once()

    def test_init(self):
        """Test initialization of InferenceEngine."""
        self.assertEqual(self.engine.model_path, self.model_path)
        self.assertEqual(self.engine.confidence_threshold, self.confidence_threshold)
        self.assertIsNone(self.engine.model)

    @patch('src.inference.inference_engine.InferenceEngine.detect')
    def test_detect(self, mock_detect):
        """Test bird detection in image."""
        image_path = '/tmp/test_photo.jpg'
        expected_detections = [
            {'bbox': [100, 200, 50, 50], 'confidence': 0.85, 'class': 'bird'}
        ]
        
        mock_detect.return_value = expected_detections
        result = self.engine.detect(image_path)
        
        mock_detect.assert_called_once_with(image_path)
        self.assertEqual(result, expected_detections)

    @patch('src.inference.inference_engine.InferenceEngine.classify')
    def test_classify(self, mock_classify):
        """Test bird species classification."""
        image_path = '/tmp/test_photo.jpg'
        bbox = (100, 200, 50, 50)
        expected_result = {
            'species': 'House Sparrow',
            'confidence': 0.92
        }
        
        mock_classify.return_value = expected_result
        result = self.engine.classify(image_path, bbox)
        
        mock_classify.assert_called_once_with(image_path, bbox)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main() 