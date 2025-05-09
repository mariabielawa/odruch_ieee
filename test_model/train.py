import torch
import torch.nn as nn
import torch.optim as optim
import json
from model import SimpleNet

def load_data(file_path="training_data.json"):
    with open(file_path, "r") as f:
        data = json.load(f)

    inputs = []
    targets = []
    for entry in data:
        flat_board = [cell for row in entry["board"] for cell in row]
        inputs.append(flat_board)
        targets.append(entry["score"])

    X = torch.tensor(inputs, dtype=torch.float32)
    y = torch.tensor(targets, dtype=torch.float32).unsqueeze(1)
    return X, y

def train_model():
    model = SimpleNet()
    X, y = load_data()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    EPOCHS = 50
    for epoch in range(EPOCHS):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), "checkers_model.pth")
    print("Model saved as checkers_model.pth")

if __name__ == "__main__":
    train_model()