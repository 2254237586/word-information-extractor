from typing import Dict, List

import numpy as np

from config import settings


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0


def merge_tasks(tasks: List[Dict[str, object]], embeddings: List[np.ndarray]) -> List[Dict[str, object]]:
    merged: List[Dict[str, object]] = []
    merged_vectors: List[np.ndarray] = []
    for task, vector in zip(tasks, embeddings):
        target = next((i for i, old in enumerate(merged) if
                       (task.get("event") == old.get("event") or _cosine(vector, merged_vectors[i]) >= settings.SIMILARITY_THRESHOLD)), None)
        if target is None:
            task["sources"] = [{"paragraph_id": task["paragraph_id"], "sentence_id": task["sentence_id"], "source_text": task["source_text"]}]
            merged.append(task)
            merged_vectors.append(vector)
        else:
            old = merged[target]
            old["sources"].append({"paragraph_id": task["paragraph_id"], "sentence_id": task["sentence_id"], "source_text": task["source_text"]})
            for key in ("time", "deadline", "location", "person", "platform", "action", "requirement"):
                if not old.get(key) and task.get(key):
                    old[key] = task[key]
            old["importance_score"] = max(float(old["importance_score"]), float(task["importance_score"]))
    return merged
