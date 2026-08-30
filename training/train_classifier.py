import json
import logging
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import settings  # noqa: E402
from training.dataset import ImportantMessageDataset  # noqa: E402
from training.evaluate import trainer_metrics  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    path = settings.DATA_DIR / "sample_train.csv"
    frame = pd.read_csv(path)
    if set(frame.columns) != {"text", "label"} or not set(frame.label.unique()) <= {0, 1}:
        raise ValueError("训练 CSV 必须只包含 text,label 两列，label 只能为 0 或 1")
    train, valid = train_test_split(frame, test_size=0.2, random_state=settings.RANDOM_STATE, stratify=frame.label)
    tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(settings.MODEL_NAME, num_labels=2)
    args = TrainingArguments(output_dir=str(ROOT / "models" / "checkpoints"), num_train_epochs=settings.EPOCHS,
                             per_device_train_batch_size=settings.BATCH_SIZE,
                             per_device_eval_batch_size=settings.BATCH_SIZE,
                             learning_rate=settings.LEARNING_RATE, eval_strategy="epoch", save_strategy="epoch",
                             load_best_model_at_end=True, metric_for_best_model="f1", greater_is_better=True,
                             logging_steps=10, report_to=[])
    trainer = Trainer(model=model, args=args,
                      train_dataset=ImportantMessageDataset(train, tokenizer, settings.MAX_LENGTH),
                      eval_dataset=ImportantMessageDataset(valid, tokenizer, settings.MAX_LENGTH),
                      compute_metrics=trainer_metrics)
    trainer.train()
    metrics = trainer.evaluate()
    settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(settings.MODEL_DIR))
    tokenizer.save_pretrained(str(settings.MODEL_DIR))
    (settings.MODEL_DIR / "evaluation.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Accuracy: {metrics['eval_accuracy']:.4f}\nPrecision: {metrics['eval_precision']:.4f}\nRecall: {metrics['eval_recall']:.4f}\nF1: {metrics['eval_f1']:.4f}")


if __name__ == "__main__":
    main()
