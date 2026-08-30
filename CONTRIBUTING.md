# Contributing

1. Create a focused branch from `main`.
2. Install development dependencies with `python -m pip install -r requirements-dev.txt`.
3. Run `ruff check .` and `pytest -q` before opening a pull request.
4. Keep tests offline by default. Tests must not download model weights or require secrets.
5. Do not commit real chat logs, personal information, credentials, or model artifacts.

By contributing, you agree that your contribution is licensed under the MIT License.
