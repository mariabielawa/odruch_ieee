import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from dataset import CheckersDataset
from model import SimpleNet
import os

dataset = CheckersDataset("test_model/jsony/full.json")
loader = DataLoader(dataset, batch_size=32, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleNet().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 50
for epoch in range(epochs):
    total_loss = 0
    correct = 0
    total = 0

    for boards, labels in loader:
        boards = boards.to(device)
        labels = labels.to(device)

        outputs = model(boards)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == labels).sum().item()
        total += labels.size(0)

    accuracy = 100 * correct / total
    print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss:.4f} | Accuracy: {accuracy:.2f}%")

os.makedirs("test_model/models", exist_ok=True)
torch.save(model.state_dict(), "test_model/models/checkers_model_neural.pth")
print("Model saved to test_model/models/checkers_model_neural.pth")