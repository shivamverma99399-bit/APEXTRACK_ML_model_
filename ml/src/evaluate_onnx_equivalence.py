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

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def main():
    repo_id = "yuvrajengines/apextrack-track-condition-v2"
    dataset_repo = "yuvrajengines/apextrack-track-condition-dataset"
    onnx_fp32 = Path("ml/models/onnx_optimized/model_direct.onnx")
    onnx_int8 = Path("ml/models/onnx_optimized/model_direct_int8.onnx")

    print("=" * 65)
    print("APEXTRACK AI — COMPREHENSIVE EQUIVALENCE & ACCURACY BENCHMARK")
    print("=" * 65)

    processor = AutoImageProcessor.from_pretrained(repo_id)
    id2label = {0: "damp", 1: "dry", 2: "wet"}
    classes = ["damp", "dry", "wet"]

    api = HfApi()
    all_files = api.list_repo_files(repo_id=dataset_repo, repo_type="dataset")
    test_files = [f for f in all_files if f.startswith("test/")]

    # Pre-download all 32 test images
    test_samples = []
    for fpath in test_files:
        true_cls = fpath.split("/")[1]
        local_p = hf_hub_download(repo_id=dataset_repo, filename=fpath, repo_type="dataset")
        img = Image.open(local_p).convert("RGB")
        test_samples.append({
            "filename": Path(fpath).name,
            "true_cls": true_cls,
            "image": img,
        })

    # 1. PyTorch Baseline
    print("\n1. Running PyTorch Baseline Inference...")
    torch.set_grad_enabled(False)
    torch.set_num_threads(1)
    pt_model = AutoModelForImageClassification.from_pretrained(repo_id, low_cpu_mem_usage=True)
    pt_model.eval()

    pt_preds = []
    for s in test_samples:
        inputs = processor(images=s["image"], return_tensors="pt")
        with torch.inference_mode():
            logits = pt_model(**inputs).logits.squeeze().cpu().numpy()
            probs = softmax(logits)
            pred_idx = int(np.argmax(logits))
            pred_label = id2label[pred_idx]
        pt_preds.append({
            "file": s["filename"],
            "true": s["true_cls"],
            "pred": pred_label,
            "probs": {id2label[i]: float(probs[i]) for i in range(3)},
            "logits": logits,
        })

    del pt_model
    gc.collect()

    # 2. ONNX FP32
    print("\n2. Running ONNX FP32 Inference...")
    sess_fp32 = ort.InferenceSession(str(onnx_fp32), providers=["CPUExecutionProvider"])
    fp32_preds = []
    for s in test_samples:
        proc = processor(images=s["image"], return_tensors="np")
        pix = proc["pixel_values"].astype(np.float32)
        logits = sess_fp32.run(None, {"pixel_values": pix})[0][0]
        probs = softmax(logits)
        pred_idx = int(np.argmax(logits))
        pred_label = id2label[pred_idx]
        fp32_preds.append({
            "file": s["filename"],
            "true": s["true_cls"],
            "pred": pred_label,
            "probs": {id2label[i]: float(probs[i]) for i in range(3)},
            "logits": logits,
        })

    del sess_fp32
    gc.collect()

    # 3. ONNX INT8
    print("\n3. Running ONNX INT8 Quantized Inference...")
    sess_int8 = ort.InferenceSession(str(onnx_int8), providers=["CPUExecutionProvider"])
    int8_preds = []
    for s in test_samples:
        proc = processor(images=s["image"], return_tensors="np")
        pix = proc["pixel_values"].astype(np.float32)
        logits = sess_int8.run(None, {"pixel_values": pix})[0][0]
        probs = softmax(logits)
        pred_idx = int(np.argmax(logits))
        pred_label = id2label[pred_idx]
        int8_preds.append({
            "file": s["filename"],
            "true": s["true_cls"],
            "pred": pred_label,
            "probs": {id2label[i]: float(probs[i]) for i in range(3)},
            "logits": logits,
        })

    del sess_int8
    gc.collect()

    # ----------------------------------------------------
    # METRICS COMPARISON
    # ----------------------------------------------------
    print("\n" + "=" * 65)
    print("METRICS & PREDICTION EQUIVALENCE REPORT")
    print("=" * 65)

    def calc_metrics(preds, baseline=None):
        total = len(preds)
        correct = sum(1 for r in preds if r["true"] == r["pred"])
        acc = correct / total
        agreement = sum(1 for p, b in zip(preds, baseline if baseline else preds) if p["pred"] == b["pred"]) / total

        per_class = {}
        for c in classes:
            c_samples = [r for r in preds if r["true"] == c]
            c_corr = sum(1 for r in c_samples if r["true"] == r["pred"])
            per_class[c] = c_corr / len(c_samples) if len(c_samples) > 0 else 0.0

        return {
            "accuracy": acc,
            "correct": correct,
            "total": total,
            "agreement": agreement,
            "per_class": per_class,
        }

    m_pt = calc_metrics(pt_preds, pt_preds)
    m_fp32 = calc_metrics(fp32_preds, pt_preds)
    m_int8 = calc_metrics(int8_preds, pt_preds)

    print(f"{'Metric':<25} {'PyTorch Baseline':<18} {'ONNX FP32':<18} {'ONNX INT8'}")
    print("-" * 65)
    print(f"{'Accuracy':<25} {m_pt['accuracy']*100:>6.2f}%            {m_fp32['accuracy']*100:>6.2f}%            {m_int8['accuracy']*100:>6.2f}%")
    print(f"{'Prediction Agreement':<25} {'100.00%':<18} {m_fp32['agreement']*100:>6.2f}%            {m_int8['agreement']*100:>6.2f}%")
    print(f"{'Dry Accuracy':<25} {m_pt['per_class']['dry']*100:>6.2f}%            {m_fp32['per_class']['dry']*100:>6.2f}%            {m_int8['per_class']['dry']*100:>6.2f}%")
    print(f"{'Damp Accuracy':<25} {m_pt['per_class']['damp']*100:>6.2f}%            {m_fp32['per_class']['damp']*100:>6.2f}%            {m_int8['per_class']['damp']*100:>6.2f}%")
    print(f"{'Wet Accuracy':<25} {m_pt['per_class']['wet']*100:>6.2f}%            {m_fp32['per_class']['wet']*100:>6.2f}%            {m_int8['per_class']['wet']*100:>6.2f}%")
    print(f"{'Model File Size':<25} {'~343 MB':<18} {onnx_fp32.stat().st_size/(1024*1024):>6.2f} MB          {onnx_int8.stat().st_size/(1024*1024):>6.2f} MB")

    print("\nTarget 3 Test Images Comparison:")
    for target_name in ["dry_0041.jpg", "damp_0006.jpg", "wet_0177.jpg"]:
        pt_item = next(x for x in pt_preds if x["file"] == target_name)
        fp32_item = next(x for x in fp32_preds if x["file"] == target_name)
        int8_item = next(x for x in int8_preds if x["file"] == target_name)
        print(f"\n  Image: {target_name} (Ground Truth: {pt_item['true'].upper()})")
        print(f"    PyTorch:   Pred={pt_item['pred'].upper():<4} | Damp={pt_item['probs']['damp']*100:.1f}%, Dry={pt_item['probs']['dry']*100:.1f}%, Wet={pt_item['probs']['wet']*100:.1f}%")
        print(f"    ONNX FP32: Pred={fp32_item['pred'].upper():<4} | Damp={fp32_item['probs']['damp']*100:.1f}%, Dry={fp32_item['probs']['dry']*100:.1f}%, Wet={fp32_item['probs']['wet']*100:.1f}%")
        print(f"    ONNX INT8: Pred={int8_item['pred'].upper():<4} | Damp={int8_item['probs']['damp']*100:.1f}%, Dry={int8_item['probs']['dry']*100:.1f}%, Wet={int8_item['probs']['wet']*100:.1f}%")

if __name__ == "__main__":
    main()
