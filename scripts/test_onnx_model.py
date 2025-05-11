import numpy as np
import onnxruntime as ort
import cv2
import time
import os
import glob

# Path to the ONNX model
model_path = "common/models/bird_model.onnx"

# Load the ONNX model
print("Loading ONNX model...")
session = ort.InferenceSession(model_path)

# Get model metadata
input_name = session.get_inputs()[0].name
input_shape = session.get_inputs()[0].shape
output_name = session.get_outputs()[0].name

print(f"Model input name: {input_name}, shape: {input_shape}")
print(f"Model output name: {output_name}")

# Get the first image from the test_images directory
test_images = glob.glob("test_images/*.*")
if not test_images:
    raise FileNotFoundError("No test images found in test_images directory")

test_image_path = test_images[0]
print(f"Using test image: {test_image_path}")

def preprocess_image(image_path, input_shape):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")
    
    # Resize to model's expected input dimensions
    height, width = input_shape[2], input_shape[3] if len(input_shape) > 3 else input_shape[1:3]
    img = cv2.resize(img, (width, height))
    
    # Convert from BGR to RGB (if using OpenCV)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Transpose to NCHW format if required by the model
    # img = np.transpose(img, (2, 0, 1))
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

# Test inference with the model
try:
    print(f"Preprocessing test image: {test_image_path}")
    input_data = preprocess_image(test_image_path, input_shape)
    
    print("Running inference...")
    start_time = time.time()
    predictions = session.run([output_name], {input_name: input_data})
    end_time = time.time()
    
    inference_time = (end_time - start_time) * 1000  # Convert to ms
    print(f"Inference completed in {inference_time:.2f} ms")
    
    # Process predictions
    output = predictions[0]
    print(f"Output shape: {output.shape}")
    
    # If classification model, get top prediction
    if len(output.shape) == 2:
        class_id = np.argmax(output, axis=1)[0]
        confidence = output[0][class_id]
        print(f"Top prediction - Class ID: {class_id}, Confidence: {confidence:.4f}")
    
    print("Inference test successful!")
    
except Exception as e:
    print(f"Error during inference: {e}") 