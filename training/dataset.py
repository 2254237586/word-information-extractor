from typing import Dict

import pandas as pd
import torch
from torch.utils.data import Dataset


class ImportantMessageDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, tokenizer, max_length: int) -> None:
        self.frame = frame.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        row = self.frame.iloc[index]
        values = self.tokenizer(str(row.text), padding="max_length", truncation=True,
                                max_length=self.max_length, return_tensors="pt")
        return {**{key: value.squeeze(0) for key, value in values.items()},
                "labels": torch.tensor(int(row.label), dtype=torch.long)}

