# convert_keras_to_onnx.py
from tensorflow import keras
import tf2onnx

model = keras.models.load_model("common/models/bird_mobilenet_v5data.keras")
spec = (tf2onnx.tf_loader.from_keras(model), {"opset": 13})
model_proto, _ = tf2onnx.convert.from_keras(model, opset=13, output_path="common/models/bird_mobilenet_v5data.onnx")