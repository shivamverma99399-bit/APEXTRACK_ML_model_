import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import os
import gc
import json
import numpy as np
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from huggingface_hub import hf_hub_download, HfApi
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

# Windows memory helper
import ctypes
from ctypes import wintypes, c_size_t, Structure, POINTER, byref, windll

class PROCESS_MEMORY_COUNTERS_EX(Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('PageFaultCount', wintypes.DWORD),
        ('PeakWorkingSetSize', c_size_t),
        ('WorkingSetSize', c_size_t),
        ('QuotaPeakPagedPoolUsage', c_size_t),
        ('QuotaPagedPoolUsage', c_size_t),
        ('QuotaPeakNonPagedPoolUsage', c_size_t),
        ('QuotaNonPagedPoolUsage', c_size_t),
        ('PagefileUsage', c_size_t),
        ('PeakPagefileUsage', c_size_t),
        ('PrivateUsage', c_size_t),
    ]

GetProcessMemoryInfo = windll.psapi.GetProcessMemoryInfo
GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, POINTER(PROCESS_MEMORY_COUNTERS_EX), wintypes.DWORD]
GetProcessMemoryInfo.restype = wintypes.BOOL
GetCurrentProcess = windll.kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE

def get_ram_mb():
    counters = PROCESS_MEMORY_COUNTERS_EX()
    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
    h = GetCurrentProcess()
    res = GetProcessMemoryInfo(h, byref(counters), counters.cb)
    if res:
        return counters.WorkingSetSize / (1024 * 1024), counters.PrivateUsage / (1024 * 1024)
    return 0.0, 0.0

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def main():
    repo_id = "yuvrajengines/apextrack-track-condition-v2"
    dataset_repo = "yuvrajengines/apextrack-track-condition-dataset"
    onnx_dir = Path("ml/models/onnx_optimized")
    onnx_fp32_path = onnx_dir / "model.onnx"
    onnx_int8_path = onnx_dir / "model_quantized.onnx"

    print("=" * 65)
    print("APEXTRACK AI — ONNX INFERENCE BENCHMARK & MEMORY PROFILING")
    print("=" * 65)

    # 1. Baseline PyTorch Model
    print("\n1. Running Baseline PyTorch Evaluation...")
    processor = AutoImageProcessor.from_pretrained(repo_id)
    torch.set_grad_enabled(False)
    torch.set_num_threads(1)
    pt_model = AutoModelForImageClassification.from_pretrained(repo_id, low_cpu_mem_usage=True)
    pt_model.eval()

    id2label = {int(k): v for k, v in pt_model.config.id2label.items()}
    print(f"   Model Target:   {repo_id}")
    print(f"   Class Mapping:  {id2label}")

    api = HfApi()
    all_files = api.list_repo_files(repo_id=dataset_repo, repo_type="dataset")
    test_files = [f for f in all_files if f.startswith("test/")]

    pt_results = []
    for fpath in test_files:
        true_cls = fpath.split("/")[1]
        local_img = hf_hub_download(repo_id=dataset_repo, filename=fpath, repo_type="dataset")
        img = Image.open(local_img).convert("RGB")
        inputs = processor(images=img, return_tensors="pt")
        with torch.inference_mode():
            logits = pt_model(**inputs).logits.squeeze().cpu().numpy()
            probs = softmax(logits)
            pred_idx = int(np.argmax(logits))
            pred_label = id2label[pred_idx]

        pt_results.append({
            "file": Path(fpath).name,
            "true": true_cls,
            "pred": pred_label,
            "logits": logits,
            "probs": {id2label[i]: float(probs[i]) for i in range(3)},
        })

    pt_acc = sum(1 for r in pt_results if r["true"] == r["pred"]) / len(pt_results)
    print(f"   PyTorch Baseline Accuracy: {pt_acc * 100:.2f}% ({sum(1 for r in pt_results if r['true'] == r['pred'])}/{len(pt_results)})")

    # Quantize to INT8
    print("\n2. Quantizing ONNX model to INT8...")
    try:
        quantize_dynamic(
            model_input=str(onnx_fp32_path),
            model_output=str(onnx_int8_path),
            weight_type=QuantType.QUInt8,
        )
        print(f"   INT8 Quantization SUCCESS: {onnx_int8_path.stat().st_size / (1024 * 1024):.2f} MB")
    except Exception as e:
        print(f"   INT8 Quantization Error: {e}")

    # Clean PyTorch from memory
    del pt_model
    gc.collect()

    # Benchmark ONNX Runtime (FP32 & INT8)
    candidates = [("ONNX FP32", onnx_fp32_path)]
    if onnx_int8_path.exists():
        candidates.append(("ONNX INT8 Quantized", onnx_int8_path))

    for name, mpath in candidates:
        print("\n" + "-" * 65)
        print(f"BENCHMARKING: {name} ({mpath.name})")
        print("-" * 65)

        session_opts = ort.SessionOptions()
        session_opts.intra_op_num_threads = 1
        session_opts.inter_op_num_threads = 1
        session = ort.InferenceSession(str(mpath), session_opts, providers=["CPUExecutionProvider"])

        ox_results = []
        for fpath in test_files:
            true_cls = fpath.split("/")[1]
            local_img = hf_hub_download(repo_id=dataset_repo, filename=fpath, repo_type="dataset")
            img = Image.open(local_img).convert("RGB")
            processed = processor(images=img, return_tensors="np")
            pixel_values = processed["pixel_values"].astype(np.float32)

            outputs = session.run(None, {"pixel_values": pixel_values})
            logits = outputs[0][0]
            probs = softmax(logits)
            pred_idx = int(np.argmax(logits))
            pred_label = id2label[pred_idx]

            ox_results.append({
                "file": Path(fpath).name,
                "true": true_cls,
                "pred": pred_label,
                "logits": logits,
                "probs": {id2label[i]: float(probs[i]) for i in range(3)},
            })

        acc = sum(1 for r in ox_results if r["true"] == r["pred"]) / len(ox_results)
        agreement = sum(1 for pt, ox in zip(pt_results, ox_results) if pt["pred"] == ox["pred"]) / len(pt_results)

        print(f"   Model Size:           {mpath.stat().st_size / (1024*1024):.2f} MB")
        print(f"   Accuracy:             {acc * 100:.2f}% ({sum(1 for r in ox_results if r['true'] == r['pred'])}/{len(ox_results)})")
        print(f"   Prediction Agreement: {agreement * 100:.2f}% ({sum(1 for pt, ox in zip(pt_results, ox_results) if pt['pred'] == ox['pred'])}/{len(pt_results)})")

        for cls in ["dry", "damp", "wet"]:
            cls_pt = [r for r in pt_results if r["true"] == cls]
            cls_ox = [r for r in ox_results if r["true"] == cls]
            acc_pt = sum(1 for r in cls_pt if r["true"] == r["pred"]) / len(cls_pt)
            acc_ox = sum(1 for r in cls_ox if r["true"] == r["pred"]) / len(cls_ox)
            print(f"     * {cls.upper():<5} Accuracy: PyTorch={acc_pt*100:.1f}%, {name}={acc_ox*100:.1f}%")

if __name__ == "__main__":
    main()
