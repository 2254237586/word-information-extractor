# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-08-30

### Added

- Command-line and Streamlit interfaces for extracting important notices from Word documents.
- Offline rule-based fallback when MacBERT is unavailable.
- Structured JSON and Markdown output with ranking, merging, and source traceability.
- Automated tests, CI, CodeQL, dependency review, Dependabot, and security policy.

### Changed

- Made the PyTorch/Transformers stack optional through `requirements-ml.txt` so the
  core offline workflow remains lightweight and reproducible.
