from src.pipeline import ExtractionPipeline


def test_pipeline_offline(sample_docx, tmp_path):
    result = ExtractionPipeline(allow_download=False).run(sample_docx, tmp_path)
    assert result["total_sentences"] > 5
    assert result["important_sentences"] >= 3
    assert (tmp_path / "tasks.json").exists()

