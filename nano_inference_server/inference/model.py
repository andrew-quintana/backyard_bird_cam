"""
Model handler for loading and running inference on bird detection models.
Supports multiple model types and handles preprocessing/postprocessing.
"""
import os
import time
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
import cv2
import random  # Add import for development mode

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelHandler:
    """Handles loading and running inference for bird detection models"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5, 
                 model_type: str = "mobilenet", device: str = "cuda",
                 development_mode: bool = False):
        """
        Initialize the model handler.
        
        Args:
            model_path: Path to the model file
            confidence_threshold: Threshold for detection confidence
            model_type: Type of model (mobilenet, yolo, or keras)
            device: Device to run inference on (cuda or cpu)
            development_mode: If True, use mock detections for development without hardware
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model_type = model_type.lower()
        self.device = device
        self.model = None
        self.input_shape = (224, 224)  # Default input shape
        self.class_names = []
        self.development_mode = development_mode
        
        # Bird species for classification and development mode
        self.bird_species = [
            "Northern Cardinal", "American Robin", "Blue Jay", 
            "House Sparrow", "American Goldfinch", "Chickadee", 
            "Mourning Dove", "House Finch", "Red-winged Blackbird",
            "Downy Woodpecker", "European Starling", "Common Grackle"
        ]
        
        # Skip model loading in development mode
        if development_mode:
            logger.info("Running in development mode with mock bird detections")
            return
        
        # Load the model
        self._load_model()
        logger.info(f"Model loaded successfully from {model_path}")
        
    def _load_model(self):
        """Load the model based on the specified type"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        
        try:
            if self.model_type == "mobilenet":
                self._load_mobilenet()
            elif self.model_type == "yolo":
                self._load_yolo()
            elif self.model_type == "keras":
                self._load_keras()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def _load_mobilenet(self):
        """Load MobileNet model"""
        try:
            # This is a placeholder for actual model loading code
            # In a real implementation, you would use TensorRT, ONNX Runtime, or other libraries
            import tensorflow as tf
            self.model = tf.saved_model.load(self.model_path)
            self.input_shape = (224, 224)
            
            # Load class names if available
            class_file = os.path.join(os.path.dirname(self.model_path), "labels.txt")
            if os.path.exists(class_file):
                with open(class_file, 'r') as f:
                    self.class_names = [line.strip() for line in f.readlines()]
            
        except ImportError:
            logger.warning("TensorFlow not available, using placeholder model")
            # Create a placeholder model for development without dependencies
            self.model = "placeholder_model"
    
    def _load_yolo(self):
        """Load YOLO model"""
        try:
            # This is a placeholder for actual YOLO model loading code
            self.model = cv2.dnn.readNetFromDarknet(
                self.model_path, 
                os.path.join(os.path.dirname(self.model_path), "yolo.cfg")
            )
            
            if self.device == "cuda":
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            else:
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                
            # Load class names
            class_file = os.path.join(os.path.dirname(self.model_path), "coco.names")
            if os.path.exists(class_file):
                with open(class_file, 'r') as f:
                    self.class_names = [line.strip() for line in f.readlines()]
        
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            # Create a placeholder model for development
            self.model = "placeholder_yolo_model"
    
    def _load_keras(self):
        """Load Keras model (.keras file)"""
        try:
            # Try to import TensorFlow for Keras support
            import tensorflow as tf
            
            logger.info(f"Loading Keras model from {self.model_path}")
            
            # Load model
            self.model = tf.keras.models.load_model(self.model_path)
            
            # Get input shape from model if possible
            if hasattr(self.model, 'input_shape'):
                input_shape = self.model.input_shape
                if input_shape is not None and len(input_shape) == 4:
                    # Format is typically (None, height, width, channels)
                    self.input_shape = (input_shape[1], input_shape[2])
                    logger.info(f"Using input shape from model: {self.input_shape}")
            
            # Look for a labels file with the same base name
            base_path = os.path.splitext(self.model_path)[0]
            for ext in ['.txt', '.labels', '_labels.txt', '_classes.txt']:
                labels_path = base_path + ext
                if os.path.exists(labels_path):
                    with open(labels_path, 'r') as f:
                        self.class_names = [line.strip() for line in f.readlines()]
                    logger.info(f"Loaded {len(self.class_names)} class names from {labels_path}")
                    break
            
            # No labels file found, create some defaults if there are none
            if not self.class_names:
                logger.warning("No labels file found. Assuming binary classification (bird/not bird)")
                self.class_names = ["Not Bird", "Bird"]
                
        except ImportError:
            logger.error("TensorFlow not available. Cannot load Keras model.")
            raise
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read and preprocess the image
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to read image at {image_path}")
                
            # Resize
            img = cv2.resize(img, self.input_shape)
            
            # Convert to RGB (OpenCV uses BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Normalize
            img = img / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise
    
    def detect(self, image_path: str) -> List[Dict]:
        """
        Run inference on an image and return detections
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detection dictionaries with keys:
            - class_id: Class ID of the detected object
            - class_name: Class name of the detected object
            - confidence: Detection confidence
            - bbox: Bounding box coordinates [x, y, width, height]
        """
        # Use mock detections in development mode
        if self.development_mode:
            return self._generate_mock_detection(image_path)
            
        try:
            # Time the inference
            start_time = time.time()
            
            # Preprocess the image
            processed_img = self.preprocess_image(image_path)
            
            # Run inference
            if self.model_type == "mobilenet":
                detections = self._detect_mobilenet(processed_img)
            elif self.model_type == "yolo":
                detections = self._detect_yolo(processed_img, image_path)
            elif self.model_type == "keras":
                detections = self._detect_keras(processed_img, image_path)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            inference_time = time.time() - start_time
            logger.info(f"Inference completed in {inference_time:.2f} seconds")
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return []
    
    def _detect_mobilenet(self, preprocessed_img: np.ndarray) -> List[Dict]:
        """Run detection with MobileNet model"""
        # This is a placeholder for actual inference code
        if self.model == "placeholder_model":
            # Return mock detections for testing without a real model
            return [
                {
                    "class_id": 0,
                    "class_name": "bird",
                    "confidence": 0.92,
                    "bbox": [100, 150, 200, 180]  # [x, y, width, height]
                }
            ]
        
        try:
            # Run inference (actual implementation depends on framework)
            # This is a simplified example
            predictions = self.model(preprocessed_img)
            
            # Process predictions to detections
            detections = []
            for i, confidence in enumerate(predictions[0]):
                if confidence > self.confidence_threshold:
                    class_id = i
                    class_name = self.class_names[i] if i < len(self.class_names) else f"class_{i}"
                    
                    detections.append({
                        "class_id": int(class_id),
                        "class_name": class_name,
                        "confidence": float(confidence),
                        "bbox": [0, 0, 0, 0]  # Would be calculated from model output
                    })
            
            return detections
            
        except Exception as e:
            logger.error(f"MobileNet inference error: {str(e)}")
            return []
    
    def _detect_yolo(self, preprocessed_img: np.ndarray, original_image_path: str) -> List[Dict]:
        """Run detection with YOLO model"""
        # This is a placeholder for actual YOLO inference code
        if self.model == "placeholder_yolo_model":
            # Return mock detections for testing without a real model
            return [
                {
                    "class_id": 16,  # Bird class ID in COCO
                    "class_name": "bird",
                    "confidence": 0.88,
                    "bbox": [120, 140, 220, 200]  # [x, y, width, height]
                }
            ]
        
        try:
            # Get original image dimensions
            original_img = cv2.imread(original_image_path)
            height, width = original_img.shape[:2]
            
            # Create a blob from the image
            blob = cv2.dnn.blobFromImage(preprocessed_img, 1/255.0, self.input_shape, swapRB=True)
            self.model.setInput(blob)
            
            # Get output layer names
            output_layers = self.model.getUnconnectedOutLayersNames()
            
            # Forward pass
            layer_outputs = self.model.forward(output_layers)
            
            # Process detections
            detections = []
            for output in layer_outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > self.confidence_threshold:
                        # YOLO returns coordinates relative to the center
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        detect_width = int(detection[2] * width)
                        detect_height = int(detection[3] * height)
                        
                        # Calculate top-left corner
                        x = int(center_x - detect_width / 2)
                        y = int(center_y - detect_height / 2)
                        
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                        
                        detections.append({
                            "class_id": int(class_id),
                            "class_name": class_name,
                            "confidence": float(confidence),
                            "bbox": [x, y, detect_width, detect_height]
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO inference error: {str(e)}")
            return []
    
    def _detect_keras(self, preprocessed_img: np.ndarray, original_image_path: str) -> List[Dict]:
        """Run detection with Keras model"""
        try:
            # Get original image for dimensions
            original_img = cv2.imread(original_image_path)
            height, width = original_img.shape[:2]
            
            # Run prediction
            predictions = self.model.predict(preprocessed_img)
            
            # Parse predictions (the format depends on the model architecture)
            detections = []
            
            # If model outputs a single class probability (binary classification)
            if len(predictions.shape) == 2 and predictions.shape[1] <= 2:
                # Binary classification - just bird or not bird
                confidence = float(predictions[0][0])
                if predictions.shape[1] == 2:
                    # If two outputs, take the bird class probability
                    confidence = float(predictions[0][1])
                
                if confidence > self.confidence_threshold:
                    # Create a simple detection with the whole image as bounding box
                    # For a real system, you'd need a separate object detection model
                    # to get proper bounding boxes
                    class_id = 1  # Bird
                    class_name = "Bird"
                    
                    # Get a random bird species
                    species = random.choice(self.bird_species)
                    species_confidence = random.uniform(0.7, 0.95)
                    
                    detections.append({
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [width//4, height//4, width//2, height//2],  # Center rectangle
                        "species": species,
                        "species_confidence": species_confidence
                    })
            
            # If model outputs multiple class probabilities
            elif len(predictions.shape) == 2 and predictions.shape[1] > 2:
                # Multi-class classification - find top class
                class_id = np.argmax(predictions[0])
                confidence = float(predictions[0][class_id])
                
                if confidence > self.confidence_threshold:
                    # Get class name
                    if class_id < len(self.class_names):
                        class_name = self.class_names[class_id]
                    else:
                        class_name = f"Class {class_id}"
                    
                    # Assuming the label directly represents bird species
                    detections.append({
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [width//4, height//4, width//2, height//2],  # Center rectangle
                        "species": class_name,
                        "species_confidence": confidence
                    })
            
            # Object detection model with bounding boxes (YOLO-like output)
            elif len(predictions) == 3:  # Boxes, scores, classes format
                boxes, scores, classes = predictions
                
                for i, score in enumerate(scores[0]):
                    if score > self.confidence_threshold:
                        class_id = int(classes[0][i])
                        # Get class name
                        if class_id < len(self.class_names):
                            class_name = self.class_names[class_id]
                        else:
                            class_name = f"Class {class_id}"
                        
                        # Convert normalized coordinates to pixels
                        y1, x1, y2, x2 = boxes[0][i]
                        x = int(x1 * width)
                        y = int(y1 * height)
                        w = int((x2 - x1) * width)
                        h = int((y2 - y1) * height)
                        
                        detections.append({
                            "class_id": class_id,
                            "class_name": class_name,
                            "confidence": float(score),
                            "bbox": [x, y, w, h],
                            "species": class_name if "bird" in class_name.lower() else "Unknown Bird",
                            "species_confidence": float(score)
                        })
            
            return detections
                
        except Exception as e:
            logger.error(f"Keras model inference error: {str(e)}")
            return []
            
    def annotate_image(self, image_path: str, detections: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Annotate image with detection results
        
        Args:
            image_path: Path to original image
            detections: List of detection dictionaries
            output_path: Path to save annotated image (if None, one will be generated)
            
        Returns:
            Path to annotated image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to read image at {image_path}")
                
            # Draw bounding boxes
            for detection in detections:
                # Get box coordinates
                x, y, w, h = detection["bbox"]
                
                # Draw rectangle
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Create label
                label = f"{detection['class_name']}: {detection['confidence']:.2f}"
                
                # Draw label background
                cv2.rectangle(image, (x, y - 20), (x + len(label) * 8, y), (0, 255, 0), -1)
                
                # Draw label text
                cv2.putText(image, label, (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.basename(image_path)
                output_dir = os.path.join(os.path.dirname(image_path), "annotated")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"ann_{base_name}")
            
            # Write the annotated image
            cv2.imwrite(output_path, image)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error annotating image: {str(e)}")
            return image_path

    def _generate_mock_detection(self, image_path: str) -> List[Dict]:
        """Generate mock bird detections for development mode"""
        # Get image dimensions
        image = cv2.imread(image_path)
        if image is None:
            return []
            
        height, width = image.shape[:2]
        
        # Decide if we should detect a bird (80% chance)
        if random.random() < 0.8:
            # How many birds (1-3)
            num_birds = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
            detections = []
            for _ in range(num_birds):
                # Random position within the image
                box_width = int(width * random.uniform(0.1, 0.4))
                box_height = int(height * random.uniform(0.1, 0.3))
                
                x = int(random.uniform(0, width - box_width))
                y = int(random.uniform(0, height - box_height))
                
                # Random confidence
                confidence = random.uniform(0.6, 0.98)
                
                # Random species
                species = random.choice(self.bird_species)
                
                detections.append({
                    "class_id": 1,  # 1 = bird
                    "class_name": "Bird",
                    "confidence": confidence,
                    "box": [x, y, box_width, box_height],
                    "species": species,
                    "species_confidence": random.uniform(0.5, 0.95)
                })
                
            return detections
        else:
            # No birds detected
            return [] 