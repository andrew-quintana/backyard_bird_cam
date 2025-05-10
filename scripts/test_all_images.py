import numpy as np
import onnxruntime as ort
import cv2
import time
import os
import glob
from bird_classes import get_bird_name

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
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def main():
    # Path to the ONNX model
    model_path = "common/models/bird_model.onnx"
    
    # Load the ONNX model
    print("Loading ONNX model...")
    try:
        session = ort.InferenceSession(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Get model metadata
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape
    output_name = session.get_outputs()[0].name
    
    print(f"Model details:")
    print(f"- Input name: {input_name}, shape: {input_shape}")
    print(f"- Output name: {output_name}")
    print("-" * 50)
    
    # Get all images from the test_images directory
    test_images = glob.glob("test_images/*.*")
    if not test_images:
        print("No test images found in test_images directory")
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Test each image
    total_time = 0
    successful_inferences = 0
    
    for i, image_path in enumerate(test_images):
        print(f"\nTesting image {i+1}/{len(test_images)}: {os.path.basename(image_path)}")
        
        try:
            # Preprocess image
            input_data = preprocess_image(image_path, input_shape)
            
            # Run inference
            start_time = time.time()
            predictions = session.run([output_name], {input_name: input_data})
            end_time = time.time()
            
            inference_time = (end_time - start_time) * 1000  # Convert to ms
            total_time += inference_time
            successful_inferences += 1
            
            # Process predictions
            output = predictions[0]
            
            print(f"Inference time: {inference_time:.2f} ms")
            print(f"Output shape: {output.shape}")
            
            # If classification model, get top prediction
            if len(output.shape) == 2:
                top_indices = np.argsort(output[0])[-5:][::-1]  # Get top 5 predictions
                print("Top 5 predictions:")
                for idx in top_indices:
                    confidence = output[0][idx]
                    bird_name = get_bird_name(idx)
                    print(f"  {bird_name}: {confidence:.4f}")
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
    
    # Print summary
    if successful_inferences > 0:
        avg_time = total_time / successful_inferences
        print("\n" + "=" * 50)
        print(f"Summary: Successfully ran inference on {successful_inferences}/{len(test_images)} images")
        print(f"Average inference time: {avg_time:.2f} ms")
        print("=" * 50)
    else:
        print("\nNo successful inferences")

if __name__ == "__main__":
    main() 