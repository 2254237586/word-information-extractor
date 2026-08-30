import re
from typing import Dict, Iterable, List


def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.translate(str.maketrans({",": "，", "!": "！", "?": "？", ";": "；"})).strip()


def split_sentences(paragraphs: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    result: List[Dict[str, object]] = []
    for paragraph in paragraphs:
        original = str(paragraph["text"])
        cleaned = clean_text(original)
        for part in re.split(r"[。！？；\n]+", cleaned):
            text = part.strip(" ，。；：")
            if text:
                result.append({"paragraph_id": paragraph["paragraph_id"],
                               "sentence_id": len(result), "text": text,
                               "original_text": original})
    return result

