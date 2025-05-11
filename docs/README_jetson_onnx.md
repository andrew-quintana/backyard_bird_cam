# Bird Classification with ONNX on Jetson Nano

This guide explains how to run the bird classification ONNX model on a Jetson Nano.

## Prerequisites

- Jetson Nano with JetPack installed
- Python 3.6+
- Internet connection for package installation

## Setup

1. Make the setup script executable:
   ```bash
   chmod +x scripts/setup_onnx_jetson.sh
   ```

2. Run the setup script to install required dependencies:
   ```bash
   ./scripts/setup_onnx_jetson.sh
   ```

3. Prepare test images:
   ```bash
   # Images should already be in the test_images/ directory
   ls -l test_images/
   ```

4. Update the bird species in the bird class mapping file if needed:
   ```bash
   nano scripts/bird_classes.py
   # Edit the BIRD_CLASSES list to match your model's classes
   ```

## Running Inference

### Testing a Single Image

```bash
python3 scripts/test_onnx_model.py
```

This will:
1. Load the ONNX model
2. Select the first image from your test_images directory
3. Preprocess the image
4. Run inference
5. Display the prediction results and inference time

### Testing All Images

```bash
python3 scripts/test_all_images.py
```

This will:
1. Load the ONNX model
2. Test all images in the test_images directory
3. Show the top 5 predictions for each image
4. Display a summary with average inference time

## Performance Metrics

The test script will output the inference time in milliseconds, which is useful for benchmarking on the Jetson Nano. You should expect:

- CPU inference: ~100-300ms per image
- GPU acceleration with TensorRT: ~10-50ms per image (if properly configured)

## Troubleshooting

### ONNX Runtime Installation Issues

If the standard ONNX Runtime installation fails, try the Jetson-specific version:

```bash
pip3 install --extra-index-url https://jetson-wheel-index.co/onnxruntime-jetson
```

### Memory Issues

If you encounter memory errors:

1. Reduce unnecessary services:
   ```bash
   sudo service lightdm stop  # Stop the desktop environment if not needed
   ```

2. Add swap space if necessary:
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## Performance Optimization

For better performance, consider:

1. Using TensorRT instead of ONNX Runtime
2. Enabling GPU execution with ONNX Runtime
3. Quantizing the model to INT8 precision

### TensorRT Conversion

For even better performance on Jetson Nano, you can convert the ONNX model to TensorRT:

```bash
# Install required packages
sudo apt-get install python3-libnvinfer
pip3 install nvidia-tensorrt

# Create a simple conversion script
cat > convert_to_trt.py << EOL
import tensorrt as trt
import os

def build_engine(onnx_file_path, engine_file_path):
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
    with trt.Builder(TRT_LOGGER) as builder, builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)) as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
        builder.max_batch_size = 1
        config = builder.create_builder_config()
        config.max_workspace_size = 1 << 30  # 1GB
        with open(onnx_file_path, 'rb') as model:
            if not parser.parse(model.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))
                return False
        engine = builder.build_engine(network, config)
        with open(engine_file_path, "wb") as f:
            f.write(engine.serialize())
        return True

build_engine("common/models/bird_model.onnx", "common/models/bird_model.trt")
EOL

# Run the conversion
python3 convert_to_trt.py
``` 