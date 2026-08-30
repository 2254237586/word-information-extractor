import logging
import re
from typing import Dict, List

import numpy as np

try:
    import torch
except ImportError:  # Optional: the rule-only fallback does not need PyTorch.
    torch = None

from config import settings

LOGGER = logging.getLogger(__name__)
ACTION_WORDS = ("提交", "上传", "参加", "报名", "签到", "填写", "下载", "到场", "完成", "修改", "考试", "开会", "上课", "答辩", "领取", "培训", "实验", "答疑")
DEADLINE_WORDS = ("截止", "截至", "之前", "最晚", "务必", "必须")
LOW_WORDS = ("哈哈", "天气不错", "收到", "谢谢", "吃饭", "早上好", "晚安")


class ImportanceClassifier:
    """本地微调分类器优先；否则使用 MacBERT embedding + 可解释规则评分。"""

    def __init__(self, allow_download: bool = True) -> None:
        self.device = settings.DEVICE
        self.tokenizer = self.encoder = self.classifier = None
        self.mode = "rule_only"
        self._load(allow_download)

    def _load(self, allow_download: bool) -> None:
        try:
            if torch is None:
                raise ImportError("PyTorch 未安装")
            from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer
            local = settings.MODEL_DIR
            source = str(local) if local.exists() else settings.MODEL_NAME
            kwargs = {} if allow_download or local.exists() else {"local_files_only": True}
            self.tokenizer = AutoTokenizer.from_pretrained(source, **kwargs)
            if local.exists():
                self.classifier = AutoModelForSequenceClassification.from_pretrained(source).to(self.device).eval()
                self.encoder = self.classifier.base_model
                self.mode = "finetuned"
            else:
                self.encoder = AutoModel.from_pretrained(source, **kwargs).to(self.device).eval()
                self.mode = "macbert_fallback"
            LOGGER.info("模型加载成功：%s，设备：%s", self.mode, self.device)
        except Exception as exc:
            LOGGER.warning("MacBERT 暂不可用，启用纯规则离线降级：%s", exc)

    def extract_embedding(self, text: str) -> np.ndarray:
        if self.encoder is None or self.tokenizer is None:
            # 可重复的字符哈希向量只用于离线去重，绝不伪装成 MacBERT 特征。
            vector = np.zeros(768, dtype=np.float32)
            for char in text:
                vector[ord(char) % 768] += 1
            norm = np.linalg.norm(vector)
            return vector / norm if norm else vector
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=settings.MAX_LENGTH).to(self.device)
        assert torch is not None
        with torch.no_grad():
            output = self.encoder(**inputs)
        return output.last_hidden_state[:, 0, :].cpu().numpy()[0]

    @staticmethod
    def _rule_score(text: str) -> float:
        score = 0.08
        score += min(sum(word in text for word in ACTION_WORDS) * 0.16, 0.32)
        score += min(sum(word in text for word in DEADLINE_WORDS) * 0.18, 0.36)
        score += 0.18 if re.search(r"今天|明天|后天|周[一二三四五六日天]|星期|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2}|[上下晚]午", text) else 0
        score += 0.12 if re.search(r"楼\d+|馆\d*|实验室|线上|腾讯会议", text) else 0
        score -= 0.25 if any(word in text for word in LOW_WORDS) else 0
        return float(np.clip(score, 0.01, 0.99))

    def predict(self, text: str) -> Dict[str, object]:
        if self.classifier is not None and self.tokenizer is not None:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                    max_length=settings.MAX_LENGTH).to(self.device)
            assert torch is not None
            with torch.no_grad():
                probs = torch.softmax(self.classifier(**inputs).logits, dim=-1)[0]
            score = float(probs[1].cpu())
        else:
            score = self._rule_score(text)
        return {"label": int(score >= settings.IMPORTANCE_THRESHOLD),
                "importance_score": round(score, 4), "text": text, "mode": self.mode}

    def predict_batch(self, texts: List[str]) -> List[Dict[str, object]]:
        return [self.predict(text) for text in texts]
