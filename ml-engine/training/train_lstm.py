import torch
import torch.nn as pd
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import os

class LSTMPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(LSTMPredictor, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.fc(out[:, -1, :]) 
        return out

def prepare_data(symbol: str, lookback: int = 30):
    df = yf.Ticker(symbol).history(period="5y")
    data = df[['Close']].values
    
    scaler = MinMaxScaler(feature_range=(-1, 1))
    data_scaled = scaler.fit_transform(data)
    
    x, y = [], []
    for i in range(len(data_scaled) - lookback):
        x.append(data_scaled[i:(i + lookback)])
        y.append(data_scaled[i + lookback])
        
    x = np.array(x)
    y = np.array(y)
    
    # Split
    test_size = int(len(x) * 0.2)
    x_train, y_train = x[:-test_size], y[:-test_size]
    x_test, y_test = x[-test_size:], y[-test_size:]
    
    return torch.FloatTensor(x_train), torch.FloatTensor(y_train), torch.FloatTensor(x_test), torch.FloatTensor(y_test), scaler

def train_lstm(symbol: str):
    print(f"Preparing data for LSTM ({symbol})...")
    lookback = 30
    x_train, y_train, x_test, y_test, scaler = prepare_data(symbol, lookback)
    
    input_dim = 1
    hidden_dim = 32
    num_layers = 2
    output_dim = 1
    num_epochs = 50
    
    model = LSTMPredictor(input_dim, hidden_dim, num_layers, output_dim)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    print(f"Training LSTM model for {symbol}...")
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        out = model(x_train)
        loss = criterion(out, y_train)
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}/{num_epochs}, Loss: {loss.item():.4f}")
            
    # Save the model
    os.makedirs('../models_store', exist_ok=True)
    torch.save(model.state_dict(), f"../models_store/{symbol}_lstm.pth")
    print(f"LSTM model saved to ../models_store/{symbol}_lstm.pth")
    
if __name__ == "__main__":
    for sym in ['AAPL', 'MSFT']:
         train_lstm(sym)
