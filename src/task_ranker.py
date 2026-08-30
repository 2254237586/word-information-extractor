from typing import Dict, List


def rank_task(task: Dict[str, object]) -> Dict[str, object]:
    score = float(task.get("importance_score", 0)) * 0.55
    score += 0.2 if task.get("deadline") else 0
    score += 0.1 if task.get("time") else 0
    score += 0.08 if any(x in str(task.get("source_text", "")) for x in ("截止", "必须", "务必", "最晚", "考试")) else 0
    score += min(sum(bool(task.get(x)) for x in ("location", "platform", "action", "requirement")) * 0.025, 0.1)
    task["priority_score"] = round(min(score, 1.0), 4)
    task["priority"] = "high" if score >= 0.68 else "medium" if score >= 0.48 else "low"
    return task


def rank_tasks(tasks: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted((rank_task(x) for x in tasks), key=lambda x: float(x["priority_score"]), reverse=True)

