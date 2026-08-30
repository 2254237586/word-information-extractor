import json
from pathlib import Path
from typing import Dict

LABELS = {"high": "高优先级", "medium": "中优先级", "low": "低优先级"}


def console_text(result: Dict[str, object]) -> str:
    lines = ["========== 重要事项汇总 =========="]
    tasks = result["tasks"]
    for level in ("high", "medium", "low"):
        selected = [x for x in tasks if x["priority"] == level]
        if not selected:
            continue
        lines.extend(["", f"[{LABELS[level]}]"])
        for task in selected:
            lines.append(f"\n{task['id']}. {task['event']}")
            for key, title in (("deadline", "截止时间"), ("time", "时间"), ("location", "地点"),
                               ("platform", "平台"), ("action", "操作")):
                if task.get(key):
                    lines.append(f"   {title}：{task[key]}")
            lines.append(f"   置信度：{float(task['importance_score']):.1%}")
    return "\n".join(lines)


def save_outputs(result: Dict[str, object], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "tasks.json"
    md_path = output_dir / "summary.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# 重要事项汇总", "", f"文档：{result['document']}",
             f"共 {result['total_sentences']} 句，识别重要内容 {result['important_sentences']} 条。"]
    for level in ("high", "medium", "low"):
        selected = [x for x in result["tasks"] if x["priority"] == level]
        if selected:
            lines.extend(["", f"## {LABELS[level]}", ""])
            for task in selected:
                lines.append(f"### {task['id']}. {task['event']}")
                for key, title in (("deadline", "截止"), ("time", "时间"), ("location", "地点"),
                                   ("person", "对象"), ("platform", "平台"), ("action", "操作"),
                                   ("requirement", "要求")):
                    if task.get(key):
                        lines.append(f"- {title}：{task[key]}")
                lines.extend([f"- 置信度：{float(task['importance_score']):.1%}",
                              f"- 来源：第 {task['paragraph_id'] + 1} 段，第 {task['sentence_id'] + 1} 句",
                              f"- 原文：{task['source_text']}", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

