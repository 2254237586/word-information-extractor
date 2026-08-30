import logging
from pathlib import Path
from typing import Dict

from config import settings
from src.document_reader import read_docx
from src.formatter import save_outputs
from src.importance_classifier import ImportanceClassifier
from src.information_extractor import InformationExtractor
from src.task_merger import merge_tasks
from src.task_ranker import rank_tasks
from src.text_preprocessor import split_sentences

LOGGER = logging.getLogger(__name__)


class ExtractionPipeline:
    def __init__(self, allow_download: bool = True) -> None:
        self.classifier = ImportanceClassifier(allow_download=allow_download)
        self.extractor = InformationExtractor()

    def run(self, file_path: Path, output_dir: Path = settings.OUTPUT_DIR) -> Dict[str, object]:
        LOGGER.info("开始读取文件：%s", file_path)
        paragraphs = read_docx(file_path)
        LOGGER.info("读取段落/表格行数量：%d", len(paragraphs))
        sentences = split_sentences(paragraphs)
        LOGGER.info("分句数量：%d", len(sentences))
        predictions = self.classifier.predict_batch([str(x["text"]) for x in sentences])
        tasks, vectors = [], []
        for sentence, prediction in zip(sentences, predictions):
            if prediction["label"] != 1:
                continue
            extracted = self.extractor.extract(str(sentence["text"]))
            extracted.update({"importance_score": prediction["importance_score"],
                              "classification_mode": prediction["mode"],
                              "source_text": sentence["text"],
                              "paragraph_id": sentence["paragraph_id"],
                              "sentence_id": sentence["sentence_id"]})
            tasks.append(extracted)
            vectors.append(self.classifier.extract_embedding(str(sentence["text"])))
        tasks = rank_tasks(merge_tasks(tasks, vectors))
        for index, task in enumerate(tasks, 1):
            task["id"] = index
        result: Dict[str, object] = {"document": Path(file_path).name,
                                    "total_sentences": len(sentences),
                                    "important_sentences": sum(int(x["label"]) for x in predictions),
                                    "classifier_mode": self.classifier.mode, "tasks": tasks}
        paths = save_outputs(result, output_dir)
        result["output_paths"] = {key: str(path) for key, path in paths.items()}
        LOGGER.info("识别重要信息 %d 条；输出：%s", len(tasks), paths)
        return result

