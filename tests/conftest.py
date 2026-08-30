from pathlib import Path

import pytest


@pytest.fixture
def sample_docx() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample.docx"
