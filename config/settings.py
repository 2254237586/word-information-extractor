from pathlib import Path

try:
    import torch
except ImportError:  # PyTorch is optional for the rule-only runtime.
    torch = None

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
MODEL_DIR = ROOT_DIR / "models" / "important_message_model"
MODEL_NAME = "hfl/chinese-macbert-base"
MAX_LENGTH = 128
IMPORTANCE_THRESHOLD = 0.55
SIMILARITY_THRESHOLD = 0.85
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
EPOCHS = 3
RANDOM_STATE = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") if torch else "cpu"
