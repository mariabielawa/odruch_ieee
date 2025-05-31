import json
import torch
from torch.utils.data import Dataset, DataLoader

class CheckersDataset(Dataset):
    def __init__(self, json_path):
        with open(json_path, "r") as f:
            self.data = json.load(f)

        self.samples = []
        for item in self.data:
            board = item["board"]
            move = item["move"]

            flat_board = [cell for row in board for cell in row]
            board_tensor = torch.tensor(flat_board, dtype=torch.float32)

            from_row, from_col, to_row, to_col = move
            start = from_row * 8 + from_col
            end = to_row * 8 + to_col
            move_class = start * 64 + end

            self.samples.append((board_tensor, move_class))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]
    
if __name__ == "__main__":
    dataset = CheckersDataset("test_model/jsony/full.json")
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    for batch in loader:
        boards, labels = batch
        print("Board batch shape:", boards.shape)
        print("Move labels:", labels)
        break
