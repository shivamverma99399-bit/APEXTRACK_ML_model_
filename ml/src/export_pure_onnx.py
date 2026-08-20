import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch
import numpy as np
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

repo_id = "yuvrajengines/apextrack-track-condition-v2"
print("1. Loading Canonical Model...")
model = AutoModelForImageClassification.from_pretrained(repo_id)
model.eval()

class ViTWrapper(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m
    def forward(self, pixel_values):
        return self.m(pixel_values=pixel_values).logits

wrapped = ViTWrapper(model)
wrapped.eval()

dummy = torch.randn(1, 3, 224, 224)

print("2. Exporting with torch.onnx.export (dynamo=False, opset_version=18)...")
torch.onnx.export(
    wrapped,
    dummy,
    "ml/models/onnx_optimized/model_perfect.onnx",
    input_names=["pixel_values"],
    output_names=["logits"],
    dynamic_axes={"pixel_values": {0: "batch_size"}, "logits": {0: "batch_size"}},
    opset_version=18,
)

print("3. Testing ONNX FP32...")
sess_fp32 = ort.InferenceSession("ml/models/onnx_optimized/model_perfect.onnx", providers=["CPUExecutionProvider"])
with torch.no_grad():
    pt_logits = wrapped(dummy).numpy()

ox_logits = sess_fp32.run(None, {"pixel_values": dummy.numpy()})[0]

print("   PyTorch Logits: ", pt_logits)
print("   ONNX Logits:    ", ox_logits)
diff = np.max(np.abs(pt_logits - ox_logits))
print("   Max Difference: ", diff)

print("4. Quantizing to INT8...")
quantize_dynamic(
    "ml/models/onnx_optimized/model_perfect.onnx",
    "ml/models/onnx_optimized/model_perfect_int8.onnx",
    weight_type=QuantType.QUInt8,
)
sess_int8 = ort.InferenceSession("ml/models/onnx_optimized/model_perfect_int8.onnx", providers=["CPUExecutionProvider"])
ox_int8_logits = sess_int8.run(None, {"pixel_values": dummy.numpy()})[0]
print("   INT8 Logits:    ", ox_int8_logits)

print("ALL ONNX EXPORTS COMPLETED SUCCESSFULLY!")
