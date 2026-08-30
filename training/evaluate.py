from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def classification_metrics(labels: np.ndarray, predictions: np.ndarray) -> Dict[str, float]:
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary", zero_division=0)
    return {"accuracy": accuracy_score(labels, predictions), "precision": precision,
            "recall": recall, "f1": f1}


def trainer_metrics(eval_prediction) -> Dict[str, float]:
    logits, labels = eval_prediction
    return classification_metrics(labels, np.argmax(logits, axis=-1))

