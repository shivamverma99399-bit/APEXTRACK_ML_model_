import json
from pathlib import Path
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModelForImageClassification

def main():
    repo_id = 'yuvrajengines/apextrack-track-condition-v2'
    print("=" * 60)
    print("APEXTRACK V2 — FULL TEST DATASET EVALUATION & ANALYSIS")
    print("=" * 60)

    print("\n1. Loading Model & Processor from Hugging Face Hub...")
    processor = AutoImageProcessor.from_pretrained(repo_id)
    model = AutoModelForImageClassification.from_pretrained(repo_id)
    model.eval()

    print(f"   Model Target:     {repo_id}")
    print(f"   Model id2label:   {model.config.id2label}")
    print(f"   Model label2id:   {model.config.label2id}")
    print(f"   Image Size:       {processor.size}")
    print(f"   Image Mean:       {processor.image_mean}")
    print(f"   Image Std:        {processor.image_std}")

    test_dir = Path("../ml/data/processed/apextrack_balanced/test")
    if not test_dir.exists():
        test_dir = Path("ml/data/processed/apextrack_balanced/test")

    classes = ['damp', 'dry', 'wet']

    print(f"\n2. Evaluating all samples in: {test_dir}")
    y_true = []
    y_pred = []
    all_results = []

    for cls_name in classes:
        cls_folder = test_dir / cls_name
        files = sorted(list(cls_folder.glob("*.jpg")))
        print(f"   - Class '{cls_name}': {len(files)} test images")
        for fpath in files:
            img = Image.open(fpath).convert("RGB")
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = F.softmax(logits, dim=-1).squeeze().tolist()
                pred_idx = int(torch.argmax(logits, dim=-1).item())

            pred_label = model.config.id2label[pred_idx]
            y_true.append(cls_name)
            y_pred.append(pred_label)
            all_results.append({
                "file": fpath.name,
                "true": cls_name,
                "pred": pred_label,
                "logits": [round(float(x), 4) for x in logits.squeeze().tolist()],
                "probs": {model.config.id2label[i]: round(float(probs[i]), 4) for i in range(3)},
            })

    total = len(y_true)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    incorrect = total - correct
    acc = correct / total if total > 0 else 0.0

    # Confusion matrix: rows = true, cols = pred
    cm = {t_cls: {p_cls: 0 for p_cls in classes} for t_cls in classes}
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1

    # Per-class precision, recall, F1
    per_class_metrics = {}
    for c in classes:
        tp = cm[c][c]
        fp = sum(cm[other][c] for other in classes if other != c)
        fn = sum(cm[c][other] for other in classes if other != c)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        support = sum(cm[c].values())
        per_class_metrics[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
            "accuracy": tp / support if support > 0 else 0.0,
        }

    macro_precision = sum(m["precision"] for m in per_class_metrics.values()) / len(classes)
    macro_recall = sum(m["recall"] for m in per_class_metrics.values()) / len(classes)
    macro_f1 = sum(m["f1"] for m in per_class_metrics.values()) / len(classes)

    print("\n" + "=" * 60)
    print("3. OVERALL EVALUATION METRICS")
    print("=" * 60)
    print(f"   Total Samples:    {total}")
    print(f"   Correct:          {correct}")
    print(f"   Incorrect:        {incorrect}")
    print(f"   Overall Accuracy: {acc * 100:.2f}%")
    print(f"   Dry Accuracy:     {per_class_metrics['dry']['accuracy'] * 100:.2f}% ({cm['dry']['dry']}/{per_class_metrics['dry']['support']})")
    print(f"   Damp Accuracy:    {per_class_metrics['damp']['accuracy'] * 100:.2f}% ({cm['damp']['damp']}/{per_class_metrics['damp']['support']})")
    print(f"   Wet Accuracy:     {per_class_metrics['wet']['accuracy'] * 100:.2f}% ({cm['wet']['wet']}/{per_class_metrics['wet']['support']})")
    print(f"   Macro Precision:  {macro_precision:.4f}")
    print(f"   Macro Recall:     {macro_recall:.4f}")
    print(f"   Macro F1:         {macro_f1:.4f}")

    print("\nPer-class Metrics Summary:")
    print(f"   {'Class':<10} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<8}")
    print("   " + "-" * 54)
    for c in classes:
        m = per_class_metrics[c]
        print(f"   {c:<10} {m['precision']:<12.4f} {m['recall']:<12.4f} {m['f1']:<12.4f} {m['support']:<8}")

    print("\nConfusion Matrix (Rows = Ground Truth, Columns = Predicted):")
    print(f"   {'Ground Truth':<15} | {'Pred DAMP':<10} | {'Pred DRY':<10} | {'Pred WET':<10}")
    print("   " + "-" * 55)
    for t_cls in classes:
        print(f"   {t_cls.upper():<15} | {cm[t_cls]['damp']:<10} | {cm[t_cls]['dry']:<10} | {cm[t_cls]['wet']:<10}")

    print("\n" + "=" * 60)
    print("4. TARGET THREE IMAGES ANALYSIS")
    print("=" * 60)
    for target_name in ['dry_0041.jpg', 'damp_0006.jpg', 'wet_0177.jpg']:
        item = next((x for x in all_results if x["file"] == target_name), None)
        if item:
            print(f"\nImage: {item['file']}")
            print(f"   Ground Truth: {item['true'].upper()}")
            print(f"   Prediction:   {item['pred'].upper()}")
            print(f"   Logits:       {item['logits']}")
            print(f"   Softmax:      {item['probs']}")
            print(f"   Confidence:   {max(item['probs'].values()) * 100:.2f}%")

if __name__ == "__main__":
    main()
