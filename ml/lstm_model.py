import torch
import torch.nn as nn


class LSTMModel(nn.Module):
    # here is where we define the LSTM architecture
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        # we store these arguments so we can use them in the forward pass:
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        # the main lstm layer:
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True, # we want (batch, sequence, features)
            dropout=0.2, # we drop 20% of neurons, so that we avoid overfitting
        )
        # adding a fully connected layer to get from hidden_size to a single output value:
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # we initialize hidden state and cell state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        # we pass the input through the lstm:
        out, _ = self.lstm(x, (h0, c0))
        # then, we only take into consideration the last output in the sequence
        out = self.fc(out[:, -1, :])
        return out

    def save(self, path: str):
        # saving the model weights to disk
        torch.save(self.state_dict(), path)
        print(f"[LSTMModel] model saved to {path}")

    def load(self, path: str):
        # we load the weights back: for when the server restarts
        self.load_state_dict(torch.load(path, weights_only=True))
        self.eval()
        print(f"[LSTMModel] model loaded from {path}")