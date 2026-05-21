import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from ml.lstm_model import LSTMModel
from ml.preprocessor import Preprocessor


class Trainer:
    # we handle all the training logic here, separate from the model definition
    def __init__(self, epochs=50, learning_rate=0.001, batch_size=32):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.model = LSTMModel()
        self.preprocessor = Preprocessor()
        self.model_path = os.path.join("ml", "saved_models", "lstm.pt")

    def train(self, values: list):
        # we need at least 50 data points to train something meaningful
        if len(values) < 50:
            print("[Trainer] not enough data to train, need at least 50 points")
            return
        # we scale the data and create sequences for the LSTM
        scaled = self.preprocessor.fit_transform(values)
        X, y = self.preprocessor.create_sequences(scaled)
        # convert to pytorch tensors:
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y)
        # we wrap the data in a DataLoader so pytorch handles batching for us
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        # Adam optimizer works well for LSTM in most cases:
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()
        print(f"[Trainer] starting training for {self.epochs} epochs...")
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for X_batch, y_batch in loader:
                optimizer.zero_grad()
                output = self.model(X_batch)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            # we log every 10 epochs so we don't spam the console
            if (epoch + 1) % 10 == 0:
                avg_loss = total_loss / len(loader)
                print(f"[Trainer] epoch {epoch + 1}/{self.epochs} - loss: {avg_loss:.6f}")
        # we save the model after training so it persists across restarts
        self.model.save(self.model_path)
        print("[Trainer] training complete")

    def load_existing_model(self):
        # if a saved model exists we load it instead of retraining from scratch
        if os.path.exists(self.model_path):
            self.model.load(self.model_path)
            return True
        return False